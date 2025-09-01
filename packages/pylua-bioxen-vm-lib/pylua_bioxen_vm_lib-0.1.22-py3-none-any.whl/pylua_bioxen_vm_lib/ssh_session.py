"""
SSH Session Manager for persistent interactive connections
Maintains SSH connection state for XCP-ng VM interactive sessions
"""

import paramiko
import threading
import time
import queue
import io
from typing import Optional, Dict, Any

from .exceptions import InteractiveSessionError, VMManagerError


class SSHSessionManager:
    """Manages persistent SSH connection for interactive Lua sessions"""
    
    def __init__(self, host: str, username: str, password: str = None, 
                 key_file: str = None, port: int = 22):
        """Initialize SSH session manager
        
        Args:
            host: SSH host IP address
            username: SSH username
            password: SSH password (if using password auth)
            key_file: Path to SSH private key file (if using key auth)
            port: SSH port (default 22)
        """
        self.host = host
        self.username = username
        self.password = password
        self.key_file = key_file
        self.port = port
        
        # Connection state
        self.client = None
        self.channel = None
        self.connected = False
        self.session_active = False
        
        # Threading for output reading
        self.output_thread = None
        self.output_queue = queue.Queue()
        self.stop_reading = threading.Event()
        
        # Buffers
        self.output_buffer = io.StringIO()
        self.error_buffer = io.StringIO()
        
        # Lock for thread safety
        self.lock = threading.Lock()
    
    def connect(self) -> bool:
        """Establish SSH connection
        
        Returns:
            bool: True if connection successful
            
        Raises:
            InteractiveSessionError: If connection fails
        """
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Connect with appropriate authentication
            if self.password:
                self.client.connect(
                    hostname=self.host,
                    port=self.port,
                    username=self.username,
                    password=self.password,
                    timeout=30
                )
            elif self.key_file:
                self.client.connect(
                    hostname=self.host,
                    port=self.port,
                    username=self.username,
                    key_filename=self.key_file,
                    timeout=30
                )
            else:
                raise InteractiveSessionError("No authentication method provided")
            
            # Create interactive shell channel
            self.channel = self.client.invoke_shell()
            self.channel.settimeout(0.1)  # Non-blocking reads
            
            # Wait for shell prompt
            time.sleep(1)
            self._read_available_output()
            
            self.connected = True
            
            # Start output reading thread
            self._start_output_reader()
            
            return True
            
        except paramiko.AuthenticationException as e:
            raise InteractiveSessionError(f"SSH authentication failed: {e}")
        except paramiko.SSHException as e:
            raise InteractiveSessionError(f"SSH connection failed: {e}")
        except Exception as e:
            raise InteractiveSessionError(f"Failed to establish SSH connection: {e}")
    
    def start_lua_session(self) -> bool:
        """Start interactive Lua interpreter in SSH session
        
        Returns:
            bool: True if Lua session started successfully
            
        Raises:
            InteractiveSessionError: If Lua session fails to start
        """
        if not self.connected:
            raise InteractiveSessionError("SSH connection not established")
        
        try:
            # Clear any existing output
            self._read_available_output()
            
            # Start Lua interpreter
            self.channel.send("lua\n")
            time.sleep(0.5)
            
            # Check for Lua prompt
            output = self._read_available_output()
            
            if ">" in output or "Lua" in output:
                self.session_active = True
                return True
            else:
                raise InteractiveSessionError(f"Failed to start Lua interpreter. Output: {output}")
                
        except Exception as e:
            raise InteractiveSessionError(f"Failed to start Lua session: {e}")
    
    def send_input(self, input_text: str) -> bool:
        """Send input to interactive session
        
        Args:
            input_text: Text to send to Lua interpreter
            
        Returns:
            bool: True if input sent successfully
            
        Raises:
            InteractiveSessionError: If sending input fails
        """
        if not self.session_active:
            raise InteractiveSessionError("No active Lua session")
        
        try:
            with self.lock:
                # Ensure input ends with newline
                if not input_text.endswith('\n'):
                    input_text += '\n'
                
                self.channel.send(input_text)
                return True
                
        except Exception as e:
            raise InteractiveSessionError(f"Failed to send input: {e}")
    
    def read_output(self, timeout: float = 1.0) -> str:
        """Read output from interactive session
        
        Args:
            timeout: Maximum time to wait for output (seconds)
            
        Returns:
            str: Output from Lua interpreter
        """
        if not self.session_active:
            return ""
        
        output_lines = []
        start_time = time.time()
        
        try:
            while time.time() - start_time < timeout:
                try:
                    # Get output from queue with short timeout
                    line = self.output_queue.get(timeout=0.1)
                    output_lines.append(line)
                except queue.Empty:
                    # Check if we have enough output
                    if output_lines and (">" in output_lines[-1] or 
                                       any(line.strip().endswith(">") for line in output_lines)):
                        break
                    continue
            
            # Join all output
            full_output = ''.join(output_lines)
            
            # Clean up Lua prompt artifacts
            full_output = self._clean_lua_output(full_output)
            
            return full_output
            
        except Exception as e:
            raise InteractiveSessionError(f"Failed to read output: {e}")
    
    def execute_command(self, command: str, timeout: float = 5.0) -> str:
        """Execute command and wait for output
        
        Args:
            command: Command to execute
            timeout: Maximum time to wait for output
            
        Returns:
            str: Command output
        """
        if not self.session_active:
            if not self.start_lua_session():
                raise InteractiveSessionError("Failed to start Lua session")
        
        # Send command
        self.send_input(command)
        
        # Wait briefly for execution
        time.sleep(0.1)
        
        # Read output
        return self.read_output(timeout)
    
    def _start_output_reader(self):
        """Start background thread to read output"""
        self.stop_reading.clear()
        self.output_thread = threading.Thread(target=self._output_reader_loop)
        self.output_thread.daemon = True
        self.output_thread.start()
    
    def _output_reader_loop(self):
        """Background loop to continuously read output"""
        while not self.stop_reading.is_set() and self.connected:
            try:
                if self.channel and not self.channel.closed:
                    output = self._read_available_output()
                    if output:
                        self.output_queue.put(output)
                
                time.sleep(0.05)  # Small delay to prevent excessive CPU usage
                
            except Exception:
                # Ignore errors in background thread
                time.sleep(0.1)
    
    def _read_available_output(self) -> str:
        """Read all available output from channel
        
        Returns:
            str: Available output
        """
        if not self.channel:
            return ""
        
        output_data = []
        
        try:
            while self.channel.recv_ready():
                data = self.channel.recv(4096)
                if data:
                    output_data.append(data.decode('utf-8', errors='ignore'))
                else:
                    break
        except:
            pass
        
        return ''.join(output_data)
    
    def _clean_lua_output(self, output: str) -> str:
        """Clean up Lua output by removing prompts and artifacts
        
        Args:
            output: Raw output from Lua interpreter
            
        Returns:
            str: Cleaned output
        """
        lines = output.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Skip empty lines and prompt lines
            if line.strip() and not line.strip() in ['>', '>>', 'lua>', '...']:
                # Remove prompt prefixes
                if line.startswith('> '):
                    line = line[2:]
                elif line.startswith('>> '):
                    line = line[3:]
                
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def is_connected(self) -> bool:
        """Check if SSH connection is active
        
        Returns:
            bool: True if connected
        """
        if not self.connected or not self.client:
            return False
        
        try:
            # Test connection with a simple command
            transport = self.client.get_transport()
            return transport and transport.is_active()
        except:
            return False
    
    def reconnect(self) -> bool:
        """Reconnect SSH session
        
        Returns:
            bool: True if reconnection successful
        """
        try:
            self.disconnect()
            time.sleep(1)
            return self.connect()
        except Exception as e:
            raise InteractiveSessionError(f"Failed to reconnect: {e}")
    
    def disconnect(self):
        """Close SSH connection and cleanup"""
        try:
            # Stop background thread
            if self.output_thread and self.output_thread.is_alive():
                self.stop_reading.set()
                self.output_thread.join(timeout=2)
            
            # Close channel
            if self.channel:
                self.channel.close()
                self.channel = None
            
            # Close SSH client
            if self.client:
                self.client.close()
                self.client = None
            
            self.connected = False
            self.session_active = False
            
        except Exception:
            pass  # Ignore cleanup errors
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()
