"""
Urbalurba Structured Logger - Python Implementation
Filename: urblogger.py

★ REDESIGNED TO MATCH TYPESCRIPT WINSTON → OPENTELEMETRY ARCHITECTURE ★

This implementation creates a custom structlog processor that sends logs to OpenTelemetry,
mirroring the TypeScript Winston transport approach. This ensures identical behavior:
- structlog → OpenTelemetry → OTLP (logs + traces)
- Multiple simultaneous transports (console + file + OTLP)
- Full OpenTelemetry SDK configuration
- Graceful shutdown with flush functionality

Implements "Loggeloven av 2025" requirements with the new standardized API
that is consistent across all programming languages (TypeScript, C#, PHP, Python).

Features:
- Structured JSON logging with required fields  
- Full OpenTelemetry integration (traces AND logs)
- Custom structlog processor for OTLP export
- Security-aware error handling (removes auth credentials)
- Consistent field naming (camelCase)
- Azure Monitor compatible output
- Simple function-based API identical across languages
- Multiple simultaneous transports
- Graceful shutdown with flush functionality
"""

import json
import uuid
import traceback
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional, Union
import structlog
import logging
import os
from logging.handlers import RotatingFileHandler

# OpenTelemetry imports for full SDK configuration
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.trace import set_tracer_provider
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor
# Try to import semantic conventions, use fallback if not available
try:
    from opentelemetry.semantic_conventions.resource import ResourceAttributes
except ImportError:
    # Fallback - define the constants manually
    class ResourceAttributes:
        SERVICE_NAME = "service.name"
        SERVICE_VERSION = "service.version"
        DEPLOYMENT_ENVIRONMENT = "deployment.environment"

# OpenTelemetry log imports - use available modules
try:
    from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
    from opentelemetry.sdk._logs import LoggerProvider
    from opentelemetry.sdk._logs._internal.export import BatchLogRecordProcessor
    from opentelemetry._logs import set_logger_provider, get_logger
    from opentelemetry._logs._internal import LogRecord
    from opentelemetry._logs.severity import SeverityNumber
    import time
    LOGS_AVAILABLE = True
except ImportError:
    # Logs SDK not available in this version, fallback to trace-only
    LOGS_AVAILABLE = False
    print("⚠️  OpenTelemetry logs SDK not available, using trace context only")

# For auto-instrumentation, we'll use a simpler approach
try:
    from opentelemetry.instrumentation.auto_instrumentation import autoinstrument
except ImportError:
    try:
        from opentelemetry.auto_instrumentation import autoinstrument
    except ImportError:
        # Fallback if auto-instrumentation is not available
        def autoinstrument():
            pass

# Import log levels from separate module
from .log_levels import LOGLEVELS

# =============================================================================
# GLOBAL OPENTELEMETRY CONFIGURATION
# =============================================================================

# Global OpenTelemetry providers - initialized once per application
_global_tracer_provider: Optional[TracerProvider] = None
_global_logger_provider: Optional[Any] = None  # LoggerProvider if logs available

