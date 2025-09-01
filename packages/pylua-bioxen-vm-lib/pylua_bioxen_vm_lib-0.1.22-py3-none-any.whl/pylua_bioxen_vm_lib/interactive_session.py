"""
InteractiveSession: Persistent interactive Lua VM session with PTY and threading support.
SessionManager: Tracks and manages multiple InteractiveSession instances for VMManager integration.
"""
import os
import pty
import threading
import queue
import subprocess
import select
from typing import Dict, List, Optional, Any
import time
import signal
from typing import Dict, Optional, Callable
from pylua_bioxen_vm_lib.exceptions import InteractiveSessionError, SessionNotFoundError, SessionAlreadyExistsError
from pylua_bioxen_vm_lib.logger import VMLogger


class InteractiveSession:
    """
    Manages a persistent interactive Lua interpreter process using PTY.
    Provides bidirectional I/O, real-time output streaming, attach/detach, and command execution.
    """
    def __init__(self, session_id: str, vm_instance, lua_executable: str = "lua", debug_mode: bool = False):
        self.session_id = session_id
        self.vm_instance = vm_instance
        self.lua_executable = lua_executable
        self.debug_mode = debug_mode
        self.logger = VMLogger(debug_mode=debug_mode, component="InteractiveSession")
        self.name = f"InteractiveSession_{session_id}"
        self.process = None
        self.master_fd = None
        self.slave_fd = None
        self.output_queue = queue.Queue()
        self._output_thread = None
        self._running = False
        self._attached = False
        self._lock = threading.RLock()
        self._output_callback = None
        self._last_activity = time.time()
        self._command_output_buffer = []
        self._waiting_for_command = False

    def start(self):
        if self._running:
            raise InteractiveSessionError("Session already running")
        try:
            self.master_fd, self.slave_fd = pty.openpty()
            self.process = subprocess.Popen(
                [self.lua_executable, "-i"],
                stdin=self.slave_fd,
                stdout=self.slave_fd,
                stderr=self.slave_fd,
                bufsize=0,
                close_fds=True,
                preexec_fn=os.setsid
            )
            self._running = True
            self._last_activity = time.time()
            self._output_thread = threading.Thread(target=self._read_output, daemon=True)
            self._output_thread.start()
            time.sleep(0.1)
            self.logger.debug(f"Session {self.session_id} started successfully")
        except Exception as e:
            self._cleanup_resources()
            raise InteractiveSessionError(f"Failed to start session: {e}")

    def _read_output(self):
        self._banner_filtered = False
        while self._running:
            try:
                rlist, _, _ = select.select([self.master_fd], [], [], 0.1)
                if self.master_fd in rlist:
                    data = os.read(self.master_fd, 1024)
                    if data:
                        output = data.decode(errors="replace")
                        self.logger.debug(f"PTY output: {output!r}")
                        # Filter out Lua banner/version info on first output
                        if not self._banner_filtered:
                            if output.strip().startswith('Lua '):
                                self._banner_filtered = True
                                continue  # skip banner
                            self._banner_filtered = True
                        self._last_activity = time.time()
                        self.output_queue.put(output)
                        if self._waiting_for_command:
                            self._command_output_buffer.append(output)
                        if self._attached and self._output_callback:
                            try:
                                self._output_callback(output)
                            except Exception:
                                pass
                    else:
                        break
            except OSError:
                break
            time.sleep(0.01)

    def attach(self, output_callback: Optional[Callable[[str], None]] = None):
        with self._lock:
            self._attached = True
            self._output_callback = output_callback
            self.logger.debug(f"Session {self.session_id} attached")

    def detach(self):
        with self._lock:
            if not self._attached:
                raise DetachError("Session is not currently attached")
            self._attached = False
            self._output_callback = None
            self.logger.debug(f"Session {self.session_id} detached")

    def is_attached(self):
        return self._attached

    def send_command(self, command: str):
        if not self._running:
            raise InteractiveSessionError("Session not running")
        # Buffer multi-line Lua code and send as a block
        if isinstance(command, list):
            command = "\n".join(command)
        if not command.endswith("\n"):
            command += "\n"
        os.write(self.master_fd, command.encode())
        self._last_activity = time.time()
        self.logger.debug(f"Command sent: {command!r}")
        # Force flush: read all available output after sending command
        time.sleep(0.1)
        try:
            while True:
                rlist, _, _ = select.select([self.master_fd], [], [], 0.05)
                if self.master_fd in rlist:
                    data = os.read(self.master_fd, 1024)
                    if data:
                        output = data.decode(errors="replace")
                        self.logger.debug(f"Output after send_command: {output!r}")
                        self.output_queue.put(output)
                    else:
                        break
                else:
                    break
        except Exception as e:
            self.logger.debug(f"Error during flush: {e}")

    def read_output(self, timeout: float = 0.1) -> Optional[str]:
        # Drain all output in the queue and concatenate
        outputs = []
        try:
            while True:
                output = self.output_queue.get(timeout=timeout)
                outputs.append(output)
        except queue.Empty:
            pass
        result = "".join(outputs)
        self.logger.debug(f"Drained output: {result!r}")
        return result if result else None

    def execute_and_wait(self, command: str, timeout: float = 5.0) -> str:
        self._waiting_for_command = True
        self._command_output_buffer = []
        self.send_command(command)
        start_time = time.time()
        while time.time() - start_time < timeout:
            time.sleep(0.05)
            if self._command_output_buffer:
                # Return all output received so far
                output = "".join(self._command_output_buffer)
                self._waiting_for_command = False
                self._command_output_buffer = []
                self.logger.debug(f"Execute and wait returned: {output!r}")
                return output
        self._waiting_for_command = False
        self._command_output_buffer = []
        self.logger.debug("Execute and wait timed out")
        return ""

    def terminate(self):
        self._running = False
        if self.process:
            try:
                os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
            except Exception:
                self.process.terminate()
            self.process.wait(timeout=2)
        self._cleanup_resources()
        self.logger.debug(f"Session {self.session_id} terminated")

    def _cleanup_resources(self):
        if self.master_fd:
            try:
                os.close(self.master_fd)
            except Exception:
                pass
        if self.slave_fd:
            try:
                os.close(self.slave_fd)
            except Exception:
                pass
        self.process = None
        self.master_fd = None
        self.slave_fd = None

    def is_running(self):
        return self._running and self.process and self.process.poll() is None

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.terminate()

