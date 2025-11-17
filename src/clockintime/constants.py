"""
Application constants and configuration defaults.
"""

# Application metadata
APP_NAME = "ClockInTime"
APP_VERSION = "1.0.0"
APP_AUTHOR = "treezio"

# Factorial API
FACTORIAL_BASE_URL = "https://api.factorialhr.com"
FACTORIAL_SERVICE_NAME = "ClockInTime-Factorial"

# Workday settings
DEFAULT_WORKDAY_HOURS = 8
UPDATE_INTERVAL_SECONDS = 60  # Status update frequency

# Timing
LOGIN_EVENT_DELAY_SECONDS = 3
INITIAL_STATUS_UPDATE_DELAY_SECONDS = 2

# Icons and UI
DEFAULT_ICON = "⏰"
ICON_NON_WORKING_DAY = "🏖️"
ICON_COMPLETED = "✅"
ICON_OVERTIME = "💪"
ICON_WARNING = "⚠️"
ICON_ERROR = "❌"
