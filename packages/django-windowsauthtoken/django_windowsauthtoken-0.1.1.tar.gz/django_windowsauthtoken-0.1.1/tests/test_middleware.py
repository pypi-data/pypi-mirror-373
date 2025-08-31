import logging
import sys
from collections import namedtuple

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured

from django_windowsauthtoken.middleware import WindowsAuthTokenMiddleware


@pytest.fixture()
def mock_pywin32(mocker):
    """Fixture to mock pywin32 components used in the middleware."""
    mock_win32security = mocker.patch("django_windowsauthtoken.middleware.win32security")
    mock_win32api = mocker.patch("django_windowsauthtoken.middleware.win32api")
    mock_pywintypes = mocker.patch("django_windowsauthtoken.middleware.pywintypes")
    mock_pywintypes.error = Pywin32MockException

    # Return a namedtuple for easier access to the mocks
    pywin32_mock = namedtuple("pywin32_mock", ["win32security", "win32api", "pywintypes"])
    return pywin32_mock(mock_win32security, mock_win32api, mock_pywintypes)


def test_middleware_sets_remote_user(mocker, rf):
    mocker.patch(
        "django_windowsauthtoken.middleware.WindowsAuthTokenMiddleware.retrieve_auth_user_details",
        return_value=("testuser", "TESTDOMAIN"),
    )

    mock_get_response = mocker.Mock()
    middleware = WindowsAuthTokenMiddleware(mock_get_response)

    request = rf.get("/")
    request.headers = {"X-IIS-WindowsAuthToken": "valid_token"}
    request.META = {}

    response = middleware(request)

    assert response == mock_get_response.return_value

    assert request.META["REMOTE_USER"] == r"TESTDOMAIN\testuser"
    assert request.META["HTTP_REMOTE_USER"] == r"TESTDOMAIN\testuser"
    assert request.META["WINDOWSAUTHTOKEN_USER"] == "testuser"
    assert request.META["WINDOWSAUTHTOKEN_DOMAIN"] == "TESTDOMAIN"

    mock_get_response.assert_called_once_with(request)


def test_middleware_no_token(rf, mocker):
    mock_get_response = mocker.Mock()
    middleware = WindowsAuthTokenMiddleware(mock_get_response)

    request = rf.get("/")
    request.headers = {}
    request.META = {}

    response = middleware(request)

    assert response == mock_get_response.return_value
    assert "REMOTE_USER" not in request.META
    mock_get_response.assert_called_once_with(request)


def test_middleware_invalid_token(mocker, rf):
    mocker.patch(
        "django_windowsauthtoken.middleware.WindowsAuthTokenMiddleware.retrieve_auth_user_details",
        side_effect=ValueError("Invalid token"),
    )

    mock_get_response = mocker.Mock()
    middleware = WindowsAuthTokenMiddleware(mock_get_response)

    request = rf.get("/")
    request.headers = {"X-IIS-WindowsAuthToken": "invalid_token"}
    request.META = {}

    response = middleware(request)

    assert response == mock_get_response.return_value
    assert "REMOTE_USER" not in request.META
    mock_get_response.assert_called_once_with(request)


def test_retrieve_auth_user_details_invalid_token():
    with pytest.raises(ValueError) as excinfo:
        WindowsAuthTokenMiddleware.retrieve_auth_user_details("invalid_token")
    assert "Invalid token format" in str(excinfo.value)


class Pywin32MockException(Exception):
    """Mock exception to simulate pywin32 errors."""

    pass


def test_retrieve_auth_user_details_no_token_information(mock_pywin32):
    mock_pywin32.win32security.GetTokenInformation.side_effect = Pywin32MockException("No token information")

    with pytest.raises(ValueError) as excinfo:
        WindowsAuthTokenMiddleware.retrieve_auth_user_details("123")
    assert "Can't retrieve Security ID for token: No token information" in str(excinfo.value)

    mock_pywin32.win32security.GetTokenInformation.assert_called_once_with(291, 1)


