# backend/accounts/api_urls.py

from django.urls import path

# For now we keep this empty just to satisfy the include() in project urls.
# We can later add real API endpoints here (emergency, donations, dashboards, etc.)

urlpatterns = [
    # example (later):
    # path("emergency/", EmergencyCreateAPIView.as_view(), name="api_emergency_create"),
]
