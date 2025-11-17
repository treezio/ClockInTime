# ClockInTime - Project Structure Documentation

## Overview

This document describes the refactored project structure. The codebase has been reorganized into a modular, maintainable architecture.

## Directory Structure

```
ClockInTime/
├── src/clockintime/              # Main package
│   ├── __init__.py               # Package exports
│   ├── constants.py              # Application constants
│   ├── exceptions.py             # Custom exception hierarchy
│   │
│   ├── api/                      # API clients
│   │   ├── __init__.py
│   │   └── factorial_client.py   # Factorial HR API client
│   │
│   ├── services/                 # Business logic
│   │   ├── __init__.py
│   │   └── event_monitor.py      # macOS system event monitoring
│   │
│   ├── ui/                       # User interface
│   │   ├── __init__.py
│   │   └── menu_bar_app.py       # pyqt-based menu bar app
│   │
│   └── utils/                    # Utilities
│       ├── __init__.py
│       ├── config.py              # Configuration & credentials
│       └── time_utils.py          # Time calculations
│
├── clockintime_app.py            # Entry point
├── requirements.txt              # Dependencies
├── install.sh                    # Installation script
├── com.treezio.clockintime.plist # LaunchAgent config
└── README.md                     # User documentation
```

## Module Descriptions

### `clockintime/constants.py`
- Application metadata (name, version)
- API URLs and service names
- Default configuration values
- UI icons and display constants

### `clockintime/exceptions.py`
- Custom exception hierarchy
- `ClockInTimeError` (base)
- `APIError`, `AuthenticationError`
- `ConfigurationError`, `SystemEventError`

### `clockintime/api/factorial_client.py`
- Factorial HR API client
- CSRF-based authentication
- Shift management (clock in/out)
- Calendar and period data fetching
- Session management

### `clockintime/services/event_monitor.py`
- macOS system event monitoring via PyObjC
- Sleep/wake notifications
- Login detection
- Callback-based event handling

### `clockintime/ui/menu_bar_app.py`
- pyqt-based menu bar application
- Real-time status display
- Credential management dialogs
- Event handler orchestration

### `clockintime/utils/config.py`
- Configuration file management (~/.clockintime/config.json)
- macOS Keychain integration for passwords
- Workday hours configuration

### `clockintime/utils/time_utils.py`
- Time calculation utilities
- Worked hours calculation
- Remaining hours formatting
- Display string generation

## Running the Application

### Development Mode
```bash
cd /Users/lfernandez/workspace/treezio/ClockInTime
./venv/bin/python clockintime_app.py
```

### Production Mode
```bash
# Install as LaunchAgent
launchctl load ~/Library/LaunchAgents/com.treezio.clockintime.plist
```

## Dependencies

- **pyqt5** (5.15.0+)
- **requests** (2.31.0+): HTTP client for API calls
- **keyring** (24.0.0+): Secure credential storage
- **pyobjc** (12.0+): Python-Objective-C bridge
- **pyobjc-framework-Cocoa** (10.0+): macOS frameworks

## Configuration

### Application Settings
Location: `~/.clockintime/config.json`
```json
{
  "email": "user@example.com",
  "workday_hours": 8
}
```

### Credentials
Stored in macOS Keychain under service name: `ClockInTime-Factorial`

## Future Enhancements

Potential areas for improvement:

1. **Testing**
   - Unit tests for all modules
   - Integration tests for API client
   - Mock-based testing for system events

2. **Configuration UI**
   - Settings panel in menu bar
   - Workday hours adjustment
   - Notification preferences

3. **Notifications**
   - macOS notifications for clock in/out
   - Error notifications
   - Daily summary

4. **Logging**
   - Configurable log levels
   - Log file rotation
   - Remote logging support

5. **Analytics**
   - Work hours tracking
   - Overtime calculations
   - Weekly/monthly reports