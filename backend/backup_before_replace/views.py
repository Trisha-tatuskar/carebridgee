from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, VolunteerRegisterForm, SupportCenterRegisterForm, DonationForm, EmergencyForm
from .models import Volunteer, SupportCenter, Donation, Emergency, Hospital
from .serializers import EmergencySerializer, DonationSerializer, VolunteerAssignSerializer, SupportCenterSerializer, HospitalSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.core.paginator import Paginator
from django.db import models

def home(request):
    centers = SupportCenter.objects.all()[:6]
    hospitals = Hospital.objects.all()[:6]
    return render(request, 'accounts/home.html', {'centers': centers, 'hospitals': hospitals})

def user_login(request):
    if request.method == 'POST':
        username_or_email = request.POST.get('username') or request.POST.get('email') or request.POST.get('username')
        password = request.POST.get('password')
        # allow login via username
        user = authenticate(request, username=username_or_email, password=password)
        if user:
            login(request, user)
            return redirect('home')
        messages.error(request, 'Invalid credentials')
    return render(request, 'accounts/login.html')

def user_logout(request):
    logout(request)
    return redirect('home')

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created. Please login.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def volunteer_register(request):
    # You required login for volunteer registration in earlier flow
    if request.method == 'POST':
        form = VolunteerRegisterForm(request.POST)
        if form.is_valid():
            vol = form.save(commit=False)
            vol.user = request.user
            vol.save()
            messages.success(request, 'Volunteer profile created.')
            return redirect('volunteer_dashboard')
    else:
        form = VolunteerRegisterForm()
    return render(request, 'accounts/volunteer_registration.html', {'form': form})

@login_required
def support_register(request):
    if request.method == 'POST':
        form = SupportCenterRegisterForm(request.POST)
        if form.is_valid():
            center = form.save(commit=False)
            center.user = request.user
            center.save()
            messages.success(request, 'Support center registered.')
            return redirect('ngo_dashboard')
    else:
        form = SupportCenterRegisterForm()
    return render(request, 'accounts/support.html', {'form': form})

@login_required
def donation_view(request):
    if request.method == 'POST':
        form = DonationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Donation recorded.')
            return redirect('donations')
    else:
        form = DonationForm()
    return render(request, 'accounts/donation.html', {'form': form})

@login_required
def donations_list(request):
    qs = Donation.objects.all().order_by('-created_at')
    paginator = Paginator(qs, 10)
    page = request.GET.get('page')
    donations = paginator.get_page(page)
    return render(request, 'accounts/notification.html', {'donations': donations})

def emergency_view(request):
    if request.method == 'POST':
        form = EmergencyForm(request.POST)
        if form.is_valid():
            em = form.save(commit=False)
            if request.user.is_authenticated:
                em.user = request.user
            em.save()
            messages.success(request, 'Emergency reported.')
            return redirect('home')
    else:
        form = EmergencyForm()
    return render(request, 'accounts/emergency.html', {'form': form})

def hospitals_view(request):
    hospitals = Hospital.objects.all()
    return render(request, 'accounts/hospitals.html', {'hospitals': hospitals})

@login_required
def volunteer_dashboard(request):
    try:
        volunteer = Volunteer.objects.get(user=request.user)
    except Volunteer.DoesNotExist:
        messages.info(request, 'No volunteer profile found. Register as a volunteer.')
        return redirect('volunteer_registration')
    assigned = volunteer.assigned_center
    donations_via = Donation.objects.filter(via_volunteer=volunteer)
    total = donations_via.count()
    return render(request, 'accounts/volunteer.html', {
        'volunteer': volunteer,
        'assigned': assigned,
        'donations': donations_via,
        'total': total
    })

@login_required
def ngo_dashboard(request):
    try:
        center = SupportCenter.objects.get(user=request.user)
    except SupportCenter.DoesNotExist:
        messages.info(request, 'No support center linked to your user. Register your support center.')
        return redirect('support')
    volunteers = Volunteer.objects.filter(assigned_center=center)
    donations = Donation.objects.filter(to_center=center)
    total_count = donations.count()
    total_amount = donations.aggregate(models.Sum('amount'))['amount__sum'] or 0
    return render(request, 'accounts/ngo.html', {
        'center': center,
        'volunteers': volunteers,
        'donations': donations,
        'total_count': total_count,
        'total_amount': total_amount
    })

# API endpoints

@api_view(['POST'])
@permission_classes([AllowAny])
def api_emergency_create(request):
    serializer = EmergencySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_donation_create(request):
    serializer = DonationSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_volunteer_assign(request):
    serializer = VolunteerAssignSerializer(data=request.data)
    if serializer.is_valid():
        vid = serializer.validated_data['volunteer_id']
        cid = serializer.validated_data['center_id']
        vol = Volunteer.objects.get(pk=vid)
        center = SupportCenter.objects.get(pk=cid)
        vol.assigned_center = center
        vol.save()
        return Response({'status': 'assigned'}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_support_centers_list(request):
    centers = SupportCenter.objects.all()
    serializer = SupportCenterSerializer(centers, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_hospitals_list(request):
    hospitals = Hospital.objects.all()
    serializer = HospitalSerializer(hospitals, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_dashboard_volunteer(request):
    try:
        volunteer = Volunteer.objects.get(user=request.user)
    except Volunteer.DoesNotExist:
        return Response({'error': 'Volunteer profile not found.'}, status=404)
    donations = Donation.objects.filter(via_volunteer=volunteer)
    data = {
        'assigned_center': volunteer.assigned_center and SupportCenterSerializer(volunteer.assigned_center).data or None,
        'donations': DonationSerializer(donations, many=True).data,
        'total_delivered': donations.count()
    }
    return Response(data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_dashboard_ngo(request):
    try:
        center = SupportCenter.objects.get(user=request.user)
    except SupportCenter.DoesNotExist:
        return Response({'error': 'Support center not found.'}, status=404)
    volunteers = Volunteer.objects.filter(assigned_center=center)
    donations = Donation.objects.filter(to_center=center)
    total_amount = donations.aggregate(models.Sum('amount'))['amount__sum'] or 0
    data = {
        'volunteers': [{'id': v.id, 'full_name': v.full_name, 'phone': v.phone} for v in volunteers],
        'donations': DonationSerializer(donations, many=True).data,
        'total_donations': donations.count(),
        'total_amount': total_amount
    }
    return Response(data)
