#!/usr/bin/env python3
"""
ClockInTime - Entry point for the application.
"""

import logging
import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from clockintime import APP_NAME, APP_VERSION
from clockintime.ui import ClockInTimeApp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Main entry point for ClockInTime application."""
    try:
        logger.info("%s v%s starting...", APP_NAME, APP_VERSION)
        app = ClockInTimeApp()
        logger.info("Application initialized successfully")
        app.run()
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.exception("Fatal error: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
