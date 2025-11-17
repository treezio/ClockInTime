#!/usr/bin/env python3
"""
ClockInTime - Automatic Factorial clock in/out for macOS

A lightweight menu bar application that automatically clocks in when you
log into your Mac and clocks out when you log out or put it to sleep.
"""

import sys
import logging
from typing import Optional

from PyQt5.QtWidgets import (
    QApplication, QSystemTrayIcon, QMenu, QAction, 
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
)
from PyQt5.QtCore import QTimer

from clockintime.api.factorial_client import FactorialClient
from clockintime.exceptions import APIError, AuthenticationError
from clockintime.utils.config import Config
from clockintime.utils.time_utils import calculate_remaining_hours, format_remaining_time, format_time_display
from clockintime.services.event_monitor import MacEventMonitor, LoginEventDetector
from clockintime.constants import (
    UPDATE_INTERVAL_SECONDS,
    LOGIN_EVENT_DELAY_SECONDS,
    ICON_NON_WORKING_DAY,
    ICON_COMPLETED,
    ICON_OVERTIME,
    ICON_WARNING,
    ICON_ERROR
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CredentialsDialog(QDialog):
    """Dialog for entering Factorial credentials"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Factorial Credentials")
        self.setModal(True)
        
        layout = QVBoxLayout()
        
        # Email field
        layout.addWidget(QLabel("Email:"))
        self.email_input = QLineEdit()
        layout.addWidget(self.email_input)
        
        # Password field
        layout.addWidget(QLabel("Password:"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)
        
        # Buttons
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        layout.addWidget(self.save_button)
        layout.addWidget(self.cancel_button)
        
        self.setLayout(layout)
    
    def get_credentials(self):
        """Return entered credentials"""
        return self.email_input.text(), self.password_input.text()
    
    def set_email(self, email: str):
        """Pre-fill email field"""
        self.email_input.setText(email)


class ClockInTimeApp:
    """Main application class"""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        
        self.config = Config()
        self.factorial_client: Optional[FactorialClient] = None
        self.event_monitor = MacEventMonitor()
        self.login_detector = LoginEventDetector()
        
        # Setup UI
        self.setup_tray_icon()
        
        # Setup event handlers
        self.event_monitor.on_sleep(self.handle_sleep)
        self.event_monitor.on_wake(self.handle_wake)
        self.login_detector.on_login(self.handle_login)
        
        # Status update timer
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(UPDATE_INTERVAL_SECONDS * 1000)  # Convert to milliseconds
        
        # Start monitoring
        self.event_monitor.start()
        
        # Check credentials and login
        if self.config.has_credentials():
            self.login_to_factorial()
        else:
            self.show_credentials_dialog()
        
        # Trigger login event after a short delay
        QTimer.singleShot(LOGIN_EVENT_DELAY_SECONDS * 1000, self.login_detector.detect_login)
    
    def setup_tray_icon(self):
        """Setup system tray icon and menu"""
        # Create menu first
        self.menu = QMenu()
        
        # Status
        self.status_action = QAction("Status: Initializing...")
        self.status_action.setEnabled(False)
        self.menu.addAction(self.status_action)
        
        self.menu.addSeparator()
        
        # Credentials
        self.credentials_action = QAction("Change Credentials...")
        self.credentials_action.triggered.connect(self.show_credentials_dialog)
        self.menu.addAction(self.credentials_action)
        
        self.menu.addSeparator()
        
        # Quit
        self.quit_action = QAction("Quit")
        self.quit_action.triggered.connect(self.quit)
        self.menu.addAction(self.quit_action)
        
        # Create tray icon
        self.tray = QSystemTrayIcon(self.app)
        
        # Load icon from PNG file
        from PyQt5.QtGui import QIcon, QPixmap, QPainter, QFont
        from PyQt5.QtCore import Qt
        import os
        
        # Try to load custom icon from file
        icon_path = os.path.join(os.path.dirname(__file__), 'icon.png')
        
        if os.path.exists(icon_path):
            # Load from PNG file
            icon = QIcon(icon_path)
            logger.info("Loaded icon from: %s", icon_path)
        else:
            # Fallback: Create a clock icon using emoji/text
            logger.warning("icon.png not found, using emoji fallback")
            pixmap = QPixmap(64, 64)
            pixmap.fill(Qt.transparent)
            
            painter = QPainter(pixmap)
            painter.setFont(QFont('Arial', 48))
            painter.drawText(pixmap.rect(), Qt.AlignCenter, '🕐')
            painter.end()
            
            icon = QIcon(pixmap)
        
        self.tray.setIcon(icon)
        self.tray.setToolTip("ClockInTime - Initializing...")
        
        # Create status label for menu bar text (note: this may not work on all macOS versions)
        self.status_label = ""
        
        # Set the menu
        self.tray.setContextMenu(self.menu)
        
        # Make sure tray is visible
        self.tray.setVisible(True)
        
        # Also connect activated signal for left-click
        self.tray.activated.connect(self.tray_icon_activated)
    
    def tray_icon_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.Trigger:  # Left click
            self.menu.popup(self.tray.geometry().center())
    
    def login_to_factorial(self) -> bool:
        """Login to Factorial with stored credentials"""
        try:
            email = self.config.get_email()
            password = self.config.get_password()
            
            if not email or not password:
                logger.warning("No credentials stored")
                return False
            
            logger.info("Logging into Factorial...")
            self.factorial_client = FactorialClient(email, password)
            self.factorial_client.login()
            
            self.tray.setToolTip("ClockInTime - Connected")
            self.update_status()
            return True
            
        except (APIError, AuthenticationError) as e:
            logger.error("Failed to login: %s", str(e))
            self.show_error("Login Failed", f"Could not connect to Factorial.\n\n{str(e)}")
            return False
    
    def show_credentials_dialog(self):
        """Show dialog to enter credentials"""
        dialog = CredentialsDialog()
        
        # Pre-fill email if available
        email = self.config.get_email()
        if email:
            dialog.set_email(email)
        
        if dialog.exec_() == QDialog.Accepted:
            email, password = dialog.get_credentials()
            if email and password:
                # Save credentials
                self.config.set_email(email)
                self.config.set_password(email, password)
                
                # Try to login
                self.login_to_factorial()
    
    def show_error(self, title: str, message: str):
        """Show error message"""
        QMessageBox.critical(None, title, message)
    
    def update_status(self):
        """Update status display and tooltip with time information"""
        if not self.factorial_client:
            self.status_action.setText("Status: Not connected")
            self.tray.setToolTip("ClockInTime - Not connected")
            return
        
        try:
            # Check if today is a working day
            should_work, reason = self.factorial_client.should_work_today()
            
            if not should_work:
                # Not a working day
                self.status_action.setText(f"Status: {reason}")
                self.tray.setToolTip(f"{ICON_NON_WORKING_DAY} {reason}")
                return
            
            # It's a working day - check shift status
            has_shift, clock_in, clock_out = self.factorial_client.get_today_status()
            
            if has_shift:
                if clock_out:
                    # Already clocked out
                    status = f"Clocked: {clock_in} - {clock_out}"
                    self.tray.setToolTip(f"{ICON_COMPLETED} Done for today: {clock_in} - {clock_out}")
                else:
                    # Currently clocked in - calculate remaining hours
                    workday_hours = self.config.get_workday_hours()
                    remaining_hours = calculate_remaining_hours(clock_in, workday_hours)
                    
                    if remaining_hours > 0:
                        hours, minutes = format_remaining_time(remaining_hours)
                        time_str = format_time_display(hours, minutes)
                        status = f"Clocked in: {clock_in} ({time_str} left)"
                        self.tray.setToolTip(f"⏰ {time_str} remaining of {workday_hours}h workday")
                    else:
                        status = f"Clocked in: {clock_in} (overtime!)"
                        self.tray.setToolTip(f"{ICON_OVERTIME} Working overtime since {clock_in}")
            else:
                status = "Not clocked in today"
                self.tray.setToolTip(f"{ICON_WARNING} Ready to clock in (not clocked in yet)")

            self.status_action.setText(f"Status: {status}")

        except APIError as e:
            logger.error("Error fetching status: %s", str(e))
            self.status_action.setText("Status: Error fetching data")
            self.tray.setToolTip(f"{ICON_ERROR} Error fetching data")

    def handle_login(self):
        """Handle login event - clock in if it's a working day"""
        logger.info("Handling login event")
        
        if not self.factorial_client:
            logger.warning("Not connected to Factorial")
            return
        
        try:
            # Check if today is a working day
            should_work, reason = self.factorial_client.should_work_today()
            
            if not should_work:
                logger.info("Skipping clock in: %s", reason)
                self.tray.setToolTip(f"ClockInTime - {reason}")
                return
            
            # Clock in with current time
            if self.factorial_client.clock_in_now():
                logger.info("Auto clocked in on login")
                self.update_status()
            else:
                logger.error("Failed to auto clock in")
        except APIError as e:
            logger.error("Error during auto clock in: %s", str(e))
    
    def handle_sleep(self):
        """Handle sleep event - clock out"""
        logger.info("Handling sleep event")
        
        if not self.factorial_client:
            logger.warning("Not connected to Factorial")
            return
        
        try:
            # Check if we have an open shift
            has_shift, _, clock_out = self.factorial_client.get_today_status()
            
            if not has_shift or clock_out:
                logger.info("No open shift to clock out")
                return
            
            # Clock out with current time
            if self.factorial_client.clock_out_now():
                logger.info("Auto clocked out on sleep")
                self.update_status()
            else:
                logger.error("Failed to auto clock out")
        except APIError as e:
            logger.error("Error during auto clock out: %s", str(e))
    
    def handle_wake(self):
        """Handle wake event - clock in if it's a working day"""
        logger.info("Handling wake event")
        
        if not self.factorial_client:
            logger.warning("Not connected to Factorial")
            return
        
        try:
            # Check if today is a working day
            should_work, reason = self.factorial_client.should_work_today()
            
            if not should_work:
                logger.info("Skipping clock in: %s", reason)
                self.tray.setToolTip(f"ClockInTime - {reason}")
                return
            
            # Check if we already have a shift today
            has_shift, clock_in, clock_out = self.factorial_client.get_today_status()
            
            if has_shift and not clock_out:
                logger.info("Already clocked in at %s", clock_in)
                return
            
            # Clock in with current time
            if self.factorial_client.clock_in_now():
                logger.info("Auto clocked in on wake")
                self.update_status()
            else:
                logger.error("Failed to auto clock in")
        except APIError as e:
            logger.error("Error during auto clock in on wake: %s", str(e))
    
    def quit(self):
        """Quit the application"""
        logger.info("Quitting application")
        self.event_monitor.stop()
        self.app.quit()
    
    def run(self):
        """Run the application"""
        return self.app.exec_()


def main():
    """Main entry point"""
    app = ClockInTimeApp()
    sys.exit(app.run())


if __name__ == "__main__":
    main()