def _configure_opentelemetry_sdk(system_id: str) -> None:
    """Configure OpenTelemetry SDK with traces and logs (if available) - matching TypeScript architecture"""
    global _global_tracer_provider, _global_logger_provider
    
    try:
        # Create resource with semantic conventions
        resource = Resource.create({
            ResourceAttributes.SERVICE_NAME: system_id,
            ResourceAttributes.SERVICE_VERSION: "1.0.0",
            ResourceAttributes.DEPLOYMENT_ENVIRONMENT: os.getenv('OTEL_ENVIRONMENT', 'development')
        })
        
        # Configure Trace Provider
        _global_tracer_provider = TracerProvider(resource=resource)
        set_tracer_provider(_global_tracer_provider)
        
        # Configure trace exporter if endpoint is provided
        trace_endpoint = os.getenv('OTEL_EXPORTER_OTLP_TRACES_ENDPOINT')
        if trace_endpoint:
            trace_exporter = OTLPSpanExporter(endpoint=trace_endpoint)
            span_processor = BatchSpanProcessor(trace_exporter)
            _global_tracer_provider.add_span_processor(span_processor)
            print(f"📡 OpenTelemetry traces enabled: {trace_endpoint}")
        
        # ★ Configure Logger Provider for OTLP log export (if logs SDK available)
        if LOGS_AVAILABLE:
            _global_logger_provider = LoggerProvider(resource=resource)
            set_logger_provider(_global_logger_provider)
            
            # Configure log exporter if endpoint is provided
            log_endpoint = os.getenv('OTEL_EXPORTER_OTLP_LOGS_ENDPOINT')
            if log_endpoint:
                log_exporter = OTLPLogExporter(endpoint=log_endpoint)
                log_processor = BatchLogRecordProcessor(log_exporter)
                _global_logger_provider.add_log_record_processor(log_processor)
                print(f"📡 OpenTelemetry logs enabled: {log_endpoint}")
        else:
            log_endpoint = os.getenv('OTEL_EXPORTER_OTLP_LOGS_ENDPOINT')
            if log_endpoint:
                print(f"⚠️  OTLP logs endpoint configured ({log_endpoint}) but logs SDK not available")
        
        # Enable auto-instrumentation for common libraries
        try:
            autoinstrument()
            print("🔧 OpenTelemetry auto-instrumentation enabled")
        except Exception as e:
            print(f"⚠️  Auto-instrumentation failed: {e}")
            
    except Exception as e:
        print(f"⚠️  OpenTelemetry SDK configuration failed: {e}")

def _map_severity(level_str: str):
    """Map log level to OpenTelemetry severity number"""
    if not LOGS_AVAILABLE:
        return 9  # Default to INFO number
        
    level_mapping = {
        'TRACE': SeverityNumber.TRACE,
        'DEBUG': SeverityNumber.DEBUG,
        'INFO': SeverityNumber.INFO,
        'WARN': SeverityNumber.WARN,
        'WARNING': SeverityNumber.WARN,
        'ERROR': SeverityNumber.ERROR,
        'FATAL': SeverityNumber.FATAL,
        'CRITICAL': SeverityNumber.FATAL
    }
    return level_mapping.get(level_str.upper(), SeverityNumber.INFO)

def _opentelemetry_processor(logger, method_name, event_dict):
    """Custom structlog processor that sends logs to OpenTelemetry OTLP - matching TypeScript Winston transport"""
    
    try:
        # Inject trace context if available
        span = trace.get_current_span()
        current_trace_id = None
        current_span_id = None
        current_trace_flags = None
        if span and span.get_span_context().is_valid:
            span_context = span.get_span_context()
            event_dict["traceId"] = f"{span_context.trace_id:032x}"
            event_dict["spanId"] = f"{span_context.span_id:016x}"
            current_trace_id = span_context.trace_id
            current_span_id = span_context.span_id
            current_trace_flags = span_context.trace_flags
        
        # ★ Send structured logs to OpenTelemetry if logs SDK available
        global _global_logger_provider
        if LOGS_AVAILABLE and _global_logger_provider and os.getenv('OTEL_EXPORTER_OTLP_LOGS_ENDPOINT'):
            # Get logger from the logger provider (which has the resource)
            otel_logger = _global_logger_provider.get_logger(__name__)
            
            # Extract message and attributes
            message = event_dict.get('message', event_dict.get('event', 'Log entry'))
            attributes = {k: v for k, v in event_dict.items() if k not in ['message', 'event']}
            
            # Map log level to severity
            severity = _map_severity(event_dict.get('level', 'INFO'))
            
            # Create LogRecord and emit to OpenTelemetry
            from opentelemetry.trace import TraceFlags
            log_record = LogRecord(
                timestamp=int(time.time_ns()),
                body=message,
                severity_number=severity,
                severity_text=event_dict.get('level', 'INFO'),
                attributes=attributes,
                trace_id=current_trace_id or 0,
                span_id=current_span_id or 0,
                trace_flags=current_trace_flags or TraceFlags.DEFAULT
            )
            
            # ★ WORKAROUND: Add missing attributes to LogRecord for encoder
            # The encoder expects several attributes that LogRecord doesn't have by design
            # This is a temporary fix until proper solution is found
            log_record.resource = _global_logger_provider._resource
            log_record.dropped_attributes = 0
            
            otel_logger.emit(log_record)
        
    except Exception as e:
        # Don't break logging if OpenTelemetry fails
        print(f"⚠️  OpenTelemetry log export failed: {e}")
    
    return event_dict

