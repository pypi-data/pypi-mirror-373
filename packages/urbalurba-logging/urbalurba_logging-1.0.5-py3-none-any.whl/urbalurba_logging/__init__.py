"""
Urbalurba Logging - Python Package

Professional Python implementation of the Urbalurba structured logging system
following "Loggeloven av 2025" requirements.

This package provides a simple, consistent API for structured logging across
all programming languages with OpenTelemetry integration.
"""

from .log_levels import LOGLEVELS
from .urblogger import urbinitializelogger, urblog, urblogjobstatus, urblogjobprogress, urbflushlog, urbflushlog_async

__version__ = "1.0.5"
__author__ = "Terje Christensen"
__email__ = "integration-platform@redcross.no"

# Export the public API
__all__ = [
    'LOGLEVELS',
    'urbinitializelogger', 
    'urblog',
    'urblogjobstatus',
    'urblogjobprogress',
    'urbflushlog',
    'urbflushlog_async'
]