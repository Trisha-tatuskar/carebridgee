from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

from .models import Emergency, Donation, SupportCenter, Hospital, Volunteer
from .serializers import (
    EmergencySerializer,
    DonationSerializer,
    SupportCenterSerializer,
    HospitalSerializer,
    VolunteerDashboardSerializer,
    NGODashboardSerializer,
)


class EmergencyCreateAPIView(generics.CreateAPIView):
    queryset = Emergency.objects.all()
    serializer_class = EmergencySerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(user=user)


class DonationCreateAPIView(generics.CreateAPIView):
    queryset = Donation.objects.all()
    serializer_class = DonationSerializer
    permission_classes = [permissions.IsAuthenticated]


class VolunteerAssignAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Only staff or support center owners can assign volunteers
        if not (request.user.is_staff or hasattr(request.user, "supportcenter")):
            return Response({"detail": "Not allowed."}, status=status.HTTP_403_FORBIDDEN)

        volunteer_id = request.data.get("volunteer_id")
        center_id = request.data.get("center_id")

        volunteer = get_object_or_404(Volunteer, pk=volunteer_id)
        center = get_object_or_404(SupportCenter, pk=center_id)

        volunteer.assigned_center = center
        volunteer.save()
        return Response({"detail": "Volunteer assigned successfully."}, status=status.HTTP_200_OK)


class SupportCenterListAPIView(generics.ListAPIView):
    queryset = SupportCenter.objects.all()
    serializer_class = SupportCenterSerializer
    permission_classes = [permissions.AllowAny]


class HospitalListAPIView(generics.ListAPIView):
    queryset = Hospital.objects.all()
    serializer_class = HospitalSerializer
    permission_classes = [permissions.AllowAny]


class VolunteerDashboardAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        volunteer = getattr(request.user, "volunteer", None)
        if not volunteer:
            return Response({"detail": "User is not a volunteer."}, status=status.HTTP_403_FORBIDDEN)

        donations = Donation.objects.filter(via_volunteer=volunteer).order_by("-created_at")
        center = volunteer.assigned_center

        data = {
            "volunteer": volunteer.full_name,
            "center_name": center.name if center else None,
            "center_address": center.address if center else None,
            "center_phone": center.phone if center else None,
            "total_donations": donations.count(),
            "donations": DonationSerializer(donations, many=True).data,
        }
        serializer = VolunteerDashboardSerializer(data)
        return Response(serializer.data)


class NGODashboardAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        center = getattr(request.user, "supportcenter", None)
        if not center:
            return Response({"detail": "User is not a support center owner."}, status=status.HTTP_403_FORBIDDEN)

        volunteers = center.volunteers.all()
        donations = Donation.objects.filter(to_center=center).order_by("-created_at")
        total_donations = donations.count()
        total_amount = sum(d.amount for d in donations)

        data = {
            "center_name": center.name,
            "volunteers": [v.full_name for v in volunteers],
            "total_donations": total_donations,
            "total_amount": total_amount,
            "donations": DonationSerializer(donations, many=True).data,
        }
        serializer = NGODashboardSerializer(data)
        return Response(serializer.data)
