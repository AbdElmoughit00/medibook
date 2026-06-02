# patients/models.py
from django.db import models
from accounts.models import CustomUser

class PatientProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='patient_profile')
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.CharField(max_length=255, blank=True)

    def __str__(self): return self.user.get_full_name()