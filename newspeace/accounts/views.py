from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.conf import settings
from .forms import *
from django.contrib.auth.views import LoginView

def signup(request):
    if request.method=='POST':
        form=CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(settings.LOGIN_URL)
    else:
        form=CustomUserCreationForm()
    return render(request,'registration/signup.html',{'form':form})

class CustomLoginView(LoginView):
    authentication_form = EmailAuthenticationForm
    template_name = 'registration/login.html'