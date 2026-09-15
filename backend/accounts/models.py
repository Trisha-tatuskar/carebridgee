# accounts/models.py

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError


# --- Validators used by old migrations --- #

def validate_digits(value):
    """
    Used for phone fields in old migrations.
    Ensures the value contains only digits.
    """
    if not str(value).isdigit():
        raise ValidationError("Phone number must contain digits only.")


def validate_letters(value):
    """
    Used for name fields in old migrations.
    Allows only letters and spaces.
    """
    cleaned = str(value).replace(" ", "")
    if not cleaned.isalpha():
        raise ValidationError("Name must contain letters only.")


def validate_email_local_lower_letters(value):
    """
    Used in migrations for SupportCenter.email.
    Local-part (before @) must be lowercase a-z only.
    """
    value = str(value)
    local_part = value.split("@")[0]

    # must be only lowercase letters a-z
    if not local_part.isalpha() or not local_part.islower():
        raise ValidationError(
            "Local-part (before @) must be lowercase letters a-z only."
        )
def validate_non_negative_integer(value):
    """
    Used for 'amount' fields in old migrations.
    Ensures the value is an integer >= 0.
    """
    try:
        ivalue = int(value)
    except (TypeError, ValueError):
        raise ValidationError("Amount must be a valid integer.")

    if ivalue < 0:
        raise ValidationError("Amount cannot be negative.")


class SupportCenter(models.Model):
    CENTER_TYPES = [
        ("NGO", "NGO"),
        ("Orphanage", "Orphanage"),
        ("Shelter", "Shelter"),
    ]

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="supportcenter"
    )
    name = models.CharField(max_length=200)
    center_type = models.CharField(max_length=50, choices=CENTER_TYPES)
    address = models.TextField()
    phone = models.CharField(max_length=15)
    # description is OPTIONAL
    description = models.TextField(blank=True)     # ✅ optional
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Volunteer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    address = models.TextField(blank=True)
    skills = models.TextField(blank=True)  # NEW: volunteer skills
    available_time = models.CharField(      # NEW: when they can volunteer
        max_length=100,
        blank=True,
        help_text="Example: Weekends 10am–2pm"
    )
    # NEW: which NGO / support center they are assigned to
    support_center = models.ForeignKey(
        SupportCenter,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="volunteers",
    )

    def __str__(self):
        return self.full_name or self.user.username


class Donation(models.Model):
    DONATION_TYPES = [
        ("food", "Food"),
        ("clothes", "Clothes"),
        ("medicine", "Medicine"),
        ("books", "Books"),
        ("other", "Other"),
    ]

    donor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="donations",
    )
    donation_type = models.CharField(max_length=50, choices=DONATION_TYPES)
    quantity = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)      # ✅ optional
    address = models.TextField()

    # either donate via volunteer OR directly to a support center
    to_center = models.ForeignKey(
        SupportCenter,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="donations",
    )
    via_volunteer = models.ForeignKey(
        Volunteer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="donations",
    )

    created_at = models.DateTimeField(default=timezone.now)

    donor_name = models.CharField(max_length=150, blank=True)
    donor_phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.get_donation_type_display()} from {self.donor_name or 'Anonymous'}"


class Emergency(models.Model):
    EMERGENCY_TYPES = [
        ("medical", "Medical"),
        ("fire", "Fire"),
        ("accident", "Accident"),
        ("natural_disaster", "Natural Disaster"),
        ("other", "Other"),
    ]

    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    emergency_type = models.CharField(
        max_length=50,
        choices=EMERGENCY_TYPES,
        default="other",
    )
    description = models.TextField(blank=True)    # ✅ optional
    address = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.get_emergency_type_display()} emergency by {self.full_name}"


class Hospital(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField()
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.name