def test_retrieve_auth_user_details_no_account(mock_pywin32):
    # GetTokenInformation returns a SID object and some integer value
    mock_pywin32.win32security.GetTokenInformation.return_value = ("mocked_sid", 0)
    mock_pywin32.win32security.LookupAccountSid.side_effect = Pywin32MockException("No account found")

    with pytest.raises(ValueError) as excinfo:
        WindowsAuthTokenMiddleware.retrieve_auth_user_details("123")
    assert "Can't retrieve account details for SID: No account found" in str(excinfo.value)

    mock_pywin32.win32security.GetTokenInformation.assert_called_once_with(291, 1)
    mock_pywin32.win32security.LookupAccountSid.assert_called_once_with(None, "mocked_sid")


def test_retrieve_auth_user_details_invalid_sid_object(mock_pywin32):
    # GetTokenInformation returns a SID object and some integer value
    mock_pywin32.win32security.GetTokenInformation.return_value = ("mocked_sid", 0)
    mock_pywin32.win32security.LookupAccountSid.side_effect = TypeError("Invalid SID object")

    with pytest.raises(ValueError) as excinfo:
        WindowsAuthTokenMiddleware.retrieve_auth_user_details("123")
    assert "Can't retrieve account details for SID: Invalid SID object" in str(excinfo.value)

    mock_pywin32.win32security.GetTokenInformation.assert_called_once_with(291, 1)
    mock_pywin32.win32security.LookupAccountSid.assert_called_once_with(None, "mocked_sid")


def test_retrieve_auth_user_details_success(mock_pywin32):
    # GetTokenInformation returns a SID object and some integer value
    mock_pywin32.win32security.GetTokenInformation.return_value = ("mocked_sid", 0)
    # LookupAccountSid returns a tuple of (username, domain, account_type)
    mock_pywin32.win32security.LookupAccountSid.return_value = (
        "testuser",
        "TESTDOMAIN",
        1,
    )

    username, domain = WindowsAuthTokenMiddleware.retrieve_auth_user_details("123")

    assert username == "testuser"
    assert domain == "TESTDOMAIN"

    mock_pywin32.win32security.GetTokenInformation.assert_called_once_with(291, 1)
    mock_pywin32.win32security.LookupAccountSid.assert_called_once_with(None, "mocked_sid")
    mock_pywin32.win32api.CloseHandle.assert_called_once()


def test_middleware_init_pywin32_error_handling(mocker):
    mocker.patch("django_windowsauthtoken.middleware._IGNORE_PYWIN32_ERRORS", False)
    mocker.patch("django_windowsauthtoken.middleware.win32security", None)
    mocker.patch("django_windowsauthtoken.middleware.pywintypes", None)
    mocker.patch("django_windowsauthtoken.middleware.win32api", None)

    mock_get_response = mocker.Mock()
    with pytest.raises(ImproperlyConfigured) as excinfo:
        WindowsAuthTokenMiddleware(mock_get_response)
    assert "pywin32 is required for Windows Authentication Token middleware." in str(excinfo.value)


def test_retrieve_auth_user_details_pywin32_error_handling(mocker):
    mocker.patch("django_windowsauthtoken.middleware._IGNORE_PYWIN32_ERRORS", False)
    mocker.patch("django_windowsauthtoken.middleware.win32security", None)
    mocker.patch("django_windowsauthtoken.middleware.pywintypes", None)
    mocker.patch("django_windowsauthtoken.middleware.win32api", None)

    with pytest.raises(ImproperlyConfigured) as excinfo:
        WindowsAuthTokenMiddleware.retrieve_auth_user_details("123")
    assert "pywin32 is required for Windows Authentication Token middleware." in str(excinfo.value)


@pytest.mark.skipif(sys.platform != "win32", reason="Requires Windows platform")
def test_retrieve_auth_user_details_nonexistent_token(mocker):
    """On Windows, a made up token should result in an actual GetTokenInformation error."""
    mocker.patch("django_windowsauthtoken.middleware._IGNORE_PYWIN32_ERRORS", False)

    with pytest.raises(ValueError) as excinfo:
        WindowsAuthTokenMiddleware.retrieve_auth_user_details("123")

    assert "Can't retrieve Security ID for token" in str(excinfo.value)
    # The error response from GetTokenInformation
    assert "The handle is invalid." in str(excinfo.value)


