"""Authentication management for LiveJournal."""

import re
from typing import Optional, Union

from requests.structures import CaseInsensitiveDict

from yalje.core.config import YaljeConfig
from yalje.core.exceptions import AuthenticationError
from yalje.core.session import HTTPSession
from yalje.utils.logging import get_logger

logger = get_logger("auth")


class Authenticator:
    """Handles LiveJournal authentication flow."""

    def __init__(self, config: YaljeConfig):
        """Initialize authenticator.

        Args:
            config: Configuration object
        """
        self.config = config
        self.session: Optional[HTTPSession] = None

    def login(self, username: str, password: str) -> HTTPSession:
        """Perform login and return authenticated session.

        This follows the three-step LiveJournal authentication:
        1. GET homepage to acquire luid cookie
        2. POST login credentials with luid cookie
        3. Extract ljloggedin and ljmastersession cookies

        Args:
            username: LiveJournal username
            password: LiveJournal password

        Returns:
            Authenticated HTTPSession

        Raises:
            AuthenticationError: If authentication fails at any step
        """
        logger.info(f"Authenticating user: {username}")
        session = HTTPSession(self.config)

        # Acquire luid cookie
        logger.debug("Acquiring luid cookie")
        try:
            response = session.get(f"{self.config.base_url}/")
            luid = self._extract_cookie_from_response(response.headers, "luid")
            if not luid:
                raise AuthenticationError("Failed to acquire luid cookie")
            session.set_cookies({"luid": luid})
            logger.debug("luid cookie acquired")
        except Exception as e:
            logger.error(f"Failed to acquire luid cookie: {e}")
            raise AuthenticationError(f"Failed to acquire luid cookie: {e}") from e

        # Login with credentials
        logger.debug("Logging in with credentials")
        login_data = {
            "user": username,
            "password": password,
        }

        try:
            response = session.post(
                f"{self.config.base_url}/login.bml",
                data=login_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            logger.debug("Login request successful")
        except Exception as e:
            logger.error(f"Login request failed: {e}")
            raise AuthenticationError(f"Login request failed: {e}") from e

        # Extract session cookies
        logger.debug("Extracting session cookies")
        try:
            ljloggedin = self._extract_cookie_from_response(response.headers, "ljloggedin")
            ljmastersession = self._extract_cookie_from_response(
                response.headers, "ljmastersession"
            )

            if not ljloggedin or not ljmastersession:
                logger.error("Session cookies not found in response - invalid credentials?")
                raise AuthenticationError("Failed to acquire session cookies. Check credentials.")

            session.set_cookies(
                {
                    "ljloggedin": ljloggedin,
                    "ljmastersession": ljmastersession,
                }
            )
            logger.debug("Session cookies acquired")
        except Exception as e:
            logger.error(f"Failed to extract session cookies: {e}")
            raise AuthenticationError(f"Failed to extract session cookies: {e}") from e

        self.session = session
        logger.info(f"Authentication successful for user: {username}")
        return session

    def _extract_cookie_from_response(
        self, headers: Union[dict[str, str], CaseInsensitiveDict[str]], cookie_name: str
    ) -> Optional[str]:
        """Extract cookie value from Set-Cookie headers.

        Args:
            headers: Response headers
            cookie_name: Name of cookie to extract

        Returns:
            Cookie value or None if not found
        """
        set_cookie_headers = headers.get("Set-Cookie", "")
        if not set_cookie_headers:
            return None

        # Handle multiple Set-Cookie headers
        if isinstance(set_cookie_headers, str):
            cookie_strings = [set_cookie_headers]
        else:
            cookie_strings = set_cookie_headers

        for cookie_str in cookie_strings:
            if cookie_name in cookie_str:
                # Extract value between "cookie_name=" and ";"
                match = re.search(rf"{cookie_name}=([^;]+)", cookie_str)
                if match:
                    return match.group(1)

        return None

    def validate_session(self) -> bool:
        """Validate that the current session is still active.

        Returns:
            True if session is valid, False otherwise
        """
        if not self.session:
            return False

        try:
            # Test with a simple request
            response = self.session.get(f"{self.config.base_url}/inbox/")
            return response.status_code == 200
        except Exception:
            return False

    def logout(self) -> None:
        """Close the session and clear authentication."""
        if self.session:
            self.session.close()
            self.session = None
