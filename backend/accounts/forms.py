# accounts/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Volunteer, SupportCenter, Donation, Emergency


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)


class VolunteerRegistrationForm(forms.ModelForm):
    class Meta:
        model = Volunteer
        fields = [
            "full_name",
            "phone",
            "address",
            "skills",         # NEW
            "available_time", # NEW
        ]
        widgets = {
            "address": forms.Textarea(attrs={"rows": 2}),
            "skills": forms.Textarea(attrs={"rows": 3}),
        }


class SupportCenterRegistrationForm(forms.ModelForm):
    class Meta:
        model = SupportCenter
        # IMPORTANT: only fields that actually exist on SupportCenter model
        fields = ["name", "center_type", "address", "phone", "description"]

        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "center_type": forms.Select(attrs={"class": "form-control"}),
            "address": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(
                attrs={"class": "form-control", "rows": 3, "placeholder": "Optional"}
            ),
        }


class DonationForm(forms.ModelForm):
    class Meta:
        model = Donation
        fields = [
            "donation_type",
            "quantity",
            "description",
            "address",
            "via_volunteer",  # either this
            "to_center",      # or this
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "address": forms.Textarea(attrs={"rows": 2}),
        }
        labels = {
            "donation_type": "Donation Type",
            "via_volunteer": "Assign a Volunteer",
            "to_center": "Send to a Support Center",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # optional: nicer empty labels
        self.fields["via_volunteer"].required = False
        self.fields["to_center"].required = False
        self.fields["via_volunteer"].empty_label = "Select a volunteer"
        self.fields["to_center"].empty_label = "Select a support center"


class EmergencyForm(forms.ModelForm):
    class Meta:
        model = Emergency
        fields = [
            "full_name",
            "phone",
            "emergency_type",  # NEW choices
            "description",
            "address",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "address": forms.Textarea(attrs={"rows": 2}),
        }
