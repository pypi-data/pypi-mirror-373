from django.conf import settings

from .exceptions import handle_ratelimited_exception
from .utils import get_ratelimit_ip


def conditional_ratelimit(view_func):
    """Apply django-ratelimit only if enable in settings."""
    # If rate limiting is disabled return original view
    if not getattr(settings, "CLICKIFY_ENABLE_RATELIMIT", True):
        return view_func

    try:
        from django_ratelimit.decorators import ratelimit
        from django_ratelimit.exceptions import Ratelimited
    except ImportError as err:
        raise ImportError(
            "django-ratelimit is required for rate-limiting"
            "Either install it or disable CLICKIFY_ENABLE_RATELIMIT in settings"
        ) from err

    def wrapper(request, *args, **kwargs):
        # Apply rate limiting
        decorated_view = ratelimit(
            key=get_ratelimit_ip,
            rate=lambda r, g: getattr(settings, "CLICKIFY_RATE_LIMIT", "5/m"),
            block=True,
        )(view_func)

        try:
            return decorated_view(request, *args, **kwargs)
        except Ratelimited:
            if hasattr(request, "accepted_renderer"):
                # This is a DRF request - let DRF handle it
                raise
            return handle_ratelimited_exception(request)

    return wrapper
