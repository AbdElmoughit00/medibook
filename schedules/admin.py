from django.contrib import admin
from .models import Availability, UnavailablePeriod

@admin.register(Availability)
class AvailabilityAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'day_of_week', 'start_time', 'end_time', 'slot_duration', 'is_active')
    list_filter = ('day_of_week', 'is_active')

@admin.register(UnavailablePeriod)
class UnavailablePeriodAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'start_date', 'end_date', 'reason')
    list_filter = ('start_date', 'end_date')
