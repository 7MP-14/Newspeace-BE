from django.shortcuts import render, redirect
from django.conf import settings
from .forms import *

def signup(request):
    if request.method=='POST':
        form=UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(settings.LOGIN_URL)
    else:
        form=UserCreationForm()
    return render(request,'registration/signup.html',{'form':form})

# class CustomLoginView(View):
#     form_class = EmailAuthenticationForm
#     template_name = 'registration/login.html'
#     success_url = '/'  # 로그인 성공 시 리디렉션할 URL

#     def get(self, request, *args, **kwargs):
#         form = self.form_class()
#         return render(request, self.template_name, {'form': form})

#     def post(self, request, *args, **kwargs):
#         form = self.form_class(request, request.POST)
#         if form.is_valid():
#             user = authenticate(request, email=form.cleaned_data['email'], password=form.cleaned_data['password'])
#             if user is not None:
#                 login(request, user)
#                 return redirect(self.success_url)
#         return render(request, self.template_name, {'form': form})