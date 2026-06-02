from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from appointments.models import Appointment
from doctors.models import Doctor, Specialty
from accounts.models import CustomUser
from datetime import date

@login_required
def index(request):
    if request.user.is_patient():
        return redirect('dashboard:patient')
    elif request.user.is_doctor():
        return redirect('dashboard:doctor')
    else:
        return redirect('dashboard:admin')

@login_required
def patient_dashboard(request):
    today = date.today()
    upcoming = Appointment.objects.filter(
        patient=request.user,
        date__gte=today
    ).exclude(status='cancelled').order_by('date', 'time')
    past = Appointment.objects.filter(
        patient=request.user,
        date__lt=today
    ).order_by('-date')
    cancelled = Appointment.objects.filter(
        patient=request.user,
        status='cancelled'
    ).order_by('-created_at')
    return render(request, 'dashboard/patient.html', {
        'upcoming': upcoming,
        'past': past,
        'cancelled': cancelled
    })

@login_required
def doctor_dashboard(request):
    try:
        doctor = request.user.doctor_profile
    except:
        return redirect('/')
    today = date.today()
    today_apts = Appointment.objects.filter(
        doctor=doctor, date=today
    ).exclude(status='cancelled').order_by('time')
    upcoming = Appointment.objects.filter(
        doctor=doctor, date__gt=today
    ).exclude(status='cancelled').order_by('date', 'time')
    total = Appointment.objects.filter(doctor=doctor).count()
    confirmed = Appointment.objects.filter(doctor=doctor, status='confirmed').count()
    cancelled = Appointment.objects.filter(doctor=doctor, status='cancelled').count()
    return render(request, 'dashboard/doctor.html', {
        'today_apts': today_apts,
        'upcoming': upcoming,
        'total': total,
        'confirmed': confirmed,
        'cancelled': cancelled,
        'doctor': doctor
    })

@login_required
def admin_dashboard(request):
    total_patients = CustomUser.objects.filter(role='patient').count()
    total_doctors = Doctor.objects.count()
    total_apts = Appointment.objects.count()
    by_status = {}
    for s, label in Appointment.STATUS_CHOICES:
        by_status[label] = Appointment.objects.filter(status=s).count()
    by_specialty = []
    for sp in Specialty.objects.all():
        count = Appointment.objects.filter(specialty=sp).count()
        by_specialty.append({'name': sp.name, 'count': count})
    return render(request, 'dashboard/admin.html', {
        'total_patients': total_patients,
        'total_doctors': total_doctors,
        'total_apts': total_apts,
        'by_status': by_status,
        'by_specialty': by_specialty
    })