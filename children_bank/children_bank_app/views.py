from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from django.contrib.auth.models import Group
from .forms import SignUpForm

class SignUpView(FormView):
    template_name = 'registration/signup.html'
    form_class = SignUpForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = form.save()
        
        # グループを作成または取得
        family_name = form.cleaned_data.get('family_name')
        group, created = Group.objects.get_or_create(name=family_name)
        
        # ユーザーをグループに追加
        user.groups.add(group)
        
        # ログイン
        login(self.request, user)
        
        return redirect(self.success_url)