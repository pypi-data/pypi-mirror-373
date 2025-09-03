# Urbalurba Logging - Python Implementation

Professional Python implementation of Urbalurba structured logging following "Loggeloven av 2025" requirements. Provides consistent API across all programming languages with **full OpenTelemetry integration** and **production-ready OTLP export** capabilities.

## ✅ Current Status: **PRODUCTION READY**

- **🎉 Complete Feature Parity**: Matches TypeScript Winston → OpenTelemetry architecture
- **📡 OTLP Export**: Fully functional logs + traces export to observability stack
- **🔄 Multiple Transports**: Simultaneous console + file + OTLP logging
- **🧪 Comprehensive Testing**: Demo, library tests, and real-world validation complete
- **📊 Live Verification**: Successfully integrated with Loki + Grafana observability stack

## Repository

This package is part of the multi-language Urbalurba logging system:
- **Repository**: https://github.com/terchris/urbalurba-logging  
- **Python Package**: https://github.com/terchris/urbalurba-logging/tree/main/python

## Installation

### From Source (Current Method)
```bash
git clone https://github.com/terchris/urbalurba-logging.git
cd urbalurba-logging/python
pip install -e .
```

### From PyPI
```bash
pip install urbalurba-logging
```

### From Test PyPI
```bash
pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ urbalurba-logging
```

## Quick Start

### 1. Initialize Logger (Required)
```python
from urbalurba_logging import urbinitializelogger, urblog, LOGLEVELS

# Initialize once at application startup
urbinitializelogger("your-system-id")
```

### 2. Basic Logging
```python
FUNCTIONNAME = "MyFunction"

# Simple logging
urblog(LOGLEVELS.INFO, FUNCTIONNAME, "Processing completed", None)

# With context data
urblog(LOGLEVELS.INFO, FUNCTIONNAME, "User created", None, 
       {"userId": "12345"}, {"status": "success"})

# Error logging with exception
try:
    # some operation
    pass
except Exception as error:
    urblog(LOGLEVELS.ERROR, FUNCTIONNAME, "Operation failed", error)
```

### 3. Job Tracking
```python
from urbalurba_logging import urblogjobstatus, urblogjobprogress

FUNCTIONNAME = "ProcessData"

# Job lifecycle tracking
urblogjobstatus(LOGLEVELS.INFO, FUNCTIONNAME, "DataImport", "Started")
urblogjobprogress(LOGLEVELS.INFO, FUNCTIONNAME, "item-1", 1, 100)
urblogjobstatus(LOGLEVELS.INFO, FUNCTIONNAME, "DataImport", "Completed")
```

### 4. Graceful Shutdown
```python
from urbalurba_logging import urbflushlog

# Flush all logs before application exit
urbflushlog()
```

## Running the Demo

The demo demonstrates real-world usage with API calls and comprehensive logging patterns.

### Step 1: Clone and Navigate
```bash
git clone https://github.com/terchris/urbalurba-logging.git
cd urbalurba-logging/python/examples/demo
```

### Step 2: Install Dependencies
```bash
# Install demo dependencies
pip install -r requirements.txt

# Install main package in development mode
pip install -e ../../
```

### Step 3: Configure Environment
```bash
# Run interactive setup (choose logging destination)
./setup-dev-env.sh
```

Choose from three options:
1. **Console Output** - JSON logs to terminal (good for development)
2. **File Logging** - Logs to `./logs/dev.log` (good for analysis)  
3. **OTLP Collector** - Export to observability stack (requires Docker)

### Step 4: Run Demo
```bash
python demo.py
```

## Project Structure

```
python/
├── src/
│   └── urbalurba_logging/
│       ├── __init__.py          # Package exports
│       ├── urblogger.py         # Core logging implementation  
│       └── log_levels.py        # Log level constants
├── examples/
│   └── demo/
│       ├── demo.py              # Complete working example
│       ├── requirements.txt     # Demo dependencies
│       ├── setup-dev-env.sh     # Development environment setup
│       └── .env                 # Environment template
├── setup.py                     # PyPI package configuration
├── requirements.txt             # Main dependencies
└── README-python.md            # This documentation
```

## API Reference

### Initialization

**`urbinitializelogger(system_id: str)`**
- **Required**: Must be called once at application startup
- **Purpose**: Initialize logger with unique system identifier
- **Example**: `urbinitializelogger("payment-service")`

### Core Logging

**`urblog(level, function_name, message, exception, input_json=None, response_json=None)`**
- **Purpose**: General purpose structured logging
- **Parameters**:
  - `level`: Use `LOGLEVELS` constants (INFO, ERROR, etc.)
  - `function_name`: Name of calling function (use constant)
  - `message`: Human-readable description
  - `exception`: Exception object or None
  - `input_json`: Input parameters/context (optional)
  - `response_json`: Output/response data (optional)

### Job Tracking

**`urblogjobstatus(level, function_name, job_name, status, input_json=None)`**
- **Purpose**: Track job lifecycle (Started, Completed, Failed)
- **Example**: `urblogjobstatus(LOGLEVELS.INFO, "ProcessPayments", "MonthlyBatch", "Started")`

**`urblogjobprogress(level, function_name, item_id, current, total, input_json=None)`**
- **Purpose**: Track progress through collections/batches
- **Example**: `urblogjobprogress(LOGLEVELS.INFO, "ProcessPayments", "payment-123", 5, 100)`

### Log Levels

| Level | Purpose | Usage Example |
|-------|---------|---------------|
| `LOGLEVELS.TRACE` | Detailed debugging | Successful operations with full context |
| `LOGLEVELS.DEBUG` | Development info | Function entry/exit, data flow |
| `LOGLEVELS.INFO` | Important events | Business logic, progress tracking |
| `LOGLEVELS.WARN` | Potential issues | Missing optional parameters, retries |
| `LOGLEVELS.ERROR` | Actual failures | API errors, validation failures |
| `LOGLEVELS.FATAL` | Critical failures | System crashes, data corruption |

