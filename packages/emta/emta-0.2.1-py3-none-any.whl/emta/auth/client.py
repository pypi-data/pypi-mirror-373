"""Authentication client for Eastmoney API."""

import re
from typing import Any

import httpx
from loguru import logger

from ..models.exceptions import LoginError, ValidateKeyError
from ..utils.captcha import generate_random_number, recognize_captcha
from ..utils.encryption import encrypt_password

# Constants
LOGIN_URL = "https://jywg.18.cn/Login/Authentication?validatekey="
YZM_URL = "https://jywg.18.cn/Login/YZM?randNum="
BASE_HEADERS: dict[str, str] = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/114.0.0.0 Safari/537.36",
    "Origin": "https://jywg.18.cn",
    "Host": "jywg.18.cn",
}


class AuthClient:
    """Handles authentication with Eastmoney API"""

    def __init__(self, session: httpx.Client):
        """Initialize the authentication client.

        Args:
            session: HTTP client session
        """
        self.session = session
        self.random_code: float | None = None
        self.identify_code: str | None = None
        self.validate_key: str | None = None
        self.logger = logger

    def _get_validate_key(self) -> None:
        """Get validate key from Eastmoney login page.

        Raises:
            ValidateKeyError: If unable to retrieve validate key
        """
        url = "https://jywg.18.cn/Trade/Buy"
        try:
            response = self.session.get(url, headers=BASE_HEADERS)
            response.raise_for_status()

            match_result = re.findall(
                r'id="em_validatekey" type="hidden" value="(.*?)"', response.text
            )
            if match_result:
                self.validate_key = match_result[0].strip()
            else:
                raise ValidateKeyError("Unable to extract validate key from login page")
        except httpx.RequestError as e:
            raise ValidateKeyError(f"Failed to retrieve validate key: {e}")

    def _get_captcha(self) -> None:
        """Get random number and captcha code.

        Raises:
            LoginError: If unable to get captcha
        """
        try:
            random_num = generate_random_number()
            captcha_url = f"{YZM_URL}{random_num}"

            response = self.session.get(captcha_url, headers=BASE_HEADERS, timeout=60)
            response.raise_for_status()

            captcha_code: str = recognize_captcha(response.content)
            logger.info(captcha_code)
            if captcha_code:
                self.random_code = random_num
                self.identify_code = captcha_code
            else:
                raise LoginError("Failed to recognize captcha")
        except httpx.RequestError as e:
            raise LoginError(f"Failed to retrieve captcha: {e}")
        except Exception as e:
            raise LoginError(f"Failed to process captcha: {e}")

    def login(
        self,
        username: str,
        password: str,
        duration: int = 30,
    ) -> tuple[bool, dict[str, Any]]:
        """Login to Eastmoney account

        Args:
            username: Eastmoney account username
            password: Eastmoney account password
            duration: Eastmoney account login session duration in minutes (default: 30 minutes)

        Returns:
            Tuple of (success status, response data)

        Raises:
            LoginError: If login fails due to network or authentication issues
        """

        try:
            logger.info(f"Logging in user: {username}")

            # Prepare login request
            self._get_captcha()
            headers = BASE_HEADERS.copy()
            headers["X-Requested-With"] = "XMLHttpRequest"
            headers["Referer"] = (
                "https://jywg.18.cn/Login?el=1&clear=&returl=%2fTrade%2fBuy"
            )
            headers["Content-Type"] = "application/x-www-form-urlencoded"

            encrypted_password = encrypt_password(password.strip())

            data = {
                "userId": username.strip(),
                "password": encrypted_password,
                "randNumber": self.random_code,
                "identifyCode": self.identify_code,
                "duration": duration,
                "authCode": "",
                "type": "Z",
                "secInfo": "",
            }

            login_response = self.session.post(LOGIN_URL, headers=headers, data=data)
            login_response.raise_for_status()

            # Check login result
            result = login_response.json()
            if result.get("Status") == 0:
                logger.info("Login successful")
                self._get_validate_key()
                return True, result
            else:
                error_msg = result.get("Message", "Unknown error")
                logger.error(f"Login failed: {error_msg}")
                return False, result

        except LoginError:
            raise
        except httpx.RequestError as e:
            raise LoginError(f"Network error during login: {e}")
        except Exception as e:
            raise LoginError(f"Unexpected error during login: {e}")

    def logout(self) -> None:
        """Clear authentication data"""
        self.validate_key = None
        logger.info("Logged out successfully")
