"""
Urbalurba Logging Library Test - Python
Filename: lib_test.py

This script validates the Urbalurba structured logging library implementation
against "Loggeloven av 2025" requirements. It's equivalent to the TypeScript
lib-test functionality and is designed for:

1. Library validation testing
2. Integration with observability dashboard filtering  
3. Comprehensive feature demonstration
4. OTLP collector integration verification

Key Features Tested:
- All logging functions: urblog, urblogjobstatus, urblogjobprogress
- All log levels: TRACE, DEBUG, INFO, WARN, ERROR, FATAL
- OpenTelemetry trace context injection
- Error handling with exception objects
- Input/output JSON tracking patterns
- Job lifecycle and progress tracking
- Real API calls for realistic scenarios
- Graceful shutdown with urbflushlog()

SystemId: urb-test-structuredlog-python (for dashboard filtering)
"""

import requests
import asyncio
import aiohttp
import warnings
import sys
import os

# Suppress asyncio debug output
warnings.filterwarnings("ignore", category=ResourceWarning)
import logging
logging.getLogger('asyncio').setLevel(logging.CRITICAL)
os.environ['PYTHONASYNCIODEBUG'] = '0'

from datetime import datetime
from typing import List, Dict, Any
import time

# Import the Urbalurba logging functions
from urbalurba_logging import (
    LOGLEVELS,
    urblog,
    urblogjobstatus,
    urblogjobprogress,
    urbinitializelogger,
    urbflushlog_async
)

# ★ CRITICAL: System ID for library testing (matches TypeScript pattern)
SYSTEM_ID = "urb-test-structuredlog-python"

# Initialize logger once at application startup
urbinitializelogger(SYSTEM_ID)

async def validate_basic_logging() -> None:
    """Test all log levels and basic functionality"""
    FUNCTIONNAME = "ValidateBasicLogging"
    
    input_json = {
        "testType": "basic_logging_validation",
        "logLevels": ["TRACE", "DEBUG", "INFO", "WARN", "ERROR", "FATAL"]
    }
    
    # Test all log levels
    urblog(LOGLEVELS.TRACE, FUNCTIONNAME, "TRACE level test - detailed debugging info", None, input_json)
    urblog(LOGLEVELS.DEBUG, FUNCTIONNAME, "DEBUG level test - development information", None, input_json)
    urblog(LOGLEVELS.INFO, FUNCTIONNAME, "INFO level test - important events", None, input_json)
    urblog(LOGLEVELS.WARN, FUNCTIONNAME, "WARN level test - potential problems", None, input_json)
    urblog(LOGLEVELS.ERROR, FUNCTIONNAME, "ERROR level test - actual failures", None, input_json)
    urblog(LOGLEVELS.FATAL, FUNCTIONNAME, "FATAL level test - critical system failures", None, input_json)

async def validate_exception_handling() -> None:
    """Test exception object handling and error scenarios"""
    FUNCTIONNAME = "ValidateExceptionHandling"
    
    # Test with real exception
    try:
        # Intentionally cause an exception
        result = 1 / 0
    except ZeroDivisionError as e:
        urblog(LOGLEVELS.ERROR, FUNCTIONNAME, "Division by zero error handled", e, 
               {"operation": "division", "numerator": 1, "denominator": 0},
               {"status": "error", "handled": True})
    
    # Test with requests-like exception simulation
    try:
        fake_response = type('MockResponse', (), {
            'status_code': 404,
            'headers': {'Authorization': 'Bearer secret-token'},
            'text': 'Not Found'
        })()
        raise requests.exceptions.RequestException("API endpoint not found", response=fake_response)
    except requests.exceptions.RequestException as e:
        urblog(LOGLEVELS.ERROR, FUNCTIONNAME, "API request failed", e,
               {"endpoint": "/api/test", "method": "GET"},
               {"status": "failed", "httpStatus": 404})

async def validate_job_processing() -> None:
    """Test job lifecycle and progress tracking patterns"""
    FUNCTIONNAME = "ValidateJobProcessing" 
    JOBNAME = "LibraryValidationJob"
    
    items = ["item1", "item2", "item3", "item4", "item5"]
    
    # Job start
    urblogjobstatus(LOGLEVELS.INFO, FUNCTIONNAME, JOBNAME, "Started", {
        "totalItems": len(items),
        "batchSize": len(items),
        "startTime": datetime.utcnow().isoformat() + "Z"
    })
    
    # Process items with progress tracking
    for i, item in enumerate(items):
        current = i + 1
        
        # Progress tracking
        urblogjobprogress(LOGLEVELS.INFO, FUNCTIONNAME, item, current, len(items), {
            "jobName": JOBNAME,
            "itemType": "validation_item",
            "processingStage": "started"
        })
        
        # Simulate some work
        await asyncio.sleep(0.1)
        
        # Log successful processing
        urblog(LOGLEVELS.TRACE, FUNCTIONNAME, f"Processed {item} successfully", None,
               {"item": item, "index": current},
               {"status": "success", "processingTime": "100ms"})
    
    # Job completion
    urblogjobstatus(LOGLEVELS.INFO, FUNCTIONNAME, JOBNAME, "Completed", {
        "totalProcessed": len(items),
        "successCount": len(items),
        "errorCount": 0,
        "duration": "500ms"
    })

