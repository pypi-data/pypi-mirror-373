import logging
import os

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string

from .formatters import DEFAULT_FORMATTER, FormattingError

logger = logging.getLogger("windowsauthtoken")

_IGNORE_PYWIN32_ERRORS = os.getenv("WINDOWSAUTHTOKEN_IGNORE_PYWIN32_ERRORS", "false") == "true"
"""Flag to ignore platform-specific errors, useful for non-Windows environments."""

try:  # pragma: no cover
    import pywintypes
    import win32api
    import win32security
except ImportError:
    if _IGNORE_PYWIN32_ERRORS:  # pragma: no cover
        logger.warning("pywin32 is not installed, but errors are being ignored.")
    pywintypes = None
    win32api = None
    win32security = None


class WindowsAuthTokenMiddleware:
    """
    Middleware to handle Windows Authentication Tokens and convert them to a `REMOTE_USER` environment variable.
    """

    sync_capable = True

    header_name = "X-IIS-WindowsAuthToken"
    """The HTTP header name where the Windows Authentication Token is expected."""

    def __init__(self, get_response):
        self.get_response = get_response
        self.username_formatter: str = getattr(settings, "WINDOWSAUTHTOKEN_USERNAME_FORMATTER", DEFAULT_FORMATTER)

        if not any([win32security, pywintypes, win32api]) and not _IGNORE_PYWIN32_ERRORS:
            raise ImproperlyConfigured("pywin32 is required for Windows Authentication Token middleware.'")

    def __call__(self, request):
        auth_token = request.headers.get(self.header_name, "")
        if auth_token:
            try:
                username, domain = self.retrieve_auth_user_details(auth_token)
            except ValueError as err:
                logger.warning(f"Cannot retrieve username from auth token: {err}")
                username = None
                domain = None
        else:
            username = None
            domain = None

        if username is not None and domain is not None:
            try:
                formatted_user = self.format_username(username, domain)
            except FormattingError as err:
                logger.warning(f"Username formatter raised an error: {err} {username=} {domain=}")
                formatted_user = None
        else:
            formatted_user = None

        if formatted_user is not None:
            # Set the REMOTE_USER environment variable
            request.META["REMOTE_USER"] = formatted_user
            # In async contexts, there is no environment variable, so we set it in META as a HTTP header,
            # just like the RemoteUserMiddleware expects it for async requests.
            request.META["HTTP_REMOTE_USER"] = formatted_user
            # Save the original auth results for reference
            request.META["WINDOWSAUTHTOKEN_USER"] = username
            request.META["WINDOWSAUTHTOKEN_DOMAIN"] = domain

            logger.debug(f"Set REMOTE_USER to {formatted_user}")

        return self.get_response(request)

    @staticmethod
    def retrieve_auth_user_details(auth_token: str) -> tuple[str, str]:
        """
        Retrieve the user details for the Windows Authentication Token.

        Uses pywin32 to access the hosts' API to extract the username and domain for the token.

        Args:
            auth_token (str): The Windows Authentication Token.
        Returns:
            tuple[str, str]: A tuple containing the username and domain.
        Raises:
            ValueError: If the token is invalid or cannot be processed.
        """
        if not any([win32security, pywintypes, win32api]) and not _IGNORE_PYWIN32_ERRORS:
            raise ImproperlyConfigured("pywin32 is required for Windows Authentication Token middleware.'")

        try:
            token_handle = int(auth_token, 16)
        except ValueError:
            raise ValueError("Invalid token format.")

        try:
            # See https://learn.microsoft.com/en-us/windows/win32/api/winnt/ne-winnt-token_information_class
            token_information_class = 1
            security_id, _ = win32security.GetTokenInformation(token_handle, token_information_class)
            logger.debug(f"Retrieved security ID for auth token: {auth_token=} {token_handle=} {security_id=}")
        except pywintypes.error as err:
            raise ValueError(f"Can't retrieve Security ID for token: {err}")
        finally:
            # Always try to close the token handle, but ignore any issues with it
            try:
                win32api.CloseHandle(token_handle)
            except pywintypes.error as err:
                logger.warning(f"Failed to close token handle: {err}")
                pass

        try:
            user, domain, account_type = win32security.LookupAccountSid(None, security_id)
            logger.debug(f"Retrieved account details for SID: {security_id=} {user=} {domain=} {account_type=}")
        except (pywintypes.error, TypeError) as err:
            # TypeError can occur if the SID has an incorrect type
            raise ValueError(f"Can't retrieve account details for SID: {err}")

        return user, domain

    def format_username(self, user: str, domain: str) -> str:
        """
        Format the username using the configured formatter.

        Args:
            user (str): The username.
            domain (str): The domain.
        Returns:
            str: The formatted username.
        Raises:
            FormattingError: If the formatter raises an error.
        """
        formatter = import_string(self.username_formatter)
        return formatter(user, domain)
