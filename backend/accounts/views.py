# backend/accounts/views.py

import json

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from .forms import (
    UserRegistrationForm,
    LoginForm,
    VolunteerRegistrationForm,
    SupportCenterRegistrationForm,
    DonationForm,
    EmergencyForm,
)
from .models import Volunteer, SupportCenter, Donation, Emergency, Hospital


# -------------------------
# Home
# -------------------------

def home(request):
    """
    Landing page (Bridge Help & Hope hero + feature cards).
    """
    roles = ["Donor", "Volunteer", "Support Center"]

    support_centers = SupportCenter.objects.all()[:6]
    hospitals = Hospital.objects.all()[:6]

    if not support_centers:
        messages.info(request, "No support centers nearby currently.")

    context = {
        "roles": roles,
        "support_centers": support_centers,
        "hospitals": hospitals,
    }
    return render(request, "accounts/home.html", context)


# -------------------------
# Authentication
# -------------------------

def register(request):
    """
    User registration.
    URL name: 'register'
    """
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful. Please log in.")
            return redirect("login")
    else:
        form = UserRegistrationForm()

    return render(request, "accounts/register.html", {"form": form})


def login_view(request):
    """
    User login.
    URL name: 'login'
    """
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Login successful.")
                return redirect("home")
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()

    return render(request, "accounts/login.html", {"form": form})


@login_required
def logout_view(request):
    """
    Logout and redirect to home.
    URL name: 'logout'
    """
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("home")


# -------------------------
# Volunteer
# -------------------------

@login_required
def volunteer_registration(request):
    """
    Create or update volunteer profile.
    URL name: 'volunteer_registration'
    """
    volunteer = getattr(request.user, "volunteer", None)

    if request.method == "POST":
        form = VolunteerRegistrationForm(request.POST, instance=volunteer)
        if form.is_valid():
            volunteer = form.save(commit=False)
            volunteer.user = request.user
            volunteer.save()
            messages.success(request, "Volunteer profile saved successfully.")
            return redirect("volunteer_dashboard")
    else:
        form = VolunteerRegistrationForm(instance=volunteer)

    return render(request, "accounts/volunteer_registration.html", {"form": form})



@login_required
def volunteer_dashboard(request):
    """
    Volunteer dashboard:
    - shows donations assigned to this volunteer
    - shows latest emergency requests so they can respond
    """
    volunteer = getattr(request.user, "volunteer", None)
    donations = Donation.objects.filter(via_volunteer=volunteer) if volunteer else []

    # Latest emergencies – you can filter by location later if you store it
    emergencies = Emergency.objects.all().order_by("-created_at")[:10]

    context = {
        "volunteer": volunteer,
        "donations": donations,
        "emergencies": emergencies,
    }
    return render(request, "accounts/volunteer_dashboard.html", context)


# accounts/views.py

@login_required
def volunteer_page(request):
    volunteer = getattr(request.user, "volunteer", None)
    return render(request, "accounts/volunteer.html", {"volunteer": volunteer})



# -------------------------
# Support Center (NGO / Orphanage / Shelter)
# -------------------------

@login_required
def support_center_registration(request):
    """
    Create or update support center profile.
    URL name: 'support_center_registration'
    """
    support_center = getattr(request.user, "supportcenter", None)

    if request.method == "POST":
        form = SupportCenterRegistrationForm(request.POST, instance=support_center)
        if form.is_valid():
            center = form.save(commit=False)
            center.user = request.user
            center.save()
            messages.success(request, "Support center profile saved successfully.")
            return redirect("ngo_dashboard")
    else:
        form = SupportCenterRegistrationForm(instance=support_center)

    return render(
        request,
        "accounts/support_center_registration.html",
        {"form": form},
    )


