"""
Enhanced logging system for pylua_bioxen_vm_lib

Provides unified logging across all components with:
- Integration with curator logging
- Progress tracking for package installations
- Performance metrics and timing
- Installation history for rollback capabilities
- Log file rotation and cleanup
- Component-specific logging with context
"""

import sys
import time
import logging
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from contextlib import contextmanager
from dataclasses import dataclass, asdict
import json


@dataclass
class LogEntry:
    """Structured log entry for advanced logging features"""
    timestamp: str
    level: str
    component: str
    message: str
    context: Dict[str, Any] = None
    duration: Optional[float] = None
    
    def __post_init__(self):
        if self.context is None:
            self.context = {}


@dataclass
class ProgressTracker:
    """Track progress of long-running operations"""
    operation: str
    total_steps: int
    current_step: int = 0
    start_time: float = 0.0
    status: str = "running"  # running, completed, failed
    context: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.context is None:
            self.context = {}
        if self.start_time == 0.0:
            self.start_time = time.time()
    
    @property
    def progress_percentage(self) -> float:
        """Calculate progress percentage"""
        if self.total_steps == 0:
            return 0.0
        return min(100.0, (self.current_step / self.total_steps) * 100.0)
    
    @property
    def elapsed_time(self) -> float:
        """Get elapsed time in seconds"""
        return time.time() - self.start_time
    
    @property
    def estimated_remaining(self) -> float:
        """Estimate remaining time in seconds"""
        if self.current_step == 0:
            return 0.0
        
        elapsed = self.elapsed_time
        rate = self.current_step / elapsed
        remaining_steps = self.total_steps - self.current_step
        
        return remaining_steps / rate if rate > 0 else 0.0


