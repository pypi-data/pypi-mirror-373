from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django_ratelimit.decorators import ratelimit
from django_ratelimit.exceptions import Ratelimited

from .models import TrackedLink
from .utils import create_click_log


@ratelimit(
    key="ip",
    rate=lambda r, g: getattr(settings, "CLICKIFY_RATE_LIMIT", "5/m"),
    block=True,
)
def track_click(request, slug):
    """Track a click for a TrackedLink and then redirect to its actual URL.

    On rate limit, it adds a Django message and redirects to the referrer.
    """
    try:
        target = get_object_or_404(TrackedLink, slug=slug)
        create_click_log(target=target, request=request)
        return HttpResponseRedirect(target.target_url)
    except Ratelimited:
        # Get the custome message from settings, with a sensible default
        message = getattr(
            settings,
            "CLICKIFY_RATELIMIT_MESSAGE",
            "You have made too many requests. Please try again later",
        )

        messages.error(request, message)

        # Redirect back to the page the user came from, or to the homepage as a fallback
        redirect_url = request.META.get("HTTP_REFERER", "/")

        return HttpResponseRedirect(redirect_url)
