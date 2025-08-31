# Django Clickify

[![PyPI version](https://img.shields.io/pypi/v/django-clickify.svg)](https://pypi.org/project/django-clickify/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A simple Django app to track clicks on any link (e.g., affiliate links, outbound links, file downloads) with rate limiting, IP filtering, and geolocation.

## Features

- **Click Tracking**: Logs every click on a tracked link, including IP address, user agent, and timestamp.
- **Geolocation**: Automatically enriches click logs with the country and city of the request's IP address via a web API.
- **Rate Limiting**: Prevents abuse by limiting the number of clicks per IP address in a given timeframe (can be disabled).
- **IP Filtering**: Easily configure allowlists and blocklists for IP addresses.
- **Django Admin Integration**: Create and manage your tracked links directly in the Django admin.
- **Flexible Usage**: Provides both a simple template tag for traditional Django templates and a DRF API view for headless/JavaScript applications.

## Installation

1.  Install the package from PyPI:

    ```bash
    pip install django-clickify
    ```

2.  Add `'clickify'` to your `INSTALLED_APPS` in `settings.py`:

    ```python
    INSTALLED_APPS = [
        # ...
        'clickify',
    ]
    ```

3.  Run migrations to create the necessary database models:

    ```bash
    python manage.py migrate
    ```

4.  **For API support (Optional)**: If you plan to use the DRF view, you can either install with the `[drf]` or `[full]` extra (see step 5) or manually install `djangorestframework` and add it to your `INSTALLED_APPS`.

    ```bash
    pip install djangorestframework
    ```

    ```python
    INSTALLED_APPS = [
        # ...
        'rest_framework',
        'clickify',
    ]
    ```

5.  **Optional Dependencies**: This package supports optional features that require additional dependencies:

    ```bash
    # For rate limiting support only
    pip install django-clickify[ratelimit]

    # For DRF API support only
    pip install django-clickify[drf]

    # For all optional features
    pip install django-clickify[full]
    ```

    Alternatively, you can install the base package and add dependencies manually as described in the sections above.

## Configuration

You can customize the behavior of `django-clickify` by adding the following settings to your project's `settings.py` file.

### General Settings

- `CLICKIFY_GEOLOCATION`: A boolean to enable or disable geolocation. Defaults to `True`.
- `CLICKIFY_ENABLE_RATELIMIT`: A boolean to enable or disable rate limiting. Defaults to `True`. Set to `False` to disable all rate limiting.
- `CLICKIFY_RATE_LIMIT`: The rate limit for clicks when rate limiting is enabled. Defaults to `'5/m'` (5 requests per minute).
- `CLICKIFY_RATELIMIT_MESSAGE`: Customize the message displayed when the rate limit is exceeded. This is used for both template-based views (via the Django messages framework) and the DRF API. Defaults to `"You have made too many requests. Please try again later"`.
- `CLICKIFY_IP_ALLOWLIST`: A list of IP addresses that are always allowed. Defaults to `[]`.
- `CLICKIFY_IP_BLOCKLIST`: A list of IP addresses that are always blocked. Defaults to `[]`.
- `CLICKIFY_IP_HEADERS`: A list of HTTP headers to check for the real client IP address (useful when behind proxies or load balancers). Defaults to:
  ```python
  [
      "HTTP_X_FORWARDED_FOR",
      "HTTP_X_REAL_IP",
      "HTTP_X_FORWARDED",
      "HTTP_X_CLUSTER_CLIENT_IP",
      "HTTP_FORWARDED_FOR",
      "HTTP_FORWARDED",
      "REMOTE_ADDR",
  ]
  ```

### Rate Limiting Configuration

Rate limiting is enabled by default but can be completely disabled:

```python
# settings.py

# Disable rate limiting entirely
CLICKIFY_ENABLE_RATELIMIT = False

# Or configure rate limiting (when enabled)
CLICKIFY_ENABLE_RATELIMIT = True
CLICKIFY_RATE_LIMIT = '10/h'  # 10 requests per hour
CLICKIFY_RATELIMIT_MESSAGE = "Too many clicks! Please wait before trying again."
```

**Note**: When rate limiting is enabled, you can either install with the `[ratelimit]` or `[full]` extra, or manually install `django-ratelimit`:

```bash
pip install django-ratelimit
```

### IP Detection Configuration

For applications behind proxies or load balancers, configure the IP headers to check:

```python
# settings.py

# Custom IP headers (checked in order)
CLICKIFY_IP_HEADERS = [
    "HTTP_CF_CONNECTING_IP",      # Cloudflare
    "HTTP_X_FORWARDED_FOR",       # Standard proxy header
    "HTTP_X_REAL_IP",             # Nginx
    "REMOTE_ADDR",                # Fallback
]
```

### Middleware (for IP Filtering)

To enable the IP allowlist and blocklist feature, add the `IPFilterMiddleware` to your `settings.py`.

```python
MIDDLEWARE = [
    # ...
    'clickify.middleware.IPFilterMiddleware',
    # ...
]
```

## Usage

First, create a `TrackedLink` in your Django Admin under the "Clickify" section. This target can be any URL you want to track.

- **Name:** `Monthly Report PDF`
- **Slug:** `monthly-report-pdf` (this will be auto-populated from the name)
- **Target Url:** `https://your-s3-bucket.s3.amazonaws.com/reports/monthly-summary.pdf`

Once a `TrackedLink` is created, you can use it in one of two ways.

### Option 1: Template-Based Usage

This is the standard way to use the app in traditional Django projects.

#### Step 1: Include Clickify URLs

In your project's `urls.py`, include the `clickify` URL patterns. You can choose any path you like for the tracking URLs.

```python
# your_project/urls.py
from django.urls import path, include

urlpatterns = [
    # ... your other urls
    path('track/', include('clickify.urls', namespace='clickify')),
]
```

#### Step 2: Use the Template Tag

In your Django template, use the `track_url` template tag to generate the tracking link.

```html
<!-- your_app/templates/my_template.html -->
{% load clickify_tags %}

<a href="{% track_url 'monthly-report-pdf' %}"> Get Monthly Summary </a>
```

When a user exceeds the rate limit (if enabled), `django-clickify` uses the [Django messages framework](https://docs.djangoproject.com/en/stable/ref/contrib/messages/) to display an error. The user is then redirected back to the page they came from.

To display the message in your templates, make sure you have configured the messages framework and included code to render the messages, like this:

```html
{% if messages %}
<ul class="messages">
  {% for message in messages %}
  <li class="{{ message.tags }}">{{ message }}</li>
  {% endfor %}
</ul>
{% endif %}
```

### Option 2: API Usage (for Headless/JS Frameworks)

If you are using a JavaScript frontend (like React, Vue, etc.) or need a programmatic way to track a click, you can use the DRF API endpoint.

#### Step 1: Include Clickify DRF URLs

In your project's `urls.py`, include the `clickify.drf_urls` patterns. You can choose any path you like for the API endpoint.

```python
# your_project/urls.py
from django.urls import path, include

urlpatterns = [
    # ... your other urls
    path('api/track/', include('clickify.drf_urls', namespace='clickify-api')),
]
```

#### Step 2: Make the API Request

From your frontend, make a `POST` request to the API endpoint using the slug of your `TrackedLink`.

**Endpoint**: `POST /api/track/<slug>/`

**Example using JavaScript `fetch`:**

```javascript
fetch("/api/track/monthly-report-pdf/", {
  method: "POST",
  headers: {
    // Include CSRF token if necessary for your setup
    "X-CSRFToken": "YourCsrfTokenHere",
  },
})
  .then((response) => response.json())
  .then((data) => {
    if (data.target_url) {
      console.log("Click tracked. Redirecting to:", data.target_url);
      // Redirect the user to the URL
      window.location.href = data.target_url;
    } else {
      console.error("Failed to track click:", data);
    }
  })
  .catch((error) => {
    console.error("Error:", error);
  });
```

**Successful Response (`200 OK`):**

```json
{
  "message": "Click tracked successfully",
  "target_url": "https://your-s3-bucket.s3.amazonaws.com/reports/monthly-summary.pdf"
}
```

**Rate Limited Response (`429 Too Many Requests`):**

```json
{
  "error": "You have made too many requests. Please try again later"
}
```

#### API-Specific Configuration

- **`CLICKIFY_PERMISSION_CLASSES`**: Control who can access the tracking API endpoint. This should be a list of DRF permission classes. Defaults to `[AllowAny]`.

  ```python
  # settings.py
  CLICKIFY_PERMISSION_CLASSES = ["rest_framework.permissions.IsAuthenticated"]
  ```

- **Improving API Error Responses**: To provide clearer, more consistent error messages for the API (e.g., for rate limiting or authentication errors), you can use the custom exception handling logic included with `django-clickify`.

  - **If you DO NOT have a custom exception handler:**
    In your `settings.py`, you can use the handler provided by `django-clickify` directly:

    ```python
    # settings.py
    REST_FRAMEWORK = {
        'EXCEPTION_HANDLER': 'clickify.drf_exception_handler.custom_exception_handler'
    }
    ```

  - **If you ALREADY have a custom exception handler:**
    You can easily integrate `django-clickify`'s logic into your existing handler.

    ```python
    # your_project/your_app/exception_handler.py
    from rest_framework.views import exception_handler
    from clickify.drf_exception_handler import handle_clickify_exceptions # <-- Import

    def your_custom_handler(exc, context):
        # First, check for clickify-specific exceptions
        response = handle_clickify_exceptions(exc)
        if response is not None:
            return response

        # Continue with your existing custom error handling logic
        # ...

        # Fall back to the default DRF handler
        return exception_handler(exc, context)
    ```

## How It Works

1.  A user clicks a tracked link (`/track/monthly-report-pdf/`) or a `POST` request is sent to the API.
2.  The view or API view records the click event in the database, associating it with the correct `TrackedLink`.
3.  If rate limiting is enabled and the user has exceeded the limit, they receive an error message and are redirected back (for template views) or receive a JSON error response (for API views).
4.  For successful requests, the standard view issues a `302 Redirect` to the `target_url`. The API view returns a JSON response containing the `target_url`.
5.  The user's browser is redirected to the final destination.

This approach is powerful because if you ever need to change the link's destination, you only need to update the `Target Url` in the Django Admin. All your tracked links and API calls will continue to work correctly.
