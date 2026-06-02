from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from patients.models import PatientProfile
from .forms import PatientRegistrationForm


def register_view(request):
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            PatientProfile.objects.get_or_create(user=user)
            login(request, user)
            return redirect('dashboard:index')
    else:
        form = PatientRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('dashboard:index')
    else:
        form = AuthenticationForm()
    for field in form.fields.values():
        field.widget.attrs.update({'class': 'form-control'})
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')
