"""
py2app setup script for ClockInTime
"""

import sys
from pathlib import Path
from setuptools import setup

# Add src to path so clockintime package can be found
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

APP = ['clockintime_app.py']
DATA_FILES = [
    ('', ['icon.png']),  # Include icon if you have one
]
OPTIONS = {
    'argv_emulation': False,
    'packages': [
        'rumps',
        'requests',
        'urllib3',
        'certifi',
        'charset_normalizer',
        'idna',
        'clockintime'
    ],
    'iconfile': 'icon.png',  # Optional: create an .icns file
    'site_packages': True,
    'includes': [
        'AppKit',
        'Foundation',
        'objc',
        'PyObjCTools',
        'clockintime',
        'clockintime.api',
        'clockintime.api.factorial_client',
        'clockintime.services',
        'clockintime.services.event_monitor',
        'clockintime.ui',
        'clockintime.ui.menu_bar_app',
        'clockintime.utils',
        'clockintime.utils.config',
        'clockintime.utils.time_utils',
    ],
    'plist': {
        'CFBundleName': 'ClockInTime',
        'CFBundleDisplayName': 'ClockInTime',
        'CFBundleIdentifier': 'com.treezio.clockintime',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'LSUIElement': True,  # Run as menu bar app without dock icon
        'NSHumanReadableCopyright': '© 2025 Treezio',
        'NSPrincipalClass': 'NSApplication',
    },
}

setup(
    name='ClockInTime',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    package_dir={'': 'src'},
    packages=['clockintime', 'clockintime.api', 'clockintime.services', 'clockintime.ui', 'clockintime.utils'],
)