class SessionManager:
    """
    Tracks and manages multiple InteractiveSession instances for VMManager integration.
    """
    def __init__(self, debug_mode: bool = False):
        self.debug_mode = debug_mode
        self.logger = VMLogger(debug_mode=debug_mode, component="SessionManager")
        self._sessions: Dict[str, InteractiveSession] = {}
        self._lock = threading.RLock()

    def create_session(self, session_id: str, vm_instance) -> InteractiveSession:
        with self._lock:
            if session_id in self._sessions:
                raise SessionAlreadyExistsError(f"Session '{session_id}' already exists")
            session = InteractiveSession(
                session_id, 
                vm_instance, 
                vm_instance.lua_executable, 
                debug_mode=self.debug_mode
            )
            session.start()
            self._sessions[session_id] = session
            self.logger.debug(f"Created session: {session_id}")
            return session

    def get_session(self, session_id: str) -> Optional[InteractiveSession]:
        with self._lock:
            return self._sessions.get(session_id)

    def remove_session(self, session_id: str) -> None:
        with self._lock:
            session = self._sessions.pop(session_id, None)
            if session:
                session.terminate()
                self.logger.debug(f"Removed session: {session_id}")

    def list_sessions(self) -> Dict[str, Dict[str, Any]]:
        with self._lock:
            return {
                sid: {
                    'attached': session.is_attached(),
                    'running': session.is_running(),
                    'last_activity': session._last_activity
                }
                for sid, session in self._sessions.items()
            }

    def terminate_session(self, session_id: str) -> None:
        """
        Terminate a specific session by its ID.
        """
        with self._lock:
            session = self._sessions.get(session_id)
            if session:
                session.terminate()
                self._sessions.pop(session_id, None)
                self.logger.debug(f"Terminated session: {session_id}")

    def cleanup_all(self):
        with self._lock:
            session_count = len(self._sessions)
            for session in list(self._sessions.values()):
                session.terminate()
            self._sessions.clear()
            self.logger.debug(f"Cleaned up all {session_count} sessions")