"""Logging utilities for the Pan-Omics Consciousness Engine."""

import logging
import sys
from pathlib import Path
from typing import Optional, Union, Dict, Any
from datetime import datetime
import json

from rich.logging import RichHandler
from rich.console import Console
from rich.traceback import install

# Install rich traceback handler
install()


class PCEFormatter(logging.Formatter):
    """Custom formatter for PCE logs."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record."""
        # Add timestamp
        record.timestamp = datetime.fromtimestamp(record.created).isoformat()
        
        # Add module path
        if hasattr(record, 'pathname'):
            record.module_path = Path(record.pathname).relative_to(Path.cwd()).as_posix()
        else:
            record.module_path = record.name
        
        return super().format(record)


class StructuredHandler(logging.Handler):
    """Handler that outputs structured JSON logs."""
    
    def __init__(self, stream: Optional[Any] = None) -> None:
        super().__init__()
        self.stream = stream or sys.stdout
    
    def emit(self, record: logging.LogRecord) -> None:
        """Emit a log record as structured JSON."""
        try:
            log_entry = {
                'timestamp': datetime.fromtimestamp(record.created).isoformat(),
                'level': record.levelname,
                'logger': record.name,
                'module': getattr(record, 'module', record.name),
                'function': record.funcName,
                'line': record.lineno,
                'message': record.getMessage(),
            }
            
            # Add exception info if present
            if record.exc_info:
                log_entry['exception'] = self.format(record)
            
            # Add extra fields
            for key, value in record.__dict__.items():
                if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 
                             'pathname', 'filename', 'module', 'exc_info',
                             'exc_text', 'stack_info', 'lineno', 'funcName',
                             'created', 'msecs', 'relativeCreated', 'thread',
                             'threadName', 'processName', 'process', 'getMessage']:
                    if not key.startswith('_'):
                        log_entry[key] = value
            
            json.dump(log_entry, self.stream)
            self.stream.write('\n')
            self.stream.flush()
            
        except Exception:
            self.handleError(record)


def setup_logging(
    level: str = "INFO",
    log_file: Optional[Union[str, Path]] = None,
    structured: bool = False,
    rich_console: bool = True
) -> None:
    """Setup logging configuration for PCE.
    
    Args:
        level: Logging level
        log_file: Optional log file path
        structured: Whether to use structured JSON logging
        rich_console: Whether to use Rich console output
    """
    # Clear existing handlers
    logging.getLogger().handlers.clear()
    
    # Set root logger level
    logging.getLogger().setLevel(level.upper())
    
    # Create formatters
    if structured:
        formatter = None  # StructuredHandler handles its own formatting
    else:
        formatter = PCEFormatter(
            '%(timestamp)s | %(levelname)-8s | %(module_path)s:%(lineno)d | %(message)s'
        )
    
    # Setup console handler
    if rich_console and not structured:
        console_handler = RichHandler(
            console=Console(stderr=True),
            show_path=True,
            show_time=True,
            rich_tracebacks=True,
            tracebacks_suppress=[
                # Suppress some common library tracebacks
                "torch",
                "numpy",
                "pandas",
                "sklearn",
            ]
        )
        console_handler.setFormatter(formatter)
    elif structured:
        console_handler = StructuredHandler(sys.stderr)
    else:
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setFormatter(formatter)
    
    logging.getLogger().addHandler(console_handler)
    
    # Setup file handler if specified
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        if structured:
            file_handler = StructuredHandler(open(log_path, 'a'))
        else:
            file_handler = logging.FileHandler(log_path)
            file_handler.setFormatter(formatter)
        
        logging.getLogger().addHandler(file_handler)
    
    # Set library log levels to reduce noise
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("matplotlib").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.WARNING)
    
    # PCE-specific logger
    pce_logger = logging.getLogger("pce")
    pce_logger.info("PCE logging initialized")


