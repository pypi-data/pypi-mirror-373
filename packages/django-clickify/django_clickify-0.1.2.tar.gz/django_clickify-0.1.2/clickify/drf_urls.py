from django.urls import path

from .drf_views import TrackClickAPIView

app_name = "clickify-drf"

urlpatterns = [
    path("<slug:slug>/", TrackClickAPIView.as_view(), name="track_click_api"),
]
