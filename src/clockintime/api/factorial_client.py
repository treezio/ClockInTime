"""
Factorial API client for clock in/out operations.
Based on the authentication flow from https://github.com/alejoar/factorialsucks
"""

import logging
import re
from datetime import datetime
from typing import Optional, Tuple

import requests

from clockintime.constants import FACTORIAL_BASE_URL
from clockintime.exceptions import APIError, AuthenticationError

logger = logging.getLogger(__name__)


class FactorialClient:
    """
    Client for interacting with the Factorial HR API.

    Handles authentication, session management, and attendance operations.
    """

    def __init__(self, email: str, password: str):
        """
        Initialize Factorial API client.

        Args:
            email: Factorial account email
            password: Factorial account password
        """
        self.email = email
        self.password = password
        self.base_url = FACTORIAL_BASE_URL
        self.session = requests.Session()
        self.employee_id: Optional[int] = None
        self.period_id: Optional[int] = None
        self._logged_in = False

    def login(self) -> bool:
        """
        Authenticate with Factorial using email and password.

        Returns:
            True if successful

        Raises:
            AuthenticationError: If login fails
            APIError: If network or API error occurs
        """
        try:
            # Step 1: Get the sign-in page to extract CSRF token
            logger.info("Fetching CSRF token...")
            response = self.session.get(f"{self.base_url}/users/sign_in")
            response.raise_for_status()

            # Extract CSRF token from meta tag
            csrf_match = re.search(r'<meta name="csrf-token" content="([^"]+)"', response.text)
            if not csrf_match:
                raise AuthenticationError("Could not extract CSRF token")

            csrf_token = csrf_match.group(1)
            logger.info("CSRF token extracted successfully")

            # Step 2: Submit login form
            login_data = {
                "authenticity_token": csrf_token,
                "return_host": "factorialhr.es",
                "user[email]": self.email,
                "user[password]": self.password,
                "user[remember_me]": "0",
                "commit": "Sign in"
            }

            logger.info("Submitting login credentials...")
            response = self.session.post(
                f"{self.base_url}/users/sign_in",
                data=login_data
            )
            response.raise_for_status()

            # Check for login errors
            error_match = re.search(r'<div class="flash flash--wrong">([^<]+)</div>', response.text)
            if error_match:
                error_msg = error_match.group(1).strip()
                raise AuthenticationError(f"Login failed: {error_msg}")

            self._logged_in = True
            logger.info("Login successful")

            # Get current period info
            self._set_period_id()

            return True

        except requests.RequestException as e:
            raise APIError(f"Network error during login: {e}")

    def _set_period_id(self) -> None:
        """
        Get the current period ID and employee ID.

        Raises:
            APIError: If period data cannot be fetched
        """
        try:
            now = datetime.now()
            year = now.year
            month = now.month

            logger.info("Fetching period data for %d/%d...", year, month)
            response = self.session.get(
                f"{self.base_url}/attendance/periods",
                params={"year": year, "month": month}
            )
            response.raise_for_status()

            periods = response.json()
            for period in periods:
                if period.get("year") == year and period.get("month") == month:
                    self.employee_id = period.get("employee_id")
                    self.period_id = period.get("id")
                    logger.info("Period ID: %d, Employee ID: %d", self.period_id, self.employee_id)
                    return

            raise APIError(f"Could not find period for {year}/{month}")

        except requests.RequestException as e:
            raise APIError(f"Error fetching period data: {e}")

    def _ensure_logged_in(self) -> None:
        """
        Ensure the client is logged in.

        Raises:
            AuthenticationError: If not logged in
        """
        if not self._logged_in:
            raise AuthenticationError("Not logged in. Call login() first.")

    def clock_in_now(self, clock_in_time: Optional[str] = None) -> bool:
        """
        Clock in for today using the toggle clock endpoint.

        Args:
            clock_in_time: Time in HH:MM format. If None, uses current time.

        Returns:
            True if successful

        Raises:
            AuthenticationError: If not logged in
            APIError: If clock in fails
        """
        self._ensure_logged_in()

        now = datetime.now()
        if clock_in_time is None:
            clock_in_time = now.strftime("%H:%M")

        try:
            logger.info("Clocking in at %s...", clock_in_time)

            response = self.session.post(
                f"{self.base_url}/api/2025-10-01/resources/attendance/shifts/clock_in",
                params={"now": f"{now.strftime('%Y-%m-%d')}T{clock_in_time}:00"},
                headers={"Content-Type": "application/json"}
            )

            if response.status_code in [200, 201]:
                logger.info("Successfully clocked in at %s", clock_in_time)
                return True

            logger.error("Clock in failed: %d - %s", response.status_code, response.text)
            return False

        except requests.RequestException as e:
            raise APIError(f"Error during clock in: {e}")

    def clock_out_now(self, clock_out_time: Optional[str] = None) -> bool:
        """
        Clock out for today using the toggle clock endpoint.

        Args:
            clock_out_time: Time in HH:MM format. If None, uses current time.

        Returns:
            True if successful

        Raises:
            AuthenticationError: If not logged in
            APIError: If clock out fails
        """
        self._ensure_logged_in()

        now = datetime.now()
        if clock_out_time is None:
            clock_out_time = now.strftime("%H:%M")

        try:
            logger.info("Clocking out at %s...", clock_out_time)

            response = self.session.post(
                f"{self.base_url}/api/2025-10-01/resources/attendance/shifts/clock_out",
                params={"now": f"{now.strftime('%Y-%m-%d')}T{clock_out_time}:00"},
                headers={"Content-Type": "application/json"}
            )

            if response.status_code in [200, 201]:
                logger.info("Successfully clocked out at %s", clock_out_time)
                return True

            logger.error("Clock out failed: %d - %s", response.status_code, response.text)
            return False

        except requests.RequestException as e:
            raise APIError(f"Error during clock out: {e}")

    def should_work_today(self) -> Tuple[bool, str]:
        """
        Check if today is a working day (not weekend, not holiday, not leave).

        Returns:
            Tuple of (should_work, reason)
            - should_work: True if it's a working day
            - reason: Description (e.g., "Working day", "Leave day: Vacation")

        Raises:
            AuthenticationError: If not logged in
            APIError: If calendar data cannot be fetched
        """
        self._ensure_logged_in()

        try:
            now = datetime.now()

            # Get calendar data for current month
            response = self.session.get(
                f"{self.base_url}/attendance/calendar",
                params={
                    "id": self.employee_id,
                    "year": now.year,
                    "month": now.month
                }
            )
            response.raise_for_status()

            calendar_days = response.json()

            # Find today in calendar
            for day_info in calendar_days:
                if day_info.get("day") == now.day:
                    # Check if it's a leave day
                    if day_info.get("is_leave"):
                        leave_name = day_info.get("leave_name", "Leave")
                        return (False, f"Leave day: {leave_name}")

                    # Check if it's a working day (laborable)
                    if not day_info.get("is_laborable"):
                        # Get day name or holiday name
                        date_str = day_info.get("date", "")
                        if date_str:
                            day_name = datetime.strptime(date_str, "%Y-%m-%d").strftime("%A")
                            return (False, f"Non-working day: {day_name}")
                        return (False, "Non-working day (weekend or holiday)")

                    # It's a working day
                    return (True, "Working day")

            # If not found in calendar, assume it's a working day
            logger.warning("Today not found in calendar, assuming working day")
            return (True, "Working day (assumed)")

        except requests.RequestException as e:
            raise APIError(f"Error fetching calendar: {e}")

    def get_today_status(self) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Get today's clock in/out status.

        Returns:
            Tuple of (has_shift, clock_in_time, clock_out_time)
            - has_shift: True if there's a shift for today
            - clock_in_time: Time in HH:MM format or None
            - clock_out_time: Time in HH:MM format or None

        Raises:
            AuthenticationError: If not logged in
            APIError: If status cannot be fetched
        """
        self._ensure_logged_in()

        try:
            now = datetime.now()
            response = self.session.get(
                f"{self.base_url}/attendance/shifts",
                params={
                    "employee_id": self.employee_id,
                    "year": now.year,
                    "month": now.month
                }
            )
            response.raise_for_status()

            shifts = response.json()

            for shift in shifts:
                if shift.get("day") == now.day:
                    return (True, shift.get("clock_in"), shift.get("clock_out"))

            return (False, None, None)

        except requests.RequestException as e:
            raise APIError(f"Error fetching status: {e}")
