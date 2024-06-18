from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class SignUpForm(UserCreationForm):
    username = forms.CharField(max_length=150, required=True, help_text='必須。150文字以下。文字、数字、@/./+/-/_ のみ。')
    password1 = forms.CharField(widget=forms.PasswordInput, required=True, help_text='パスワードを入力してください。')
    password2 = forms.CharField(widget=forms.PasswordInput, required=True, help_text='確認のために再度パスワードを入力してください。')

    class Meta:
        model = CustomUser
        fields = ('username', 'password1', 'password2')
