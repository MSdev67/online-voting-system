# voting/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

class VoterRegistrationForm(UserCreationForm):
    voter_id = forms.CharField(
        max_length=20,
        validators=[RegexValidator(r'^[A-Za-z0-9]+$', 'Only alphanumeric characters allowed.')]
    )
    aadhar_number = forms.CharField(
        max_length=12,
        validators=[RegexValidator(r'^\d{12}$', 'Enter valid 12-digit Aadhar number.')]
    )
    phone_number = forms.CharField(
        max_length=10,
        validators=[RegexValidator(r'^\d{10}$', 'Enter valid 10-digit phone number.')]
    )
    
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'voter_id', 'aadhar_number', 'phone_number']

class OTPVerificationForm(forms.Form):
    otp = forms.CharField(
        max_length=6,
        validators=[RegexValidator(r'^\d{6}$', 'Enter 6-digit OTP.')],
        widget=forms.TextInput(attrs={'autocomplete': 'off'})
    )

class LoginForm(forms.Form):
    voter_id = forms.CharField(max_length=20)
    aadhar_number = forms.CharField(max_length=12)
    phone_number = forms.CharField(max_length=10)