## Output Format

All logs are structured JSON with consistent fields:

```json
{
  "timestamp": "2025-07-04T12:54:34.447Z",
  "level": "info",
  "systemId": "payment-service", 
  "functionName": "ProcessPayment",
  "correlationId": "e804d7c4-4592-42e6-9923-ab4dad45f41f",
  "message": "Payment processed successfully",
  "inputJSON": {"userId": "12345", "amount": 100.00},
  "responseJSON": {"transactionId": "tx-789", "status": "completed"}
}
```

## Environment Configuration

Create `.env.development` (or use setup script):

```bash
# Logging configuration
LOG_TO_FILE=true
LOG_FILE_PATH=./logs/dev.log
LOG_LEVEL=INFO

# OpenTelemetry OTLP Export (production-ready)
OTEL_EXPORTER_OTLP_TRACES_ENDPOINT=http://localhost:4318/v1/traces
OTEL_EXPORTER_OTLP_LOGS_ENDPOINT=http://localhost:4318/v1/logs
OTEL_ENVIRONMENT=development

# Environment
PYTHON_ENV=development
```

## Dependencies

Core dependencies installed automatically:

- **structlog** ≥23.1.0 - Structured logging framework
- **opentelemetry-api** ≥1.21.0 - OpenTelemetry API for tracing  
- **opentelemetry-sdk** ≥1.21.0 - OpenTelemetry SDK
- **opentelemetry-exporter-otlp-proto-http** ≥1.21.0 - OTLP HTTP exporter
- **opentelemetry-sdk-logs** ≥1.21.0 - OpenTelemetry logs SDK
- **opentelemetry-api-logs** ≥1.21.0 - OpenTelemetry logs API
- **opentelemetry-instrumentation-auto** ≥1.21.0 - Auto-instrumentation
- **requests** ≥2.31.0 - HTTP client library

## Production Usage

### OTLP Export (Recommended)
```python
import os
# Configure OTLP endpoints for production observability stack
os.environ['OTEL_EXPORTER_OTLP_TRACES_ENDPOINT'] = 'https://your-otel-collector.com/v1/traces'
os.environ['OTEL_EXPORTER_OTLP_LOGS_ENDPOINT'] = 'https://your-otel-collector.com/v1/logs'
os.environ['OTEL_ENVIRONMENT'] = 'production'

from urbalurba_logging import urbinitializelogger, urbflushlog
urbinitializelogger("production-service")

# Your application code here...

# Graceful shutdown
urbflushlog()
```

### Multiple Transports (Console + File + OTLP)
```python
import os
# Enable all transports simultaneously
os.environ['LOG_TO_FILE'] = 'true'
os.environ['LOG_FILE_PATH'] = '/var/log/myapp/app.log'
os.environ['OTEL_EXPORTER_OTLP_TRACES_ENDPOINT'] = 'https://your-otel-collector.com/v1/traces'
os.environ['OTEL_EXPORTER_OTLP_LOGS_ENDPOINT'] = 'https://your-otel-collector.com/v1/logs'

from urbalurba_logging import urbinitializelogger, urbflushlog
urbinitializelogger("production-service")
```

### File Logging Only
```python
import os
os.environ['LOG_TO_FILE'] = 'true'
os.environ['LOG_FILE_PATH'] = '/var/log/myapp/app.log'

from urbalurba_logging import urbinitializelogger, urbflushlog
urbinitializelogger("production-service")
```

## Best Practices

1. **Function Names**: Use constants for consistent identification
   ```python
   FUNCTIONNAME = "ProcessPayment"  # Use PascalCase
   ```

2. **Context Data**: Include relevant input/output for debugging
   ```python
   urblog(LOGLEVELS.INFO, FUNCTIONNAME, "User authenticated", None,
          {"userId": user_id}, {"sessionId": session.id})
   ```

3. **Error Handling**: Always include exception objects
   ```python
   except Exception as error:
       urblog(LOGLEVELS.ERROR, FUNCTIONNAME, "Authentication failed", error)
   ```

4. **Job Processing**: Track lifecycle and progress
   ```python
   urblogjobstatus(LOGLEVELS.INFO, FUNCTIONNAME, "DataExport", "Started")
   for item in items:
       urblogjobprogress(LOGLEVELS.INFO, FUNCTIONNAME, item.id, current, total)
   urblogjobstatus(LOGLEVELS.INFO, FUNCTIONNAME, "DataExport", "Completed")
   ```

5. **Graceful Shutdown**: Always flush logs before exit
   ```python
   from urbalurba_logging import urbflushlog
   
   try:
       # Application code here
       pass
   finally:
       urbflushlog()  # Ensures all logs are sent to OTLP collector
   ```

## Architecture

The Python implementation uses the same architecture as TypeScript:

```
structlog → OpenTelemetry → OTLP (logs + traces)
```

**Key Components:**
- **structlog**: Primary logging framework (like Winston in TypeScript)
- **OpenTelemetry Processor**: Custom processor for OpenTelemetry integration
- **Multiple Transports**: Console, file, and OTLP export simultaneous operation
- **Full SDK Configuration**: Traces, logs, and auto-instrumentation
- **Graceful Shutdown**: `urbflushlog()` ensures data delivery

## Testing

The implementation includes comprehensive testing:

1. **Demo Application**: Real-world Norwegian Brreg API integration
2. **Library Tests**: All logging scenarios and error handling
3. **Setup Scripts**: Interactive environment configuration
4. **Integration Tests**: OTLP export verified with live observability stack

## License

MIT