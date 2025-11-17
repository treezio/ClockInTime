# ClockInTime for Factorial

A lightweight macOS menu bar application that automatically clocks in/out with Factorial HR when you login, logout, or put your Mac to sleep.

## Features

- 🚀 **Automatic Clock In**: Clocks in when you log into your Mac
- 🌙 **Automatic Clock Out**: Clocks out when you put your Mac to sleep
- � **Smart Scheduling**: Automatically skips weekends and holidays (reads from Factorial calendar)
- �🔒 **Secure Credentials**: Stores passwords securely in macOS Keychain
- 📊 **Status Display**: Shows current clock in/out status in menu bar
- 🎯 **Lightweight**: Runs in the background with minimal resource usage
- ⏰ **Uses Actual Time**: Clocks in/out with your actual login/sleep time

## Requirements

- macOS 10.14 (Mojave) or later
- Python 3.8 or later
- Factorial HR account

## Installation

### 1. Install Python Dependencies

```bash
# Clone or download this repository
cd ClockInTime

# Install required packages
pip3 install -r requirements.txt
```

### 2. Configure the Application

First time running the app, you'll be prompted to enter your Factorial credentials:

```bash
python3 clockintime_app.py
```

Your password will be stored securely in macOS Keychain.

### 3. Set Up Auto-Start (Optional but Recommended)

To have the app start automatically when you log in:

```bash
# Make the app executable
chmod +x clockintime_app.py

# Copy the launch agent plist to LaunchAgents directory
cp com.treezio.clockintime.plist ~/Library/LaunchAgents/

# Edit the plist file to update the path to your installation
nano ~/Library/LaunchAgents/com.treezio.clockintime.plist

# Update these lines with your actual paths:
# <string>/usr/local/bin/python3</string>
# <string>/Users/YOUR_USERNAME/workspace/treezio/ClockInTime/app.py</string>

# Load the launch agent
launchctl load ~/Library/LaunchAgents/com.treezio.clockintime.plist
```

## Usage

### Menu Bar Controls

Click the menu bar icon to access:

- **Status**: View current clock in/out status
- **Change Credentials**: Update your Factorial email/password
- **Quit**: Exit the application

The app will automatically:
- Clock in when you log into your Mac (if it's a working day)
- Clock out when you put your Mac to sleep
- Skip weekends and holidays based on your Factorial calendar
- Skip leave days configured in Factorial

### How It Determines Working Days

The app checks Factorial's calendar API to determine if today is a working day. It will skip:
- **Weekends**: Saturday and Sunday (unless configured as working days in Factorial)
- **Public Holidays**: Bank holidays and public holidays from your country
- **Leave Days**: Your personal leave/vacation days

This ensures you're never clocked in on days you shouldn't be working.

## How It Works

The application:

1. **Authentication**: Uses the Factorial web authentication flow (same as https://github.com/alejoar/factorialsucks)
   - Extracts CSRF token from login page
   - Authenticates with your credentials
   - Maintains session cookies

2. **Working Day Detection**: Checks Factorial's calendar API
   - Fetches your attendance calendar
   - Identifies weekends, holidays, and leave days
   - Only clocks in/out on actual working days

3. **System Event Monitoring**: Monitors macOS system events using PyObjC
   - Detects app startup (considered as login)
   - Monitors sleep notifications
   - Responds to system power events

4. **Clock In/Out**: Makes API calls to Factorial
   - Creates/updates shifts via the attendance API
   - Uses your actual login/sleep time
   - Handles existing shifts gracefully
   - Provides feedback via logs

## Configuration Files

- `~/.clockintime/config.json`: Application settings
- macOS Keychain: Encrypted password storage

## Troubleshooting

### "Not connected" status

1. Click "Change Credentials" from the menu
2. Re-enter your Factorial email and password
3. The app will attempt to reconnect

## Credits

Authentication flow inspired by [factorialsucks](https://github.com/alejoar/factorialsucks) by alejoar.

## License

MIT License - feel free to use and modify as needed.

## Contributing

Issues and pull requests are welcome!

## Disclaimer

This is an unofficial tool and is not affiliated with or endorsed by Factorial HR. Use at your own risk.
