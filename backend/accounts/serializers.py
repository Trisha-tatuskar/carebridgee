from rest_framework import serializers

from django.contrib.auth.models import User

from .models import Emergency, Donation, SupportCenter, Hospital, Volunteer, validate_non_negative_integer


class EmergencySerializer(serializers.ModelSerializer):
    phone = serializers.CharField()

    class Meta:
        model = Emergency
        fields = ("id", "emergency_type", "phone", "description", "address", "latitude", "longitude", "created_at")

    def validate_phone(self, value):
        from .models import validate_digits
        validate_digits(value)
        return value


class DonationSerializer(serializers.ModelSerializer):
    donor_name = serializers.CharField()
    donor_phone = serializers.CharField()
    amount = serializers.IntegerField(validators=[validate_non_negative_integer])

    class Meta:
        model = Donation
        fields = (
            "id",
            "donor_name",
            "donor_phone",
            "item",
            "description",
            "amount",
            "via_volunteer",
            "to_center",
            "created_at",
        )

    def validate(self, attrs):
        via_vol = attrs.get("via_volunteer")
        to_center = attrs.get("to_center")
        if not via_vol and not to_center:
            raise serializers.ValidationError("At least one of via_volunteer or to_center must be provided.")
        return attrs


class SupportCenterSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportCenter
        fields = ("id", "name", "center_type", "address", "phone", "email", "latitude", "longitude")


class HospitalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hospital
        fields = ("id", "name", "address", "phone", "latitude", "longitude")


class VolunteerDashboardSerializer(serializers.Serializer):
    volunteer = serializers.CharField()
    center_name = serializers.CharField(allow_null=True)
    center_address = serializers.CharField(allow_null=True)
    center_phone = serializers.CharField(allow_null=True)
    total_donations = serializers.IntegerField()
    donations = DonationSerializer(many=True)


class NGODashboardSerializer(serializers.Serializer):
    center_name = serializers.CharField()
    volunteers = serializers.ListField(child=serializers.CharField())
    total_donations = serializers.IntegerField()
    total_amount = serializers.IntegerField()
    donations = DonationSerializer(many=True)
