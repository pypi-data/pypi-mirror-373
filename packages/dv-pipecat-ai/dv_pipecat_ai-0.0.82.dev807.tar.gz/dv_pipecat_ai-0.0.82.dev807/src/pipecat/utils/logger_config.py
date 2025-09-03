# logger_config.py - MUST be imported before any other module that imports loguru

import contextvars
import datetime
import functools
import logging
import os
import socket
import sys
import traceback
from typing import Any, Dict, Optional

from loguru import logger
from loki_logger_handler.formatters.loguru_formatter import LoguruFormatter
from loki_logger_handler.loki_logger_handler import LokiLoggerHandler

# Set up log directory
log_directory = os.getenv("LOG_DIRECTORY", "/tmp/logs")
os.makedirs(log_directory, exist_ok=True)

# Get Grafana host from environment
GRAFANA_HOST = os.getenv("GRAFANA_HOST", "").strip()

# Get environment from system variables with default
ENVIRONMENT = os.getenv("ENVIRONMENT", "prod").strip()
LOGGER_NAME = os.getenv("LOGGER_NAME", "pipecat").strip()

# Remove default handler
try:
    logger.remove()
except ValueError:
    pass


def format_timestamp(ts=None):
    """Convert a timestamp to a formatted string with milliseconds.

    Args:
        ts (float, optional): Unix timestamp in seconds. If None, uses current time.

    Returns:
        str: Formatted timestamp string with milliseconds
    """
    if ts is None:
        # Use current time if no timestamp provided
        dt_obj = datetime.datetime.now()
    else:
        # Convert Unix timestamp to datetime
        dt_obj = datetime.datetime.fromtimestamp(ts)

    # Format the base timestamp
    formatted_time = dt_obj.strftime("%Y-%m-%d %H:%M:%S")

    # Add milliseconds
    millis = f"{int(dt_obj.microsecond / 1000):03d}"

    # Combine the formatted time with milliseconds
    return f"{formatted_time}.{millis}"


# def get_private_ip():
#     try:
#         s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#         s.connect(("10.255.255.255", 1))
#         ip = s.getsockname()[0]
#         s.close()
#         return ip
#     except Exception:
#         return "127.0.0.1"


def formatter(record: Dict[str, Any]) -> str:
    """Format log record with call_id and host IP, ensuring they exist."""
    if "extra" not in record:
        record["extra"] = {}

    call_id = record["extra"].get("call_id", "unknown")
    if call_id is None:
        call_id = "unknown"
    
    record["extra"]["tags"] = {
        "application": LOGGER_NAME,
        "call_id": call_id,
        "level": record["level"].name.lower(),
    }

    # Updated format string to include host IP
    format_str = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | [{call_id}] | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>\n"

    # Replace placeholders with actual values
    return format_str.replace("{call_id}", call_id)


# Add file handler with custom formatter
logger.add(
    f"{log_directory}/pipecat.log",
    rotation="15 day",
    retention="30 days",
    level="DEBUG",
    format=formatter,
    mode="a",
    catch=True,
)

# Add console handler for development environment
if ENVIRONMENT.lower() == "development":
    # Add console handler
    logger.add(
        sys.stderr,
        level="DEBUG",
        format=formatter,
        colorize=True,
        catch=True,
    )
# Add Loki handler if GRAFANA_HOST is set and not in development mode
elif GRAFANA_HOST:
    LOKI_URL = f"http://{GRAFANA_HOST}:3100/loki/api/v1/push"

    # Static labels
    static_labels = {"application": LOGGER_NAME, "environment": ENVIRONMENT}

    class CustomLoguruFormatter(LoguruFormatter):
        def format(self, record):
            try:
                result = super().format(record)

                if isinstance(result, tuple) and len(result) == 2:
                    formatted, loki_metadata = result
                else:
                    formatted = result
                    loki_metadata = {}

                original_message = formatted.get("message", "No message available")

                if formatted is None:
                    formatted = {}

                # Updated message format to include host IP
                formatted["message"] = (
                    f"{formatted.get('level', 'INFO'):<8} |"
                    f" [{formatted.get('call_id', 'unknown')}] |"
                    f" {formatted.get('name', 'unknown')}:{formatted.get('function', 'unknown')}:{formatted.get('line', '')} - "
                    f" {original_message}"
                )

                return formatted, loki_metadata
            except Exception as e:
                return {"message": f"Logging error: {str(e)}"}, {}

    # Define a custom formatter instance
    custom_formatter = CustomLoguruFormatter()

    # Configure the Loki handler - NOT using label_keys for environment
    loki_handler = LokiLoggerHandler(
        url=LOKI_URL,
        labels=static_labels,
        label_keys={},
        timeout=10,
        default_formatter=custom_formatter,
    )

    # Configure Loguru to send logs to Loki
    # logger.add(loki_handler, serialize=True, level="DEBUG", catch=True)

    logger.configure(
        handlers=[
            {
                "sink": loki_handler,
                "serialize": True,
                "level": "DEBUG",
                "catch": True,
                "enqueue": True,
            }
        ]
    )
else:
    # If not in development and no Grafana host, add a basic console handler
    # This ensures logs are visible somewhere
    logger.add(
        sys.stderr,
        level="INFO",  # Using INFO level for non-development environments
        format=formatter,
        colorize=True,
        catch=True,
    )

# Export these for use in other modules
__all__ = ["logger"]
