# schedules/models.py
from django.db import models
from doctors.models import Doctor

class Availability(models.Model):
    DAY_CHOICES = [(i, day) for i, day in enumerate(
        ['Lundi','Mardi','Mercredi','Jeudi','Vendredi','Samedi','Dimanche'])]
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='availabilities')
    day_of_week = models.IntegerField(choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    slot_duration = models.IntegerField(default=30, help_text="Durée en minutes")
    is_active = models.BooleanField(default=True)

class UnavailablePeriod(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.CharField(max_length=100, blank=True)