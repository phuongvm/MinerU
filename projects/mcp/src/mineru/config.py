"""MinerU configuration tool for File to Markdown conversion service."""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Configuration
MINERU_API_BASE = os.getenv("MINERU_API_BASE", "https://mineru.net")
MINERU_API_KEY = os.getenv("MINERU_API_KEY", "")

# Local API Configuration
USE_LOCAL_API = os.getenv("USE_LOCAL_API", "").lower() in ["true", "1", "yes"]
LOCAL_MINERU_API_BASE = os.getenv("LOCAL_MINERU_API_BASE", "http://localhost:8080")

# Default output directory for converted files
DEFAULT_OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./downloads")


# Setup logging system
def setup_logging():
    """
    Setup logging system, configuring log level based on environment variables.

    Returns:
        logging.Logger: Configured logger.
    """
    # Get log level from environment variables
    log_level = os.getenv("MINERU_LOG_LEVEL", "INFO").upper()
    debug_mode = os.getenv("MINERU_DEBUG", "").lower() in ["true", "1", "yes"]

    # Override log_level if debug_mode is set
    if debug_mode:
        log_level = "DEBUG"

    # Ensure log_level is valid
    valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    if log_level not in valid_levels:
        log_level = "INFO"

    # Set log format
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Configure logging
    logging.basicConfig(level=getattr(logging, log_level), format=log_format)

    logger = logging.getLogger("mineru")
    logger.setLevel(getattr(logging, log_level))

    # Output log level info
    logger.info(f"Log level set to: {log_level}")

    return logger


# Create default logger
logger = setup_logging()


# Create output directory if it doesn't exist
def ensure_output_dir(output_dir=None):
    """
    Ensure output directory exists.

    Args:
        output_dir: Optional path for output directory. If None, uses DEFAULT_OUTPUT_DIR.

    Returns:
        Path object representing the output directory.
    """
    output_path = Path(output_dir or DEFAULT_OUTPUT_DIR)
    output_path.mkdir(parents=True, exist_ok=True)
    return output_path


# Validate API configuration
def validate_api_config():
    """
    Validate if required API configuration is set.

    Returns:
        dict: Configuration status.
    """
    return {
        "api_base": MINERU_API_BASE,
        "api_key_set": bool(MINERU_API_KEY),
        "output_dir": DEFAULT_OUTPUT_DIR,
    }
