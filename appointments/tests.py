from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import CustomUser
from doctors.models import Doctor, Specialty
from appointments.models import Appointment
from datetime import date

class AppointmentTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.patient = CustomUser.objects.create_user(
            username='patient1', password='pass123', role='patient'
        )
        doc_user = CustomUser.objects.create_user(
            username='doc1', password='pass123', role='doctor'
        )
        self.specialty = Specialty.objects.create(name='Cardiologie')
        self.doctor = Doctor.objects.create(user=doc_user)
        self.doctor.specialties.add(self.specialty)

    def test_appointment_creation(self):
        apt = Appointment.objects.create(
            patient=self.patient, doctor=self.doctor,
            specialty=self.specialty, date=date.today(),
            time='10:00', reason='Test', status='pending'
        )
        self.assertEqual(apt.status, 'pending')

    def test_no_duplicate_slot(self):
        Appointment.objects.create(
            patient=self.patient, doctor=self.doctor,
            specialty=self.specialty, date=date.today(),
            time='10:00', reason='Test', status='pending'
        )
        with self.assertRaises(Exception):
            Appointment.objects.create(
                patient=self.patient, doctor=self.doctor,
                specialty=self.specialty, date=date.today(),
                time='10:00', reason='Test2', status='pending'
            )

    def test_cancel_requires_login(self):
        response = self.client.get(reverse('appointments:cancel', args=[1]))
        self.assertRedirects(response, '/accounts/login/?next=/appointments/cancel/1/')