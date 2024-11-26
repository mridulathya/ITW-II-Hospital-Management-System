from django import forms
from .models import Users

class DoctorSearch(forms.Form):
    specialisation = forms.CharField(max_length=100,required=True)
class LoginForm(forms.Form):
    email_id = forms.EmailField(max_length=255, required=True, widget=forms.EmailInput(attrs={'placeholder': 'Email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}), required=True)