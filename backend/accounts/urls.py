# backend/accounts/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # Home
    path("", views.home, name="home"),

    # Auth
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    # Emergency (no login)
    path("emergency/", views.emergency_form, name="emergency_form"),

    # Donation
    path("donation/create/", views.donation_form, name="create_donation"),
    path("donations/", views.donations_list, name="donations_list"),

    # Volunteer
    path("volunteer/", views.volunteer_page, name="volunteer_page"),
    path("volunteer/register/", views.volunteer_registration, name="volunteer_registration"),
    path("volunteer/dashboard/", views.volunteer_dashboard, name="volunteer_dashboard"),

    # Support Centers (NGO)
    path("support-centers/", views.support_centers_list, name="support_centers_list"),
    path("support-center/register/", views.support_center_registration, name="support_center_registration"),
    path("support-center/dashboard/", views.ngo_dashboard, name="ngo_dashboard"),

    # Hospitals
    path("hospitals/", views.hospitals_list, name="hospitals_list"),

    # Notifications
    path("notifications/", views.notifications_view, name="notifications"),
]
