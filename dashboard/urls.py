from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.index, name='index'),
    path('patient/', views.patient_dashboard, name='patient'),
    path('doctor/', views.doctor_dashboard, name='doctor'),
    path('admin/', views.admin_dashboard, name='admin'),
]