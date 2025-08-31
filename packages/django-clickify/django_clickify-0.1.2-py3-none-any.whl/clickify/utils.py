import requests
from django.conf import settings
from ipware import get_client_ip

from .models import ClickLog


def get_geolocation(ip_address):
    """Get the geolocation for a given IP address using the ip-api.com service.

    This function should only be called for public, routable IP addresses.
    """
    # Geolocation can be disabled globally in settings
    if not getattr(settings, "CLICKIFY_GEOLOCATION", True):
        return None, None

    if not ip_address:
        return None, None

    try:
        # The API endpoint. We request only the fields we need
        url = f"http://ip-api.com/json/{ip_address}?fields=status,country,city"
        response = requests.get(url, timeout=2)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        data = response.json()

        if data.get("status") == "success":
            return data.get("country"), data.get("city")
        else:
            return None, None
    except (requests.RequestException, ValueError):
        # Catch network errors, timeouts, or JSON decoding errors
        return None, None


def create_click_log(target, request):
    """Create a ClickLog object.

    This contains the core tracking logic that can be reused by both the
    standard view and the DRF API view.
    """
    ip, is_routable = get_client_ip(request)
    user_agent = request.META.get("HTTP_USER_AGENT", "")

    country, city = (None, None)
    if is_routable:
        country, city = get_geolocation(ip)

    ClickLog.objects.create(
        target=target, ip_address=ip, user_agent=user_agent, country=country, city=city
    )
