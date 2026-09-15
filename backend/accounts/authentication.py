from django.contrib.auth.models import User
from .models import Volunteer, SupportCenter


def get_user_roles(user: User):
    """
    Simple helper to detect roles for a user.
    Returns dict like {"is_volunteer": True, "is_support_center": False}.
    """
    roles = {
        "is_volunteer": False,
        "is_support_center": False,
    }
    if not user.is_authenticated:
        return roles
    roles["is_volunteer"] = Volunteer.objects.filter(user=user).exists()
    roles["is_support_center"] = SupportCenter.objects.filter(user=user).exists()
    return roles