def get_logger(name: str, **extra_fields: Any) -> logging.LoggerAdapter:
    """Get a logger with extra context fields.
    
    Args:
        name: Logger name
        **extra_fields: Extra fields to include in log messages
        
    Returns:
        Logger adapter with extra fields
    """
    logger = logging.getLogger(name)
    return logging.LoggerAdapter(logger, extra_fields)


class PerformanceLogger:
    """Logger for performance monitoring."""
    
    def __init__(self, logger: logging.Logger) -> None:
        self.logger = logger
        self.timers: Dict[str, datetime] = {}
    
    def start_timer(self, name: str) -> None:
        """Start a named timer."""
        self.timers[name] = datetime.now()
        self.logger.debug(f"Started timer: {name}")
    
    def end_timer(self, name: str, log_level: int = logging.INFO) -> float:
        """End a named timer and log duration."""
        if name not in self.timers:
            self.logger.warning(f"Timer {name} was not started")
            return 0.0
        
        start_time = self.timers.pop(name)
        duration = (datetime.now() - start_time).total_seconds()
        
        self.logger.log(log_level, f"Timer {name}: {duration:.3f}s")
        return duration
    
    def log_memory_usage(self) -> None:
        """Log current memory usage."""
        try:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            memory_mb = process.memory_info().rss / 1024 / 1024
            self.logger.info(f"Memory usage: {memory_mb:.1f} MB")
            
        except ImportError:
            self.logger.debug("psutil not available for memory monitoring")
    
    def log_gpu_usage(self) -> None:
        """Log GPU memory usage."""
        try:
            import torch
            if torch.cuda.is_available():
                for i in range(torch.cuda.device_count()):
                    allocated = torch.cuda.memory_allocated(i) / 1024**2
                    cached = torch.cuda.memory_reserved(i) / 1024**2
                    self.logger.info(
                        f"GPU {i}: {allocated:.1f} MB allocated, {cached:.1f} MB cached"
                    )
        except ImportError:
            pass


# Context manager for performance timing
class timer_context:
    """Context manager for timing operations."""
    
    def __init__(self, name: str, logger: Optional[logging.Logger] = None) -> None:
        self.name = name
        self.logger = logger or logging.getLogger(__name__)
        self.start_time: Optional[datetime] = None
    
    def __enter__(self) -> 'timer_context':
        self.start_time = datetime.now()
        self.logger.debug(f"Starting: {self.name}")
        return self
    
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if self.start_time:
            duration = (datetime.now() - self.start_time).total_seconds()
            if exc_type is None:
                self.logger.info(f"Completed {self.name}: {duration:.3f}s")
            else:
                self.logger.error(f"Failed {self.name} after {duration:.3f}s: {exc_val}")


# Audit logging for security and compliance
class AuditLogger:
    """Specialized logger for audit events."""
    
    def __init__(self, name: str = "pce.audit") -> None:
        self.logger = logging.getLogger(name)
        
        # Ensure audit logs always use structured format
        if not any(isinstance(h, StructuredHandler) for h in self.logger.handlers):
            audit_handler = StructuredHandler()
            self.logger.addHandler(audit_handler)
            self.logger.setLevel(logging.INFO)
    
    def log_data_access(
        self,
        user: str,
        dataset: str,
        action: str,
        success: bool = True,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log data access event."""
        self.logger.info(
            "Data access event",
            extra={
                "event_type": "data_access",
                "user": user,
                "dataset": dataset,
                "action": action,
                "success": success,
                "details": details or {}
            }
        )
    
    def log_model_operation(
        self,
        user: str,
        model: str,
        operation: str,
        success: bool = True,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log model operation event."""
        self.logger.info(
            "Model operation event",
            extra={
                "event_type": "model_operation",
                "user": user,
                "model": model,
                "operation": operation,
                "success": success,
                "details": details or {}
            }
        )
    
    def log_security_event(
        self,
        event: str,
        severity: str = "info",
        user: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log security event."""
        log_level = getattr(logging, severity.upper(), logging.INFO)
        self.logger.log(
            log_level,
            f"Security event: {event}",
            extra={
                "event_type": "security",
                "severity": severity,
                "user": user,
                "details": details or {}
            }
        )
