from django.shortcuts import render, redirect
from django.conf import settings
from .forms import *
from .models import *

def signup(request):
    if request.method=='POST':
        form=UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(settings.LOGIN_URL)
    else:
        form=UserCreationForm()
    return render(request,'registration/signup.html',{'form':form})

def update(request):
    if request.method=='POST':
        form=UserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('/')
    else:
        form=UserChangeForm(instance=request.user)
    return render(request,'registration/update.html',{'form':form})