def test_format_username_default(mocker):
    mock_get_response = mocker.Mock()
    middleware = WindowsAuthTokenMiddleware(mock_get_response)
    formatted_username = middleware.format_username("testuser", "TESTDOMAIN")
    assert formatted_username == r"TESTDOMAIN\testuser"


def custom_formatter(user: str, domain: str) -> str:
    return f"{user}@{domain}.com"


def test_format_username_custom(mocker, settings):
    settings.WINDOWSAUTHTOKEN_USERNAME_FORMATTER = "test_middleware.custom_formatter"

    mock_get_response = mocker.Mock()
    middleware = WindowsAuthTokenMiddleware(mock_get_response)
    formatted_username = middleware.format_username("testuser", "TESTDOMAIN")
    assert formatted_username == "testuser@TESTDOMAIN.com"


def test_username_formatter_raises(mocker, caplog):
    mocker.patch(
        "django_windowsauthtoken.middleware.WindowsAuthTokenMiddleware.retrieve_auth_user_details",
        return_value=("testuser", ""),
    )
    caplog.set_level(logging.WARNING, logger="windowsauthtoken")

    mock_get_response = mocker.Mock()
    middleware = WindowsAuthTokenMiddleware(mock_get_response)

    request = mocker.Mock()
    request.headers = {"X-IIS-WindowsAuthToken": "valid_token"}
    request.META = {}

    middleware(request)

    assert "REMOTE_USER" not in request.META
    mock_get_response.assert_called_once_with(request)

    assert "Domain and user cannot be empty." in caplog.text


@pytest.mark.django_db
def test_combine_with_remote_user_middleware(mocker, settings, client):
    mocker.patch(
        "django_windowsauthtoken.middleware.WindowsAuthTokenMiddleware.retrieve_auth_user_details",
        return_value=("testuser", "TESTDOMAIN"),
    )

    settings.MIDDLEWARE = [
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django_windowsauthtoken.middleware.WindowsAuthTokenMiddleware",
        "django.contrib.auth.middleware.RemoteUserMiddleware",
    ]
    settings.AUTHENTICATION_BACKENDS = [
        "django.contrib.auth.backends.RemoteUserBackend",
    ]
    settings.WINDOWSAUTHTOKEN_USERNAME_FORMATTER = "django_windowsauthtoken.formatters.format_email_like"

    User = get_user_model()
    assert User.objects.count() == 0

    response = client.get("/", headers={"X-IIS-WindowsAuthToken": "valid_token"})

    assert response.status_code == 200
    assert response.wsgi_request.META["REMOTE_USER"] == "testuser@TESTDOMAIN"
    assert response.wsgi_request.user.is_authenticated is True

    assert User.objects.count() == 1, "User should be created by RemoteUserMiddleware"
    user = User.objects.first()
    assert user == response.wsgi_request.user
    assert user.username == "testuser@TESTDOMAIN"


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_combine_with_remote_user_middleware_async(mocker, settings, async_client):
    mocker.patch(
        "django_windowsauthtoken.middleware.WindowsAuthTokenMiddleware.retrieve_auth_user_details",
        return_value=("testuser", "TESTDOMAIN"),
    )

    settings.MIDDLEWARE = [
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django_windowsauthtoken.middleware.WindowsAuthTokenMiddleware",
        "django.contrib.auth.middleware.RemoteUserMiddleware",
    ]
    settings.AUTHENTICATION_BACKENDS = [
        "django.contrib.auth.backends.RemoteUserBackend",
    ]
    settings.WINDOWSAUTHTOKEN_USERNAME_FORMATTER = "django_windowsauthtoken.formatters.format_email_like"

    User = get_user_model()
    assert await User.objects.acount() == 0

    response = await async_client.get("/", headers={"X-IIS-WindowsAuthToken": "valid_token"})

    assert response.status_code == 200
    assert response.asgi_request.META["HTTP_REMOTE_USER"] == "testuser@TESTDOMAIN"
    assert response.asgi_request.user.is_authenticated is True

    assert await User.objects.acount() == 1, "User should be created by RemoteUserMiddleware"
    user = await User.objects.afirst()
    assert user == response.asgi_request.user
    assert user.username == "testuser@TESTDOMAIN"
