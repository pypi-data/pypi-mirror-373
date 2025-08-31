class FormattingError(Exception):
    """Custom exception for formatting errors."""

    pass


def format_domain_user(user: str, domain: str) -> str:
    r"""Format the username as DOMAIN\user."""
    if not domain or not user:
        raise FormattingError("Domain and user cannot be empty.")
    return rf"{domain}\{user}"


def format_username_only(user: str, domain: str) -> str:
    """Format the username as user only."""
    if not user:
        raise FormattingError("User cannot be empty.")
    return user


def format_email_like(user: str, domain: str) -> str:
    """Format the username as user@domain."""
    if not user or not domain:
        raise FormattingError("User and domain cannot be empty.")
    return f"{user}@{domain}"


DEFAULT_FORMATTER = f"{__name__}.format_domain_user"
