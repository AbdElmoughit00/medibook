from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('new/', views.dynamic_booking, name='new'),
    path('api/doctors/', views.api_doctors, name='api_doctors'),
    path('api/slots/', views.api_slots, name='api_slots'),
    path('book/<int:doctor_pk>/', views.book_appointment, name='book'),
    path('ticket/<int:pk>/', views.appointment_ticket, name='ticket'),
    path('ticket/<int:pk>/pdf/', views.appointment_ticket_pdf, name='ticket_pdf'),
    path('cancel/<int:pk>/', views.cancel_appointment, name='cancel'),
    path('status/<int:pk>/<str:status>/', views.update_status, name='update_status'),
]
