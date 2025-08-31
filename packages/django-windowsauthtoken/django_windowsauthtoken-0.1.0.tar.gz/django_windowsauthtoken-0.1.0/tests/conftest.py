import os

from django.conf import settings


def pytest_configure():
    # Make sure that we can run all tests even on non-Windows platforms
    os.environ.setdefault("WINDOWSAUTHTOKEN_IGNORE_PYWIN32_ERRORS", "true")

    # Set up Django settings for the tests
    settings.configure(
        DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
        INSTALLED_APPS=[
            "django.contrib.contenttypes",
            "django.contrib.auth",
            "django.contrib.sessions",
            "django.contrib.admin",
        ],
        ROOT_URLCONF="urlconf",
        SECRET_KEY="django-insecure-test-key",
    )
