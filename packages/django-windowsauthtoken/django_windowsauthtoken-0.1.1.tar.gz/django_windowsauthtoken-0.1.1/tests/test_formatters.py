import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from django_windowsauthtoken.formatters import (
    FormattingError,
    format_domain_user,
    format_email_like,
    format_username_only,
)

User = get_user_model()


def test_format_domain_user():
    assert format_domain_user("testuser", "TESTDOMAIN") == r"TESTDOMAIN\testuser"


def test_format_domain_user_empty_domain():
    with pytest.raises(FormattingError):
        format_domain_user("testuser", "")


def test_format_domain_user_empty_user():
    with pytest.raises(FormattingError):
        format_domain_user("", "TESTDOMAIN")


def test_format_domain_user_both_empty():
    with pytest.raises(FormattingError):
        format_domain_user("", "")


def testformat_username_only():
    assert format_username_only("testuser", "TESTDOMAIN") == "testuser"


def test_format_username_only_empty_user():
    with pytest.raises(FormattingError):
        format_username_only("", "TESTDOMAIN")


def test_format_username_only_empty_domain():
    assert format_username_only("testuser", "") == "testuser"


def test_format_username_only_both_empty():
    with pytest.raises(FormattingError):
        format_username_only("", "")


def test_format_email_like():
    assert format_email_like("testuser", "TESTDOMAIN") == "testuser@TESTDOMAIN"


def test_format_email_like_empty_user():
    with pytest.raises(FormattingError):
        format_email_like("", "TESTDOMAIN")


def test_format_email_like_empty_domain():
    with pytest.raises(FormattingError):
        format_email_like("testuser", "")


def test_format_email_like_both_empty():
    with pytest.raises(FormattingError):
        format_email_like("", "")


@pytest.mark.django_db
def test_format_domain_user_incompatible_with_django_user_model():
    formatted_username = format_domain_user("testuser", "TESTDOMAIN")
    user = User.objects.create_user(username=formatted_username)
    with pytest.raises(ValidationError) as excinfo:
        user.full_clean()
    assert "Enter a valid username" in str(excinfo.value)


@pytest.mark.django_db
def test_format_username_only_compatible_with_django_user_model():
    formatted_username = format_username_only("testuser", "TESTDOMAIN")
    user = User.objects.create_user(username=formatted_username)
    assert user.full_clean() is None


@pytest.mark.django_db
def test_format_email_like_compatible_with_django_user_model():
    formatted_username = format_email_like("testuser", "TESTDOMAIN")
    user = User.objects.create_user(username=formatted_username)
    assert user.full_clean() is None
