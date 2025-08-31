from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseRedirect


def handle_ratelimited_exception(request):
    """Handle Ratelimited exception with proper error messaging."""
    message = getattr(
        settings,
        "CLICKIFY_RATELIMIT_MESSAGE",
        "You have made too many requests. Please try again later",
    )
    messages.error(request, message)
    redirect_url = request.META.get("HTTP_REFERER", "/")
    return HttpResponseRedirect(redirect_url)
