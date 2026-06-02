from datetime import date, timedelta
from io import BytesIO
import base64

import qrcode
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.dateparse import parse_date
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from doctors.models import Doctor, Specialty
from .models import Appointment
from .utils import get_available_slots


def _slots_by_date_for_doctor(doctor, days=14):
    """Prépare les créneaux disponibles des prochains jours pour l'affichage."""
    slots_by_date = {}
    for i in range(1, days + 1):
        d = date.today() + timedelta(days=i)
        slots = get_available_slots(doctor, d)
        if slots:
            slots_by_date[d] = slots
    return slots_by_date


def _create_appointment_from_request(request, doctor):
    selected_date = request.POST.get('date')
    selected_time = request.POST.get('time')
    reason = request.POST.get('reason', '').strip()
    specialty_id = request.POST.get('specialty')

    if not selected_date or not selected_time or not reason:
        messages.error(request, "Veuillez choisir un médecin, un créneau et saisir le motif de consultation.")
        return False

    parsed_date = parse_date(selected_date)
    if not parsed_date:
        messages.error(request, "La date choisie est invalide.")
        return False

    available_times = [slot.strftime('%H:%M') for slot in get_available_slots(doctor, parsed_date)]
    if selected_time not in available_times:
        messages.error(request, "Ce créneau n'est plus disponible. Merci de choisir un autre horaire.")
        return False

    specialty = doctor.specialties.first()
    if specialty_id:
        selected_specialty = doctor.specialties.filter(pk=specialty_id).first()
        if selected_specialty:
            specialty = selected_specialty

    try:
        appointment = Appointment.objects.create(
            patient=request.user,
            doctor=doctor,
            specialty=specialty,
            date=selected_date,
            time=selected_time,
            reason=reason,
            status='pending'
        )
        messages.success(request, "Rendez-vous réservé avec succès. Imprimez ou téléchargez le bon de passage pour l’accueil ou la caisse.")
        return appointment
    except IntegrityError:
        messages.error(request, "Ce créneau vient d’être réservé. Merci de choisir un autre horaire.")
        return False


def _can_view_appointment(user, appointment):
    if user.is_staff or user.is_admin_user():
        return True
    if appointment.patient_id == user.id:
        return True
    if user.is_doctor() and appointment.doctor.user_id == user.id:
        return True
    return False


def _appointment_qr_payload(appointment):
    return (
        f"MediBook\n"
        f"Code: {appointment.receipt_code}\n"
        f"Patient: {appointment.patient_name}\n"
        f"Médecin: Dr. {appointment.doctor_name}\n"
        f"Spécialité: {appointment.specialty.name if appointment.specialty else 'Non précisée'}\n"
        f"Date: {appointment.date:%d/%m/%Y}\n"
        f"Heure: {appointment.time.strftime('%H:%M')}\n"
        f"Motif: {appointment.reason}"
    )


def _appointment_qr_png_bytes(appointment):
    qr = qrcode.QRCode(version=1, box_size=8, border=2)
    qr.add_data(_appointment_qr_payload(appointment))
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    return buffer.getvalue()


def _appointment_qr_base64(appointment):
    return base64.b64encode(_appointment_qr_png_bytes(appointment)).decode('utf-8')


@login_required
def appointment_ticket(request, pk):
    appointment = get_object_or_404(
        Appointment.objects.select_related('patient', 'doctor__user', 'specialty'),
        pk=pk
    )
    if not _can_view_appointment(request.user, appointment):
        messages.error(request, "Vous n’avez pas accès à ce bon de passage.")
        return redirect('dashboard:index')
    return render(request, 'appointments/ticket.html', {
        'appointment': appointment,
        'qr_code_base64': _appointment_qr_base64(appointment),
    })


