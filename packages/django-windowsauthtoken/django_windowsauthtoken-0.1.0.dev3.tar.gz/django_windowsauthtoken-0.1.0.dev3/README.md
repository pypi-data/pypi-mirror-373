# Windows Authentication Token handling for Django

![PyPI - Version](https://img.shields.io/pypi/v/django-windowsauthtoken?link=https%3A%2F%2Fpypi.org%2Fproject%2Fdjango-windowsauthtoken&logo=pypi)
![GitHub branch check runs](https://img.shields.io/github/check-runs/whyscream/django-windowsauthtoken/main?logo=github&link=https%3A%2F%2Fgithub.com%2Fwhyscream%2Fdjango-windowsauthtoken%2F)

When IIS on Windows is used as a webserver frontend for Django, authentication can be handled by the webserver using Windows Authentication. Microsoft recommends using the HttpPlatformHandler method to integrate Python webapps with IIS. Unlike the FastCGI handler which requires the old and unmaintained `wfastcgi` Python dependency, the HttpPlatformHandler doesn't set the `REMOTE_USER` variable after authentication. Instead, the authenticated user receives a Windows Authentication Token, which is available as a header named `X-IIS-WindowsAuthToken`.

This package provides a Django middleware that extracts this token from the request, retrieves the actual username from Windows, and sets the `REMOTE_USER` variable accordingly. This allows you to use Django's built-in authentication mechanisms seamlessly.

## Installation

You can install the package using pip:

```bash
pip install django-windowsauthtoken
```
On Windows, this will also install the `pywin32` package, which is required to interact with Windows APIs. Note that `pywin32` is only available on Windows, so this package will not work on other operating systems.

After installation, add the middleware to your Django settings:

```python
MIDDLEWARE = [
    ...,
    "django.auth.middleware.AuthenticationMiddleware",
    # Ensure this comes before RemoteUserMiddleware
    "django_windowsauthtoken.middleware.WindowsAuthTokenMiddleware",
    # You'll likely want to use Django's RemoteUserMiddleware too, to process the REMOTE_USER variable
    "django.contrib.auth.middleware.RemoteUserMiddleware",
    ...
]
```

If you're using Django's `RemoteUserMiddleware`, you might also want to set:

```python
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.RemoteUserBackend",
    ...
]
```

Now configure IIS to integrate with your Django application [using the HttpPlatformHandler](https://learn.microsoft.com/en-us/visualstudio/python/configure-web-apps-for-iis-windows?view=vs-2022#option-1-configure-the-httpplatformhandler), and ensure that [Windows Authentication is enabled](https://learn.microsoft.com/en-us/iis/configuration/system.webServer/security/authentication/windowsAuthentication/) for your site.

TODO: Add detailed instructions for setting up IIS.

## Usage

Once the middleware is added, it will automatically handle the extraction of the Windows Authentication token from the `X-IIS-WindowsAuthToken` header and set the `REMOTE_USER` variable. You can then use Django's authentication system as usual.

The RemoteUserMiddleware will use the `REMOTE_USER` variable to authenticate users against Django's user model. If a user with the given username does not exist, it will by default create a new user. See the Django documentation for more details on [how RemoteUserMiddleware works](https://docs.djangoproject.com/en/stable/topics/auth/default/#django.contrib.auth.middleware.RemoteUserMiddleware).

## Username format

By default, the middleware will set the `REMOTE_USER` variable to the username in the format `DOMAIN\username`. While this is true to the Windows Authentication standard, it may not be the format you want to use in your Django application, especially if you are using Django's default user model which does not allow backslashes in usernames.

If you prefer to use just the `username` without the domain, you can configure this by setting the following in your Django settings:

```python
WINDOWSAUTHTOKEN_USERNAME_FORMATTER = "django_windowsauthtoken.formatters.format_username_only"
```

Alternatively, if you want to use the `username@domain` format, you can set:

```python
WINDOWSAUTHTOKEN_USERNAME_FORMATTER = "django_windowsauthtoken.formatters.format_email_like"
```

Both of the above formats are acceptable by Django. You can also implement your own custom formatter function. The function should take two arguments: `username` and `domain`, and return the formatted username.

### Debugging

When setting up IIS or the middleware is not working as expected, there is a debug view that shows all relevant information from the request. To enable it, add the following to your `urls.py`:

```python
from django.urls import path
from django_windowsauthtoken.views import debug_view

urlpatterns = [
    ...,
    path("windowsauthtoken-debug/", debug_view, name="windowsauthtoken-debug"),
    ...,
]
```
You will also need to enable `DEBUG` in your Django settings. Then navigate to `/windowsauthtoken-debug/` in your browser. This view will display the headers and other relevant information from the request, which can help you diagnose issues with the middleware or IIS configuration.

## Development

To contribute to the development of this package, clone the repository and install the development dependencies:

```shell
git clone https://github.com/whyscream/django-windowsauthtoken
cd django-windowsauthtoken
uv sync --dev
```

### Note on pywin32

When developing on a non-Windows system, you can work around the absence of `pywin32` by setting the following environment variable:

```shell
WINDOWSAUTHTOKEN_IGNORE_PYWIN32_ERRORS=true
```

This will allow you to run the tests and work on the code without `pywin32`, but note that the middleware will not function correctly without it.

### Running Tests

You can run the tests using pytest:

```shell
pytest
```

When making changes, ensure that you add tests for any new functionality and run the existing tests to verify that everything works as expected.

### Coding standards

Code formatting and linting is done using `ruff` and `pre-commit`. See the pre-commit docs on how to set it up. You can check the formatting manually by running:

```shell
pre-commit run --all-files
```

## License

This project is licensed under the BSD-3-Clause License. See the [LICENSE](LICENSE) file for details.
