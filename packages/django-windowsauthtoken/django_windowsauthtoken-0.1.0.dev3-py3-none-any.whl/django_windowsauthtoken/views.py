from django.conf import settings
from django.http import JsonResponse


def debug_view(request):
    """
    A simple debug view that returns the current user's username and domain.
    """
    if not settings.DEBUG:
        return JsonResponse({"error": "This view is only available in DEBUG mode."})

    return JsonResponse(
        {
            "META HTTP_X_IIS_WINDOWSAUTHTOKEN": request.META.get("HTTP_X_IIS_WINDOWSAUTHTOKEN", "N/A"),
            "META REMOTE_USER": request.META.get("REMOTE_USER", "N/A"),
            "META HTTP_REMOTE_USER": request.META.get("HTTP_REMOTE_USER", "N/A"),
            "META WINDOWSAUTHTOKEN_USER": request.META.get("WINDOWSAUTHTOKEN", "N/A"),
            "META WINDOWSAUTHTOKEN_DOMAIN": request.META.get("WINDOWSAUTHTOKEN_DOMAIN", "N/A"),
            "user.is_authenticated": request.user.is_authenticated,
            "user.is_anonymous": request.user.is_anonymous,
            "user.username": request.user.username if request.user.is_authenticated else "N/A",
            "request": str(request),
            "META": {k: str(v) for k, v in request.META.items()},
        }
    )
