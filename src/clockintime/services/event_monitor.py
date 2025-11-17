"""
macOS system event monitoring for login, logout, and sleep/wake events.
"""

import logging
from typing import Callable, Optional

try:
    from AppKit import NSWorkspace
    # Sleep/wake notification constants
    NSWorkspaceWillSleepNotification = "NSWorkspaceWillSleepNotification"
    NSWorkspaceDidWakeNotification = "NSWorkspaceDidWakeNotification"
    PYOBJC_AVAILABLE = True
except ImportError:
    NSWorkspace = None
    NSWorkspaceWillSleepNotification = None
    NSWorkspaceDidWakeNotification = None
    PYOBJC_AVAILABLE = False

from clockintime.exceptions import SystemEventError

logger = logging.getLogger(__name__)


class MacEventMonitor:
    """
    Monitor macOS system events like sleep/wake.
    
    Uses PyObjC to register for NSWorkspace notifications.
    """
    
    def __init__(self):
        """Initialize the event monitor."""
        self.on_sleep_callback: Optional[Callable[[], None]] = None
        self.on_wake_callback: Optional[Callable[[], None]] = None
        self._observers = []
        
        if not PYOBJC_AVAILABLE:
            logger.error("PyObjC not available. System event monitoring will not work.")
    
    def on_sleep(self, callback: Callable[[], None]) -> None:
        """
        Register callback for sleep event.
        
        Args:
            callback: Function to call when system goes to sleep
        """
        self.on_sleep_callback = callback
    
    def on_wake(self, callback: Callable[[], None]) -> None:
        """
        Register callback for wake event.
        
        Args:
            callback: Function to call when system wakes up
        """
        self.on_wake_callback = callback
    
    def _sleep_notification(self, notification) -> None:
        """
        Called when system is going to sleep.
        
        Args:
            notification: NSNotification object
        """
        logger.info("System going to sleep")
        if self.on_sleep_callback:
            try:
                self.on_sleep_callback()
            except Exception as e:
                logger.error("Error in sleep callback: %s", e, exc_info=True)
    
    def _wake_notification(self, notification) -> None:
        """
        Called when system wakes up.
        
        Args:
            notification: NSNotification object
        """
        logger.info("System woke up")
        if self.on_wake_callback:
            try:
                self.on_wake_callback()
            except Exception as e:
                logger.error("Error in wake callback: %s", e, exc_info=True)
    
    def start(self) -> None:
        """
        Start monitoring system events.
        
        Raises:
            SystemEventError: If PyObjC is not available
        """
        if not PYOBJC_AVAILABLE:
            raise SystemEventError("Cannot start monitoring: PyObjC not available")

        workspace = NSWorkspace.sharedWorkspace()
        notification_center = workspace.notificationCenter()

        # Register for sleep notification
        notification_center.addObserver_selector_name_object_(
            self,
            'sleepNotification:',
            NSWorkspaceWillSleepNotification,
            None
        )

        # Register for wake notification
        notification_center.addObserver_selector_name_object_(
            self,
            'wakeNotification:',
            NSWorkspaceDidWakeNotification,
            None
        )
        logger.info("System event monitoring started")

    def sleepNotification_(self, notification) -> None:
        """
        Objective-C method called on sleep.
        
        Note: Underscore suffix converts to Objective-C selector format.
        
        Args:
            notification: NSNotification object
        """
        self._sleep_notification(notification)

    def wakeNotification_(self, notification) -> None:
        """
        Objective-C method called on wake.
        
        Note: Underscore suffix converts to Objective-C selector format.
        
        Args:
            notification: NSNotification object
        """
        self._wake_notification(notification)

    def stop(self) -> None:
        """Stop monitoring system events."""
        if not PYOBJC_AVAILABLE:
            return

        workspace = NSWorkspace.sharedWorkspace()
        notification_center = workspace.notificationCenter()
        notification_center.removeObserver_(self)
        logger.info("System event monitoring stopped")


class LoginEventDetector:
    """
    Detect login events by running at startup.
    
    Since macOS doesn't provide a direct login notification API,
    we consider the app starting as a login event.
    """

    def __init__(self):
        """Initialize the login detector."""
        self.on_login_callback: Optional[Callable[[], None]] = None
        self._login_detected = False

    def on_login(self, callback: Callable[[], None]) -> None:
        """
        Register callback for login event.
        
        Args:
            callback: Function to call when login is detected
        """
        self.on_login_callback = callback

    def detect_login(self) -> None:
        """
        Call this at app startup to trigger login event.
        
        This should be called once when the app starts.
        """
        if not self._login_detected:
            self._login_detected = True
            logger.info("Login detected (app started)")
            if self.on_login_callback:
                try:
                    self.on_login_callback()
                except Exception as e:
                    logger.error("Error in login callback: %s", e, exc_info=True)
