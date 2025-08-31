from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated
from rest_framework.response import Response
from rest_framework.views import exception_handler


def handle_clickify_exceptions(exception):
    """Handle exceptions specific to the django-clickify app.

    Returns a Response object if the exceptions is handled otherwise None.
    """
    if exception.__class__.__name__ == "Ratelimited":
        ratelimit_message = getattr(
            settings,
            "CLICKIFY_RATELIMIT_MESSAGE",
            "You have made too many requests. Please try again later",
        )
        return Response(
            {"error": ratelimit_message},
            status=status.HTTP_429_TOO_MANY_REQUESTS,
        )

    if isinstance(exception, NotAuthenticated):
        return Response(
            {"error": "Authentication credentials were not provided."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    if isinstance(exception, PermissionDenied):
        return Response(
            {"error": "You do not have permission to perform this action."},
            status=status.HTTP_403_FORBIDDEN,
        )

    # Handle IP detection errors (common with proxies or sockets)
    if isinstance(
        exception, ImproperlyConfigured
    ) and "IP address in REMOTE_ADDR is empty" in str(exception):
        return Response(
            {
                "error": "Unable to detect client IP. Check proxy headers or CLICKIFY_IP_HEADERS setting."
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    return None


def custom_exception_handler(exception, context):
    """Handle exceptions for the app.

    It first attempts to handle clickify-specific exceptions, then falls back
    to the default DRF exception handler.
    """
    # First try to handle our custome exceptions
    response = handle_clickify_exceptions(exception)
    if response is not None:
        return response

    # If our handler doesn't handle the exception, fall back to DRF's default
    return exception_handler(exception, context)