@login_required
def ngo_dashboard(request):
    """
    Dashboard for support center (NGO Dashboard).
    They can see assigned volunteers, donations to their center,
    and recent emergencies. They can also assign volunteers.
    URL name: 'ngo_dashboard'
    """
    center = getattr(request.user, "supportcenter", None)

    if not center:
        messages.info(request, "Please complete your support center profile first.")
        return redirect("support_center_registration")

    # Handle assigning volunteer to this center
    if request.method == "POST":
        volunteer_id = request.POST.get("assign_volunteer_id")
        if volunteer_id:
            volunteer = get_object_or_404(Volunteer, id=volunteer_id)
            volunteer.support_center = center
            volunteer.save()
            messages.success(
                request,
                f"Volunteer '{volunteer.full_name}' assigned to {center.name}.",
            )
            return redirect("ngo_dashboard")

    assigned_volunteers = Volunteer.objects.filter(support_center=center)
    unassigned_volunteers = Volunteer.objects.filter(support_center__isnull=True)

    donations = Donation.objects.filter(to_center=center)
    emergencies = Emergency.objects.all().order_by("-created_at")[:20]

    context = {
        "center": center,
        "donations": donations,
        "emergencies": emergencies,
        "assigned_volunteers": assigned_volunteers,
        "unassigned_volunteers": unassigned_volunteers,
    }
    return render(request, "accounts/ngo_dashboard.html", context)


def support_centers_list(request):
    """
    List all support centers with Google Map (similar to hospitals).
    URL name: 'support_centers_list'
    """
    support_centers = SupportCenter.objects.all()

    if not support_centers:
        messages.info(request, "No support centers nearby currently.")

    centers_data = [
        {
            "name": c.name,
            "address": c.address,
            "latitude": c.latitude,
            "longitude": c.longitude,
        }
        for c in support_centers
        if getattr(c, "latitude", None) is not None
        and getattr(c, "longitude", None) is not None
    ]

    context = {
        "support_centers": support_centers,
        "support_centers_json": json.dumps(centers_data),
    }
    return render(request, "accounts/support_centers.html", context)


# -------------------------
# Donation flow
# -------------------------

@login_required
def donation_form(request):
    """
    Donation creation form.
    URL name in urls: 'create_donation'
    """
    if request.method == "POST":
        form = DonationForm(request.POST)
        if form.is_valid():
            donation = form.save(commit=False)
            donation.donor = request.user

            # Auto-fill donor details if missing
            if not donation.donor_name:
                donation.donor_name = (
                    request.user.get_full_name() or request.user.username
                )

            if not donation.donor_phone and hasattr(request.user, "volunteer"):
                donation.donor_phone = request.user.volunteer.phone

            donation.save()
            messages.success(request, "Donation submitted successfully.")
            return redirect("donations_list")
    else:
        form = DonationForm()

    return render(request, "accounts/donation_form.html", {"form": form})


@login_required
def donations_list(request):
    """
    List of all donations.
    URL name: 'donations_list'
    """
    donations = Donation.objects.all().order_by("-created_at")
    return render(request, "accounts/donation_list.html", {"donations": donations})


# -------------------------
# Emergency flow
# -------------------------

def emergency_form(request):
    """
    Emergency form WITHOUT login.
    URL name: 'emergency_form'
    """
    if request.method == "POST":
        form = EmergencyForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Emergency reported successfully. Nearby helpers will be notified.",
            )
            return redirect("home")
    else:
        form = EmergencyForm()

    return render(request, "accounts/emergency_form.html", {"form": form})


# -------------------------
# Hospitals + Google Maps
# -------------------------

def hospitals_list(request):
    """
    Show list of hospitals + Google Map.
    URL name: 'hospitals_list'
    """
    hospitals = Hospital.objects.all()

    hospitals_data = [
        {
            "name": h.name,
            "address": h.address,
            "latitude": h.latitude,
            "longitude": h.longitude,
        }
        for h in hospitals
        if getattr(h, "latitude", None) is not None
        and getattr(h, "longitude", None) is not None
    ]

    context = {
        "hospitals": hospitals,
        "hospitals_json": json.dumps(hospitals_data),
    }
    return render(request, "accounts/hospitals.html", context)


# -------------------------
# Notifications
# -------------------------

@login_required
def notifications_view(request):
    """
    Simple notifications page: recent emergencies + donations.
    URL name: 'notifications'
    """
    latest_emergencies = Emergency.objects.all().order_by("-created_at")[:10]
    latest_donations = Donation.objects.all().order_by("-created_at")[:10]

    context = {
        "latest_emergencies": latest_emergencies,
        "latest_donations": latest_donations,
    }
    return render(request, "accounts/notifications.html", context)
