from django.urls import path
from .import views
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from .views import *

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(),name='login'),
    path('logout/', auth_views.LogoutView.as_view(),name='logout'),
    path('signup/',views.signup, name='signup'),
    path('update/',views.update, name='update'),
    path('profile/',TemplateView.as_view(template_name='registration/profile.html'), name='profile'),
]


