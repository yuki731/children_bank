from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class ParentSignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    family_name = forms.CharField(max_length=100)

    class Meta:
        model = User
        fields = ('username', 'email', 'family_name', 'password1', 'password2')

class CreateUserForm(forms.ModelForm):
    FAMILY_ROLE_CHOICES = [
        ('parent', 'Parent'),
        ('child', 'Child'),
    ]
    
    role = forms.ChoiceField(choices=FAMILY_ROLE_CHOICES, help_text='Select whether this user is a parent or a child')
    
    class Meta:
        model = User
        fields = ('username', 'password', 'role')
        widgets = {
            'password': forms.PasswordInput()
        }