# yourapp/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')
    family_name = forms.CharField(max_length=100, required=True, help_text='Required. Family name.')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'email', 'password1', 'password2', 'family_name')