@login_required
def appointment_ticket_pdf(request, pk):
    appointment = get_object_or_404(
        Appointment.objects.select_related('patient', 'doctor__user', 'specialty'),
        pk=pk
    )
    if not _can_view_appointment(request.user, appointment):
        messages.error(request, "Vous n’avez pas accès à ce bon de passage.")
        return redirect('dashboard:index')

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="bon_passage_{appointment.receipt_code}.pdf"'

    pdf = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # Header
    pdf.setTitle(f"Bon de passage {appointment.receipt_code}")
    pdf.setFont("Helvetica-Bold", 22)
    pdf.drawString(50, height - 60, "MediBook")
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, height - 90, "BON DE PASSAGE")
    pdf.setFont("Helvetica", 11)
    pdf.drawString(50, height - 110, "À présenter à l’accueil / à la caisse avant la consultation")

    # Code box
    pdf.roundRect(width - 220, height - 105, 160, 45, 10, stroke=1, fill=0)
    pdf.setFont("Helvetica", 9)
    pdf.drawString(width - 205, height - 78, "Code rendez-vous")
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(width - 205, height - 95, appointment.receipt_code)

    # Main info box
    y_top = height - 150
    pdf.roundRect(45, y_top - 290, width - 90, 280, 14, stroke=1, fill=0)

    lines = [
        ("Patient", appointment.patient_name),
        ("Téléphone", appointment.patient.phone or "Non renseigné"),
        ("Email", appointment.patient.email or "Non renseigné"),
        ("Médecin", f"Dr. {appointment.doctor_name}"),
        ("Spécialité", appointment.specialty.name if appointment.specialty else "Non précisée"),
        ("Cabinet", appointment.doctor.cabinet_address or "Adresse non renseignée"),
        ("Date", appointment.date.strftime('%d/%m/%Y')),
        ("Heure", appointment.time.strftime('%H:%M')),
        ("Statut", appointment.get_status_display()),
        ("Motif", appointment.reason),
    ]

    x1, x2 = 65, 310
    y = y_top - 30
    pdf.setFont("Helvetica", 11)
    for index, (label, value) in enumerate(lines):
        current_x = x1 if index < 5 else x2
        current_y = y - (index % 5) * 42
        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawString(current_x, current_y, f"{label} :")
        pdf.setFont("Helvetica", 10)
        text_value = str(value)
        max_chars = 28 if label == "Motif" else 30
        wrapped = [text_value[i:i+max_chars] for i in range(0, len(text_value), max_chars)] or [""]
        for line_idx, line in enumerate(wrapped[:3]):
            pdf.drawString(current_x + 70, current_y - (line_idx * 12), line)

    # QR code box
    qr_png = _appointment_qr_png_bytes(appointment)
    qr_img = ImageReader(BytesIO(qr_png))
    pdf.roundRect(50, 180, 180, 160, 12, stroke=1, fill=0)
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(65, 320, "QR code")
    pdf.setFont("Helvetica", 10)
    pdf.drawString(65, 306, "Scan à l’accueil pour vérification rapide")
    pdf.drawImage(qr_img, 70, 205, width=110, height=110, preserveAspectRatio=True, mask='auto')

    # Steps box
    pdf.roundRect(250, 180, width - 300, 160, 12, stroke=1, fill=0)
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(265, 320, "Étapes")
    pdf.setFont("Helvetica", 10)
    steps = [
        "1. Présentez le bon à l’accueil.",
        "2. Passez à la caisse si nécessaire.",
        "3. Conservez ce document jusqu’à la consultation.",
        "4. Arrivez idéalement 10 minutes avant l’heure prévue.",
    ]
    step_y = 300
    for step in steps:
        pdf.drawString(270, step_y, step)
        step_y -= 22

    # Footer note
    pdf.setFont("Helvetica", 9)
    pdf.drawString(50, 145, f"Bon généré automatiquement par MediBook — {appointment.receipt_code}")
    pdf.drawString(50, 132, "Ce document ne remplace pas un justificatif médical officiel.")

    pdf.showPage()
    pdf.save()
    return response


@login_required
def dynamic_booking(request):
    """Page dynamique : spécialité → médecins → créneaux → confirmation."""
    if request.method == 'POST':
        doctor_id = request.POST.get('doctor')
        doctor = get_object_or_404(Doctor, pk=doctor_id, is_active=True)
        appointment = _create_appointment_from_request(request, doctor)
        if appointment:
            return redirect('appointments:ticket', pk=appointment.pk)
        return redirect('appointments:new')

    specialties = Specialty.objects.order_by('name')
    doctors = Doctor.objects.filter(is_active=True).select_related('user').prefetch_related('specialties').order_by('user__first_name')
    return render(request, 'appointments/dynamic_book.html', {
        'specialties': specialties,
        'doctors': doctors,
    })


@login_required
def book_appointment(request, doctor_pk):
    doctor = get_object_or_404(Doctor, pk=doctor_pk, is_active=True)
    slots_by_date = _slots_by_date_for_doctor(doctor)

    if request.method == 'POST':
        appointment = _create_appointment_from_request(request, doctor)
        if appointment:
            return redirect('appointments:ticket', pk=appointment.pk)
        return redirect('appointments:book', doctor_pk=doctor.pk)

    return render(request, 'appointments/book.html', {
        'doctor': doctor,
        'slots_by_date': slots_by_date
    })


@login_required
def api_doctors(request):
    specialty_id = request.GET.get('specialty')
    doctors = Doctor.objects.filter(is_active=True).select_related('user').prefetch_related('specialties')
    if specialty_id:
        doctors = doctors.filter(specialties__id=specialty_id)

    data = []
    for doctor in doctors.distinct().order_by('user__first_name'):
        data.append({
            'id': doctor.id,
            'name': doctor.user.get_full_name() or doctor.user.username,
            'specialties': [sp.name for sp in doctor.specialties.all()],
            'address': doctor.cabinet_address or 'Adresse non renseignée',
            'experience': doctor.years_experience,
            'description': doctor.description or 'Médecin disponible pour consultation.',
        })
    return JsonResponse({'doctors': data})


@login_required
def api_slots(request):
    doctor_id = request.GET.get('doctor')
    doctor = get_object_or_404(Doctor, pk=doctor_id, is_active=True)
    grouped_slots = []
    for d, slots in _slots_by_date_for_doctor(doctor).items():
        grouped_slots.append({
            'date': d.isoformat(),
            'label': d.strftime('%d/%m/%Y'),
            'weekday': d.strftime('%A'),
            'slots': [slot.strftime('%H:%M') for slot in slots]
        })
    return JsonResponse({'slots_by_date': grouped_slots})


@login_required
def cancel_appointment(request, pk):
    apt = get_object_or_404(Appointment, pk=pk, patient=request.user)
    if apt.status in ['pending', 'confirmed']:
        apt.status = 'cancelled'
        apt.save()
        messages.success(request, "Rendez-vous annulé.")
    return redirect('dashboard:patient')


@login_required
def update_status(request, pk, status):
    allowed_statuses = {'confirmed', 'completed', 'cancelled', 'absent'}
    if status not in allowed_statuses:
        messages.error(request, "Statut invalide.")
        return redirect('dashboard:doctor')
    apt = get_object_or_404(Appointment, pk=pk)
    if not request.user.is_doctor() or apt.doctor.user != request.user:
        messages.error(request, "Action non autorisée.")
        return redirect('dashboard:index')
    apt.status = status
    apt.save()
    messages.success(request, "Statut du rendez-vous mis à jour.")
    return redirect('dashboard:doctor')
