from datetime import datetime, timedelta
from schedules.models import Availability, UnavailablePeriod
from .models import Appointment

def get_available_slots(doctor, date):
    """Retourne les créneaux libres pour un médecin à une date donnée."""
    weekday = date.weekday()
    availabilities = Availability.objects.filter(
        doctor=doctor, day_of_week=weekday, is_active=True
    )
    # Vérifie si le médecin est en congé
    unavailable = UnavailablePeriod.objects.filter(
        doctor=doctor, start_date__lte=date, end_date__gte=date
    )
    if unavailable.exists():
        return []

    booked_times = set(
        Appointment.objects.filter(
            doctor=doctor, date=date
        ).exclude(status='cancelled').values_list('time', flat=True)
    )

    slots = []
    for avail in availabilities:
        current = datetime.combine(date, avail.start_time)
        end = datetime.combine(date, avail.end_time)
        delta = timedelta(minutes=avail.slot_duration)
        while current + delta <= end:
            if current.time() not in booked_times:
                slots.append(current.time())
            current += delta
    return slots