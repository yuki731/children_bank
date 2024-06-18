from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import SignUpForm

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')  # 適切なリダイレクト先に変更してください
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})