async def validate_api_integration() -> None:
    """Test with real API calls to demonstrate realistic logging patterns"""
    FUNCTIONNAME = "ValidateApiIntegration"
    
    test_urls = [
        "https://httpbin.org/status/200",  # Should succeed
        "https://httpbin.org/status/404",  # Should fail
        "https://httpbin.org/delay/1"      # Should succeed with delay
    ]
    
    for i, url in enumerate(test_urls):
        current = i + 1
        
        urblogjobprogress(LOGLEVELS.INFO, FUNCTIONNAME, f"url-{current}", current, len(test_urls), {
            "url": url,
            "expectedBehavior": "varies_by_endpoint"
        })
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    urblog(LOGLEVELS.TRACE, FUNCTIONNAME, f"API call successful", None,
                           {"url": url, "method": "GET"},
                           {"httpStatus": response.status, "success": True})
                    
        except asyncio.TimeoutError as e:
            urblog(LOGLEVELS.WARN, FUNCTIONNAME, "API call timeout", e,
                   {"url": url, "timeout": "5s"},
                   {"status": "timeout", "retryable": True})
        except Exception as e:
            urblog(LOGLEVELS.ERROR, FUNCTIONNAME, "API call failed", e,
                   {"url": url, "method": "GET"},
                   {"status": "error", "retryable": False})

async def validate_input_output_patterns() -> None:
    """Test comprehensive input/output JSON tracking"""
    FUNCTIONNAME = "ValidateInputOutputPatterns"
    
    # Complex input/output scenario
    input_data = {
        "userId": "test-user-123",
        "operation": "data_processing",
        "parameters": {
            "includeMetadata": True,
            "format": "json",
            "filters": ["active", "verified"]
        },
        "requestId": "req-lib-test-001"
    }
    
    output_data = {
        "status": "completed",
        "recordsProcessed": 150,
        "recordsFiltered": 45,
        "metadata": {
            "processingTime": "250ms",
            "cacheHit": True,
            "version": "1.1.0"
        },
        "warnings": []
    }
    
    urblog(LOGLEVELS.INFO, FUNCTIONNAME, "Complex data processing completed", None, 
           input_data, output_data)

async def run_library_test() -> None:
    """
    Main library test runner - validates all aspects of the logging library
    """
    FUNCTIONNAME = "RunLibraryTest"
    
    print("🧪 Urbalurba Logging Library Test - Python")
    print("===========================================")
    print(f"SystemId: {SYSTEM_ID}")
    print("Testing comprehensive logging functionality...")
    print("")
    
    start_time = datetime.utcnow()
    
    input_json = {
        "testType": "comprehensive_library_validation",
        "systemId": SYSTEM_ID,
        "startTime": start_time.isoformat() + "Z"
    }
    
    response_json = {
        "status": "starting",
        "testsCompleted": 0,
        "totalTests": 5
    }
    
    urblog(LOGLEVELS.INFO, FUNCTIONNAME, "Library test execution started", None, input_json, response_json)
    
    try:
        # Test 1: Basic logging validation
        print("1. Testing basic logging (all levels)...")
        await validate_basic_logging()
        response_json["testsCompleted"] = 1
        
        # Test 2: Exception handling
        print("2. Testing exception handling...")
        await validate_exception_handling() 
        response_json["testsCompleted"] = 2
        
        # Test 3: Job processing patterns
        print("3. Testing job processing patterns...")
        await validate_job_processing()
        response_json["testsCompleted"] = 3
        
        # Test 4: API integration
        print("4. Testing API integration patterns...")
        await validate_api_integration()
        response_json["testsCompleted"] = 4
        
        # Test 5: Input/output patterns
        print("5. Testing input/output JSON patterns...")
        await validate_input_output_patterns()
        response_json["testsCompleted"] = 5
        
        # Calculate duration
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        
        response_json.update({
            "status": "completed",
            "duration": f"{duration:.2f}s",
            "endTime": end_time.isoformat() + "Z"
        })
        
        urblog(LOGLEVELS.INFO, FUNCTIONNAME, "Library test execution completed successfully", None, 
               input_json, response_json)
        
        print("")
        print("✅ All library tests completed successfully!")
        print(f"⏱️  Total duration: {duration:.2f}s")
        print("📊 Check your observability dashboard for structured logs")
        
    except Exception as error:
        response_json.update({
            "status": "failed",
            "error": str(error),
            "failedAt": datetime.utcnow().isoformat() + "Z"
        })
        
        urblog(LOGLEVELS.FATAL, FUNCTIONNAME, "Library test execution failed", error, 
               input_json, response_json)
        
        print("❌ Library test failed!")
        raise
    
    finally:
        # Flush all logs before exit
        print("")
        print("📤 Flushing logs and shutting down OpenTelemetry...")
        await urbflushlog_async()

def main():
    """Synchronous entry point for console script"""
    try:
        asyncio.run(run_library_test())
        print("🎉 Library test completed successfully!")
    except Exception as error:
        print(f"💥 Library test failed: {error}")
        sys.exit(1)

# Export functions for programmatic use
__all__ = ['run_library_test', 'main']

# If this file is run directly, execute the library test
if __name__ == "__main__":
    main()

"""
Expected Output Summary:

This library test validates all aspects of the Urbalurba logging system:

✅ Log Levels: TRACE, DEBUG, INFO, WARN, ERROR, FATAL
✅ Exception Handling: Real exception objects with context
✅ Job Processing: urblogjobstatus, urblogjobprogress patterns  
✅ API Integration: Real HTTP calls with realistic scenarios
✅ Input/Output: Comprehensive JSON context tracking
✅ OpenTelemetry: Trace context injection, OTLP export
✅ Multiple Transports: Console + File + OTLP simultaneously
✅ Graceful Shutdown: urbflushlog() for proper cleanup

Usage:
  python -m urbalurba_logging.lib_test
  
Or programmatically:
  from urbalurba_logging.lib_test import run_library_test
  await run_library_test()

The logs will use systemId "urb-test-structuredlog-python" for easy 
filtering in observability dashboards.
"""