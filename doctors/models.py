
from django.db import models
from accounts.models import CustomUser

class Specialty(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    keywords = models.TextField(blank=True, help_text="Mots-clés pour l'IA, séparés par des virgules")

    def __str__(self): return self.name

class Doctor(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='doctor_profile')
    specialties = models.ManyToManyField(Specialty, related_name='doctors')
    cabinet_address = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    years_experience = models.PositiveIntegerField(default=0)
    photo = models.ImageField(upload_to='doctors/', blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self): return f"Dr. {self.user.get_full_name()}"