from django.contrib import admin
from .models import Doctor, Specialty

@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_active')
    list_filter = ('is_active', 'specialties')