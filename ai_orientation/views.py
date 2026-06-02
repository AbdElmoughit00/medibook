from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .ml_model import get_specialty_recommendations, SPECIALTIES_DATA


@login_required
def orientation_view(request):
    ai_result = None
    symptom_text = ''
    duration = ''
    intensity = ''
    age_group = ''

    if request.method == 'POST':
        symptom_text = request.POST.get('symptoms', '').strip()
        duration = request.POST.get('duration', '').strip()
        intensity = request.POST.get('intensity', '').strip()
        age_group = request.POST.get('age_group', '').strip()

        if symptom_text:
            ai_result = get_specialty_recommendations(
                symptom_text=symptom_text,
                duration=duration,
                intensity=intensity,
                age_group=age_group,
            )

    return render(request, 'ai_orientation/form.html', {
        'ai_result': ai_result,
        'recommendations': ai_result['recommendations'] if ai_result else [],
        'symptom_text': symptom_text,
        'duration': duration,
        'intensity': intensity,
        'age_group': age_group,
        'available_specialties_count': len(SPECIALTIES_DATA),
    })
