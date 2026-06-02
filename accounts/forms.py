from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class PatientRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=True, label='Prénom')
    last_name = forms.CharField(max_length=50, required=True, label='Nom')
    email = forms.EmailField(required=True, label='Email')
    phone = forms.CharField(max_length=20, required=False, label='Téléphone')

    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email', 'phone', 'password1', 'password2')
        labels = {'username': "Nom d'utilisateur"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].help_text = ''
        self.fields['password2'].help_text = ''

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'patient'
        if commit:
            user.save()
        return user