# =============================================================================
# TRANSPORT CONFIGURATION - MULTIPLE SIMULTANEOUS TRANSPORTS
# =============================================================================

def _create_file_handler():
    """Create file handler if LOG_TO_FILE environment variable is set"""
    if os.getenv('LOG_TO_FILE') != 'true':
        return None
    
    # Get log file path from environment variable or use default
    log_file_path = os.getenv('LOG_FILE_PATH', './logs/app.log')
    log_dir = os.path.dirname(log_file_path)
    
    # Ensure log directory exists
    try:
        os.makedirs(log_dir, exist_ok=True)
        print(f"📁 Created log directory: {log_dir}")
    except Exception as error:
        print(f"⚠️  Could not create log directory {log_dir}: {error}")
        return None
    
    # Setup rotating file handler with proper size limits
    file_handler = RotatingFileHandler(
        log_file_path,
        maxBytes=50 * 1024 * 1024,  # 50MB
        backupCount=5
    )
    file_handler.setFormatter(logging.Formatter('%(message)s'))
    
    print(f"📝 File logging enabled: {log_file_path}")
    
    return file_handler

def _create_error_file_handler():
    """Create separate error file handler for ERROR and FATAL logs"""
    if os.getenv('LOG_TO_FILE') != 'true':
        return None
    
    # Get error log file path
    base_log_path = os.getenv('LOG_FILE_PATH', './logs/app.log')
    error_log_path = base_log_path.replace('.log', '-errors.log')
    error_dir = os.path.dirname(error_log_path)
    
    # Ensure log directory exists
    try:
        os.makedirs(error_dir, exist_ok=True)
    except Exception as error:
        print(f"⚠️  Could not create error log directory {error_dir}: {error}")
        return None
    
    # Setup rotating error file handler
    error_handler = RotatingFileHandler(
        error_log_path,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=3
    )
    error_handler.setFormatter(logging.Formatter('%(message)s'))
    error_handler.setLevel(logging.ERROR)
    
    print(f"📝 Error file logging enabled: {error_log_path}")
    
    return error_handler

def _rename_event_to_message(logger, method_name, event_dict):
    """Custom processor to rename 'event' field to 'message' for consistency"""
    if 'event' in event_dict:
        event_dict['message'] = event_dict.pop('event')
    return event_dict

def _configure_structlog():
    """Configure structlog with multiple simultaneous transports - similar to TypeScript Winston"""
    processors = [
        structlog.stdlib.filter_by_level,
        # Remove add_logger_name to avoid extra "logger" field
        # structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        _rename_event_to_message,  # Custom processor to fix field naming
        _opentelemetry_processor,   # ★ NEW: Send to OpenTelemetry (like TypeScript Winston transport)
        structlog.processors.JSONRenderer()
    ]
    
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Configure multiple simultaneous handlers - similar to TypeScript Winston transports
    handlers = []
    
    # ★ Console handler (always enabled - like TypeScript)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(message)s'))
    handlers.append(console_handler)
    print("📟 Console logging enabled")
    
    # ★ File handler (optional - like TypeScript)
    file_handler = _create_file_handler()
    if file_handler:
        handlers.append(file_handler)
    
    # ★ Error file handler (optional - like TypeScript)
    error_handler = _create_error_file_handler()
    if error_handler:
        handlers.append(error_handler)
    
    # ★ OTLP handler is handled by _opentelemetry_processor
    otlp_enabled = os.getenv('OTEL_EXPORTER_OTLP_LOGS_ENDPOINT')
    if otlp_enabled:
        print(f"📡 OTLP logging enabled: {otlp_enabled}")
    
    # Configure Python logging with multiple handlers
    logging.basicConfig(
        format="%(message)s",
        level=logging.DEBUG,
        handlers=handlers,
        force=True  # Force reconfiguration
    )