class VMLogger:
    """Enhanced VM logger with curator integration and advanced features"""
    
    _instances: Dict[str, 'VMLogger'] = {}
    _lock = threading.Lock()
    
    def __init__(self, debug_mode: bool = False, component: str = "VM", 
                 log_dir: str = "logs", enable_file_logging: bool = True):
        self.debug_mode = debug_mode
        self.component = component
        self.log_dir = Path(log_dir)
        self.enable_file_logging = enable_file_logging
        
        # Create logs directory
        if self.enable_file_logging:
            self.log_dir.mkdir(exist_ok=True)
        
        # Setup Python logging integration
        self.logger = self._setup_python_logger()
        
        # Progress tracking
        self._progress_trackers: Dict[str, ProgressTracker] = {}
        
        # Performance metrics
        self._performance_metrics: List[Dict[str, Any]] = []
        
        # Installation history for rollback
        self._installation_history: List[Dict[str, Any]] = []
        
        # Load existing history if available
        self._load_history()
    
    @classmethod
    def get_instance(cls, component: str = "VM", **kwargs) -> 'VMLogger':
        """Get or create logger instance for component (singleton per component)"""
        with cls._lock:
            if component not in cls._instances:
                cls._instances[component] = cls(component=component, **kwargs)
            return cls._instances[component]
    
    def _setup_python_logger(self) -> logging.Logger:
        """Setup Python logging integration"""
        logger_name = f"pylua_vm.{self.component.lower()}"
        logger = logging.getLogger(logger_name)
        
        # Avoid duplicate handlers
        if logger.handlers:
            return logger
        
        logger.setLevel(logging.DEBUG if self.debug_mode else logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(logging.INFO)
        
        # File handler if enabled
        if self.enable_file_logging:
            log_file = self.log_dir / f"{self.component.lower()}_{datetime.now().strftime('%Y%m%d')}.log"
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            
            # Detailed formatter for file
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
        
        # Simple formatter for console
        console_formatter = logging.Formatter(
            f'[%(asctime)s][%(levelname)s][{self.component}] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        return logger
    
    def _format_message(self, level: str, message: str, context: Dict[str, Any] = None) -> str:
        """Format message with timestamp and context"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        formatted = f"[{timestamp}][{level}][{self.component}] {message}"
        
        if context:
            context_str = " | ".join(f"{k}={v}" for k, v in context.items())
            formatted += f" | {context_str}"
        
        return formatted
    
    def _log_to_history(self, level: str, message: str, context: Dict[str, Any] = None):
        """Log entry to structured history"""
        if self.enable_file_logging:
            entry = LogEntry(
                timestamp=datetime.now().isoformat(),
                level=level,
                component=self.component,
                message=message,
                context=context or {}
            )
            
            history_file = self.log_dir / f"history_{datetime.now().strftime('%Y%m%d')}.jsonl"
            try:
                with open(history_file, 'a') as f:
                    json.dump(asdict(entry), f, default=str)
                    f.write('\n')
            except Exception as e:
                # Fallback to stderr if history logging fails
                print(f"History logging failed: {e}", file=sys.stderr)
    
    def debug(self, message: str, context: Dict[str, Any] = None):
        """Log debug message"""
        if self.debug_mode:
            formatted = self._format_message("DEBUG", message, context)
            print(formatted, file=sys.stderr)
            self.logger.debug(message)
            self._log_to_history("DEBUG", message, context)
    
    def info(self, message: str, context: Dict[str, Any] = None):
        """Log info message"""
        formatted = self._format_message("INFO", message, context)
        print(formatted, file=sys.stderr)
        self.logger.info(message)
        self._log_to_history("INFO", message, context)
    
    def warning(self, message: str, context: Dict[str, Any] = None):
        """Log warning message"""
        formatted = self._format_message("WARNING", message, context)
        print(formatted, file=sys.stderr)
        self.logger.warning(message)
        self._log_to_history("WARNING", message, context)
    
    def error(self, message: str, context: Dict[str, Any] = None):
        """Log error message"""
        formatted = self._format_message("ERROR", message, context)
        print(formatted, file=sys.stderr)
        self.logger.error(message)
        self._log_to_history("ERROR", message, context)
    
    def success(self, message: str, context: Dict[str, Any] = None):
        """Log success message (special info level)"""
        formatted = self._format_message("SUCCESS", message, context)
        print(formatted, file=sys.stderr)
        self.logger.info(f"SUCCESS: {message}")
        self._log_to_history("SUCCESS", message, context)
    
    @contextmanager
    def timed_operation(self, operation_name: str, context: Dict[str, Any] = None):
        """Context manager for timing operations"""
        start_time = time.time()
        self.info(f"Starting {operation_name}", context)
        
        try:
            yield
            duration = time.time() - start_time
            self.success(f"Completed {operation_name} in {duration:.2f}s", 
                        {**(context or {}), "duration": duration})
            
            # Record performance metric
            self._performance_metrics.append({
                "operation": operation_name,
                "duration": duration,
                "timestamp": datetime.now().isoformat(),
                "component": self.component,
                "context": context or {}
            })
            
        except Exception as e:
            duration = time.time() - start_time
            self.error(f"Failed {operation_name} after {duration:.2f}s: {e}", 
                      {**(context or {}), "duration": duration, "error": str(e)})
            raise
    
    def start_progress(self, operation_id: str, operation_name: str, 
                      total_steps: int, context: Dict[str, Any] = None) -> str:
        """Start tracking progress for a long-running operation"""
        tracker = ProgressTracker(
            operation=operation_name,
            total_steps=total_steps,
            context=context or {}
        )
        
        self._progress_trackers[operation_id] = tracker
        self.info(f"Started {operation_name} (0/{total_steps})", context)
        return operation_id
    
    def update_progress(self, operation_id: str, steps: int = 1, 
                       message: str = None, context: Dict[str, Any] = None):
        """Update progress for a tracked operation"""
        if operation_id not in self._progress_trackers:
            self.warning(f"Unknown progress tracker: {operation_id}")
            return
        
        tracker = self._progress_trackers[operation_id]
        tracker.current_step = min(tracker.current_step + steps, tracker.total_steps)
        
        progress_msg = (f"{tracker.operation}: {tracker.current_step}/{tracker.total_steps} "
                       f"({tracker.progress_percentage:.1f}%)")
        
        if tracker.current_step < tracker.total_steps:
            remaining = tracker.estimated_remaining
            if remaining > 0:
                progress_msg += f" - ETA: {remaining:.1f}s"
        
        if message:
            progress_msg += f" - {message}"
        
        self.info(progress_msg, {
            **(context or {}),
            "progress": tracker.progress_percentage,
            "step": tracker.current_step,
            "total": tracker.total_steps
        })
        
        # Complete if finished
        if tracker.current_step >= tracker.total_steps:
            tracker.status = "completed"
            self.success(f"Completed {tracker.operation} in {tracker.elapsed_time:.2f}s")
    
    def fail_progress(self, operation_id: str, error_message: str = None):
        """Mark a progress tracker as failed"""
        if operation_id not in self._progress_trackers:
            return
        
        tracker = self._progress_trackers[operation_id]
        tracker.status = "failed"
        
        error_msg = f"Failed {tracker.operation} at step {tracker.current_step}/{tracker.total_steps}"
        if error_message:
            error_msg += f": {error_message}"
        
        self.error(error_msg)
    
    def log_installation(self, package_name: str, version: str, success: bool, 
                        duration: float = None, error: str = None, 
                        context: Dict[str, Any] = None):
        """Log package installation for rollback history"""
        install_record = {
            "timestamp": datetime.now().isoformat(),
            "package": package_name,
            "version": version,
            "success": success,
            "duration": duration,
            "error": error,
            "context": context or {},
            "component": self.component
        }
        
        self._installation_history.append(install_record)
        
        # Save to file
        if self.enable_file_logging:
            history_file = self.log_dir / "installation_history.jsonl"
            try:
                with open(history_file, 'a') as f:
                    json.dump(install_record, f, default=str)
                    f.write('\n')
            except Exception as e:
                self.warning(f"Failed to save installation history: {e}")
        
        # Log the installation
        if success:
            msg = f"Installed {package_name} v{version}"
            if duration:
                msg += f" in {duration:.2f}s"
            self.success(msg, context)
        else:
            msg = f"Failed to install {package_name} v{version}"
            if error:
                msg += f": {error}"
            self.error(msg, context)
    
    def get_installation_history(self, package_name: str = None, 
                                days: int = 30) -> List[Dict[str, Any]]:
        """Get installation history for rollback purposes"""
        cutoff = datetime.now() - timedelta(days=days)
        
        history = []
        for record in self._installation_history:
            record_time = datetime.fromisoformat(record["timestamp"])
            if record_time >= cutoff:
                if package_name is None or record["package"] == package_name:
                    history.append(record)
        
        return sorted(history, key=lambda x: x["timestamp"], reverse=True)
    
    def get_performance_metrics(self, operation_name: str = None, 
                               hours: int = 24) -> List[Dict[str, Any]]:
        """Get performance metrics for analysis"""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        metrics = []
        for metric in self._performance_metrics:
            metric_time = datetime.fromisoformat(metric["timestamp"])
            if metric_time >= cutoff:
                if operation_name is None or metric["operation"] == operation_name:
                    metrics.append(metric)
        
        return sorted(metrics, key=lambda x: x["timestamp"], reverse=True)
    
    def cleanup_old_logs(self, days: int = 30):
        """Clean up old log files"""
        if not self.enable_file_logging:
            return
        
        cutoff = datetime.now() - timedelta(days=days)
        cleaned = 0
        
        try:
            for log_file in self.log_dir.glob("*.log"):
                if log_file.stat().st_mtime < cutoff.timestamp():
                    log_file.unlink()
                    cleaned += 1
            
            for log_file in self.log_dir.glob("*.jsonl"):
                if log_file.stat().st_mtime < cutoff.timestamp():
                    log_file.unlink()
                    cleaned += 1
            
            if cleaned > 0:
                self.info(f"Cleaned up {cleaned} old log files")
                
        except Exception as e:
            self.warning(f"Log cleanup failed: {e}")
    
    def _load_history(self):
        """Load existing installation history"""
        if not self.enable_file_logging:
            return
        
        history_file = self.log_dir / "installation_history.jsonl"
        if not history_file.exists():
            return
        
        try:
            with open(history_file, 'r') as f:
                for line in f:
                    if line.strip():
                        record = json.loads(line.strip())
                        self._installation_history.append(record)
        except Exception as e:
            self.warning(f"Failed to load installation history: {e}")
    
    def export_logs(self, output_file: str = None) -> str:
        """Export logs for analysis or sharing"""
        if output_file is None:
            output_file = f"pylua_vm_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        export_data = {
            "metadata": {
                "component": self.component,
                "export_timestamp": datetime.now().isoformat(),
                "debug_mode": self.debug_mode
            },
            "installation_history": self._installation_history,
            "performance_metrics": self._performance_metrics,
            "active_progress_trackers": {
                pid: asdict(tracker) for pid, tracker in self._progress_trackers.items()
            }
        }
        
        try:
            with open(output_file, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            self.success(f"Exported logs to {output_file}")
            return output_file
            
        except Exception as e:
            self.error(f"Failed to export logs: {e}")
            raise


# Convenience functions for backward compatibility and easy access
def get_logger(component: str = "VM", debug_mode: bool = False, **kwargs) -> VMLogger:
    """Get logger instance for component"""
    return VMLogger.get_instance(component=component, debug_mode=debug_mode, **kwargs)


def setup_global_logging(debug_mode: bool = False, log_dir: str = "logs"):
    """Setup logging for all components"""
    components = ["VM", "Curator", "Environment", "Network"]
    loggers = {}
    
    for component in components:
        loggers[component.lower()] = get_logger(
            component=component, 
            debug_mode=debug_mode, 
            log_dir=log_dir
        )
    
    return loggers


# Integration with curator logging
def integrate_with_curator_logger(curator_logger: logging.Logger, 
                                 vm_logger: VMLogger) -> logging.Logger:
    """Integrate curator's Python logger with enhanced VM logger"""
    
    class VMLoggerHandler(logging.Handler):
        """Custom handler to bridge curator logging to VM logger"""
        
        def __init__(self, vm_logger: VMLogger):
            super().__init__()
            self.vm_logger = vm_logger
        
        def emit(self, record):
            # Convert logging levels to VM logger methods
            level_map = {
                logging.DEBUG: self.vm_logger.debug,
                logging.INFO: self.vm_logger.info,
                logging.WARNING: self.vm_logger.warning,
                logging.ERROR: self.vm_logger.error,
                logging.CRITICAL: self.vm_logger.error
            }
            
            log_method = level_map.get(record.levelno, self.vm_logger.info)
            message = self.format(record)
            
            # Extract context from record if available
            context = getattr(record, 'context', None)
            log_method(message, context)
    
    # Add VM logger handler to curator logger
    vm_handler = VMLoggerHandler(vm_logger)
    curator_logger.addHandler(vm_handler)
    
    return curator_logger


if __name__ == "__main__":
    # Demo usage of enhanced logging
    logger = get_logger("DEMO", debug_mode=True)
    
    # Basic logging
    logger.info("Starting demo")
    logger.debug("Debug information", {"user": "demo", "session": "test"})
    
    # Timed operation
    with logger.timed_operation("Demo Operation", {"operation_type": "demo"}):
        time.sleep(1)
    
    # Progress tracking
    op_id = logger.start_progress("demo_install", "Installing Demo Packages", 5)
    for i in range(5):
        time.sleep(0.5)
        logger.update_progress(op_id, 1, f"Step {i+1} completed")
    
    # Installation logging
    logger.log_installation("demo-package", "1.0.0", True, 2.5)
    logger.log_installation("failed-package", "2.0.0", False, 1.0, "Connection timeout")
    
    # Show metrics
    print("\n=== Performance Metrics ===")
    metrics = logger.get_performance_metrics()
    for metric in metrics:
        print(f"- {metric['operation']}: {metric['duration']:.2f}s")
    
    print("\n=== Installation History ===")
    history = logger.get_installation_history()
    for record in history:
        status = "✓" if record["success"] else "✗"
        print(f"{status} {record['package']} v{record['version']}")