# app_admin/forms.py
from django import forms
from accounts.models import Registration

class RegistrationForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = '__all__'