# Structlog will be configured when first logger is created

class _InternalUrbLogger:
    """Internal logger class - handles all complexity, hidden from developers"""
    
    def __init__(self, system_id: str):
        self.system_id = system_id
        self.logger = structlog.get_logger()
    
    def _create_log_entry(
        self,
        level: str,
        function_name: str,
        message: str,
        exception_object: Any,
        input_json: Optional[Dict[str, Any]] = None,
        response_json: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a complete structured log entry with all required fields"""
        
        # Auto-generate correlation ID for request tracing
        correlation_id = str(uuid.uuid4())
        
        # Auto-inject OpenTelemetry trace context if available
        span = trace.get_current_span()
        trace_id = None
        span_id = None
        
        if span and span.get_span_context().is_valid:
            span_context = span.get_span_context()
            trace_id = f"{span_context.trace_id:032x}"
            span_id = f"{span_context.span_id:016x}"
        
        # Process exception object if provided
        processed_exception = None
        if exception_object is not None:
            processed_exception = self._process_exception(exception_object)
        
        # Create the complete log entry
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": self._map_log_level(level),
            "systemId": self.system_id,
            "functionName": function_name,
            "message": message,
            "correlationId": correlation_id,
        }
        
        # Add optional fields if they exist
        if trace_id:
            log_entry["traceId"] = trace_id
        if span_id:
            log_entry["spanId"] = span_id
        if input_json is not None:
            log_entry["inputJSON"] = input_json
        if response_json is not None:
            log_entry["responseJSON"] = response_json
        if processed_exception is not None:
            log_entry["exception"] = processed_exception
        
        return log_entry
    
    def _map_log_level(self, level: str) -> str:
        """Map log level to Urbalurba standard format"""
        if level.upper() == 'WARN':
            return 'warn'
        return level.lower()
    
    def _process_exception(self, exception_object: Any) -> Dict[str, Any]:
        """Process exception objects with security cleanup and standardization"""
        
        # Security: Remove sensitive data if it's a requests exception
        clean_exception = exception_object
        
        if hasattr(exception_object, '__dict__'):
            # Create a copy to avoid modifying the original
            clean_exception = type(exception_object).__new__(type(exception_object))
            clean_exception.__dict__.update(exception_object.__dict__)
            
            # Remove auth headers if present
            if hasattr(clean_exception, 'request') and hasattr(clean_exception.request, 'headers'):
                if 'Authorization' in clean_exception.request.headers:
                    clean_exception.request.headers = dict(clean_exception.request.headers)
                    del clean_exception.request.headers['Authorization']
        
        # Extract exception information
        if isinstance(clean_exception, Exception):
            stack_trace = ''.join(traceback.format_exception(
                type(clean_exception), clean_exception, clean_exception.__traceback__
            ))
            
            # Limit stack trace to 350 characters
            if len(stack_trace) > 350:
                stack_trace = stack_trace[:350]
            
            return {
                "type": type(clean_exception).__name__,
                "message": str(clean_exception),
                "stack": stack_trace
            }
        else:
            return {
                "type": "Unknown",
                "message": str(clean_exception)
            }
    
    def _write_log(self, level: str, log_entry: Dict[str, Any]) -> None:
        """Write log entry using structlog"""
        try:
            # Map levels to structlog methods
            level_mapping = {
                'TRACE': self.logger.debug,  # TRACE maps to debug
                'DEBUG': self.logger.debug,
                'INFO': self.logger.info,
                'WARN': self.logger.warning,
                'ERROR': self.logger.error,
                'FATAL': self.logger.critical
            }
            
            log_method = level_mapping.get(level, self.logger.info)
            
            # Extract message from log_entry for proper structlog usage
            message = log_entry.get('message', 'Log entry')
            
            # Create a copy without the message field for structured logging
            structured_fields = {k: v for k, v in log_entry.items() if k != 'message'}
            
            # Log using proper structlog pattern with structured fields
            log_method(message, **structured_fields)
            
        except Exception as err:
            # Fallback - logging should never break the application
            print(f"Urbalurba Logger failed: {err}")
            print(json.dumps(log_entry))
    
    def log(
        self,
        level: str,
        function_name: str,
        message: str,
        exception_object: Any,
        input_json: Optional[Dict[str, Any]] = None,
        response_json: Optional[Dict[str, Any]] = None
    ) -> None:
        """Main logging method"""
        log_entry = self._create_log_entry(
            level, function_name, message, exception_object, input_json, response_json
        )
        self._write_log(level, log_entry)
    
    def log_job_status(
        self,
        level: str,
        function_name: str,
        job_name: str,
        status: str,
        input_json: Optional[Dict[str, Any]] = None
    ) -> None:
        """Job status logging"""
        message = f"Job {status}: {job_name}"
        context_input = {
            "jobName": job_name,
            "jobStatus": status
        }
        if input_json:
            context_input.update(input_json)
        
        self.log(level, function_name, message, None, context_input, None)
    
    def log_job_progress(
        self,
        level: str,
        function_name: str,
        job_name: str,
        item_id: str,
        current: int,
        total: int,
        input_json: Optional[Dict[str, Any]] = None
    ) -> None:
        """Job progress logging"""
        message = f"Processing {item_id} ({current}/{total})"
        context_input = {
            "jobName": job_name,
            "itemId": item_id,
            "currentItem": current,
            "totalItems": total,
            "progressPercentage": round((current / total) * 100)
        }
        if input_json:
            context_input.update(input_json)
        
        self.log(level, function_name, message, None, context_input, None)

# =============================================================================
# GLOBAL LOGGER INSTANCE MANAGEMENT
# =============================================================================

# Global logger instance - initialized once per application
_global_logger: Optional[_InternalUrbLogger] = None

def urbinitializelogger(system_id: str) -> None:
    """
    Initialize the Urbalurba logger with system identifier
    Must be called once at application startup
    
    Args:
        system_id: Unique system identifier (e.g., "INT0001001", "brreglib")
    """
    global _global_logger
    
    if not system_id or not system_id.strip():
        raise ValueError('Urbalurba Logger: systemId is required and cannot be empty')
    
    # ★ NEW: Configure OpenTelemetry SDK first (like TypeScript NodeSDK)
    _configure_opentelemetry_sdk(system_id.strip())
    
    # Configure structlog when logger is first initialized (after env vars are loaded)
    _configure_structlog()
    
    _global_logger = _InternalUrbLogger(system_id.strip())

def _ensure_logger() -> _InternalUrbLogger:
    """Ensure logger is initialized before use"""
    if _global_logger is None:
        raise RuntimeError(
            'Urbalurba Logger not initialized. Call urbinitializelogger(systemId) at application startup.'
        )
    return _global_logger

# =============================================================================
# PUBLIC API - IDENTICAL ACROSS ALL LANGUAGES
# =============================================================================

def urblog(
    level: str,
    function_name: str,
    message: str,
    exception_object: Any,
    input_json: Optional[Dict[str, Any]] = None,
    response_json: Optional[Dict[str, Any]] = None
) -> None:
    """
    General purpose logging function
    
    Args:
        level: Log level from LOG_LEVELS constants
        function_name: Name of the function where logging occurs
        message: Human-readable description of what happened
        exception_object: Exception/error object (None if no exception)
        input_json: Valid dict containing function input parameters (optional)
        response_json: Valid dict containing function output/response data (optional)
    """
    _ensure_logger().log(level, function_name, message, exception_object, input_json, response_json)

def urblogjobstatus(
    level: str,
    function_name: str,
    job_name: str,
    status: str,
    input_json: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log job lifecycle events (start, completion, failure)
    
    Args:
        level: Log level from LOG_LEVELS constants
        function_name: Name of the function managing the job
        job_name: Name of the job being tracked
        status: Job status (e.g., "Started", "Completed", "Failed")
        input_json: Additional job context variables (optional)
    """
    _ensure_logger().log_job_status(level, function_name, job_name, status, input_json)

def urblogjobprogress(
    level: str,
    function_name: str,
    item_id: str,
    current: int,
    total: int,
    input_json: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log processing progress for batch operations
    
    Args:
        level: Log level from LOG_LEVELS constants
        function_name: Name of the function doing the processing
        item_id: Identifier for the item being processed
        current: Current item number (1-based)
        total: Total number of items to process
        input_json: Additional context variables for this item (optional)
    """
    _ensure_logger().log_job_progress(level, function_name, "BatchProcessing", item_id, current, total, input_json)

# =============================================================================
# FLUSH FUNCTIONALITY - MATCHING TYPESCRIPT
# =============================================================================

def urbflushlog() -> None:
    """
    Flush all logs and shutdown OpenTelemetry gracefully
    ★ UPDATED: Matching TypeScript urbflushlog() function with log support if available
    
    Call this before application shutdown to ensure all logs are exported
    """
    global _global_tracer_provider, _global_logger_provider
    
    try:
        # Flush logger provider first (logs are more important than traces) if available
        if LOGS_AVAILABLE and _global_logger_provider:
            _global_logger_provider.force_flush()
            print("📤 Flushed OpenTelemetry logs")
        
        # Flush tracer provider
        if _global_tracer_provider:
            _global_tracer_provider.force_flush()
            print("📤 Flushed OpenTelemetry traces")
        
        # Shutdown logger provider if available
        if LOGS_AVAILABLE and _global_logger_provider:
            _global_logger_provider.shutdown()
            print("🔒 Shutdown OpenTelemetry logger")
        
        # Shutdown tracer provider
        if _global_tracer_provider:
            _global_tracer_provider.shutdown()
            print("🔒 Shutdown OpenTelemetry tracer")
            
        print("✅ Urbalurba logging shutdown complete")
        
    except Exception as e:
        print(f"⚠️  Error during flush: {e}")

async def urbflushlog_async() -> None:
    """
    Async version of urbflushlog for applications using async/await
    """
    # Run the synchronous flush in a thread to avoid blocking
    import concurrent.futures
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        await asyncio.get_event_loop().run_in_executor(executor, urbflushlog)

"""
Usage Summary:

1. Initialize once at startup:
   urbinitializelogger("your-system-id")

2. Use in functions:
   FUNCTIONNAME = "myFunction"
   urblog(LOG_LEVELS.INFO, FUNCTIONNAME, "Processing completed", None, {"userId": "12345"}, {"status": "success"})
   urblogjobstatus(LOG_LEVELS.INFO, FUNCTIONNAME, "DataSync", "Started", {"batchSize": 100})
   urblogjobprogress(LOG_LEVELS.INFO, FUNCTIONNAME, "item-5", 5, 100, {"status": "success"})

3. Log levels guide:
   - TRACE: Successful operations, detailed debugging
   - DEBUG: Development information, function flow
   - INFO: Important events, data issues, progress tracking
   - WARN: Potential problems, missing parameters
   - ERROR: Actual failures, API errors
   - FATAL: Critical system failures
"""