# appointments/models.py
from django.db import models
from accounts.models import CustomUser
from doctors.models import Doctor, Specialty


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('confirmed', 'Confirmé'),
        ('cancelled', 'Annulé'),
        ('completed', 'Terminé'),
        ('absent', 'Absent'),
    ]

    patient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    specialty = models.ForeignKey(Specialty, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField()
    time = models.TimeField()
    reason = models.TextField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('doctor', 'date', 'time')
        ordering = ['-date', '-time']

    @property
    def receipt_code(self):
        """Code court lisible sur le bon de passage, sans ajouter de champ en base."""
        if self.pk:
            return f"MB-{self.date:%Y}-{self.pk:04d}"
        return f"MB-{self.date:%Y}-TEMP"

    @property
    def patient_name(self):
        full_name = self.patient.get_full_name()
        return full_name or self.patient.username

    @property
    def doctor_name(self):
        full_name = self.doctor.user.get_full_name()
        return full_name or self.doctor.user.username

    def __str__(self):
        return f"{self.patient_name} → Dr. {self.doctor_name} le {self.date} à {self.time}"
