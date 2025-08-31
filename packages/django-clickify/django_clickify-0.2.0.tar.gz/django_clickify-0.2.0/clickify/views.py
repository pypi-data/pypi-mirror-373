from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404

from .decorators import conditional_ratelimit
from .models import TrackedLink
from .utils import create_click_log


@conditional_ratelimit
def track_click(request, slug):
    """Track a click for a TrackedLink and redirect - using utility function."""
    target = get_object_or_404(TrackedLink, slug=slug)
    create_click_log(target=target, request=request)
    return HttpResponseRedirect(target.target_url)
