from django.shortcuts import render, get_object_or_404
from .models import Doctor, Specialty


def doctor_list(request):
    doctors = Doctor.objects.filter(is_active=True).select_related('user').prefetch_related('specialties')
    specialties = Specialty.objects.all().order_by('name')

    q = request.GET.get('q', '').strip()
    specialty_id = request.GET.get('specialty', '').strip()
    specialty_name = request.GET.get('specialty_name', '').strip()

    if q:
        doctors = doctors.filter(user__first_name__icontains=q) | doctors.filter(user__last_name__icontains=q)

    if specialty_id:
        doctors = doctors.filter(specialties__id=specialty_id)
    elif specialty_name:
        doctors = doctors.filter(specialties__name__iexact=specialty_name)
        match = specialties.filter(name__iexact=specialty_name).first()
        if match:
            specialty_id = str(match.id)

    return render(request, 'doctors/list.html', {
        'doctors': doctors.distinct(),
        'specialties': specialties,
        'q': q,
        'selected_specialty': specialty_id,
        'selected_specialty_name': specialty_name,
    })


def doctor_detail(request, pk):
    doctor = get_object_or_404(Doctor.objects.select_related('user').prefetch_related('specialties'), pk=pk, is_active=True)
    return render(request, 'doctors/detail.html', {'doctor': doctor})
