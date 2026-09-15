# accounts/admin.py

from django.contrib import admin
from .models import Volunteer, SupportCenter, Donation, Emergency, Hospital


@admin.register(Volunteer)
class VolunteerAdmin(admin.ModelAdmin):
    """
    Simple admin for Volunteer.
    No custom list_display so we avoid field name issues.
    """
    pass


@admin.register(SupportCenter)
class SupportCenterAdmin(admin.ModelAdmin):
    """
    Simple admin for SupportCenter.
    """
    pass


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    """
    Simple admin for Donation.
    """
    pass


@admin.register(Emergency)
class EmergencyAdmin(admin.ModelAdmin):
    """
    Simple admin for Emergency.
    """
    pass


@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    """
    Simple admin for Hospital.
    """
    pass
