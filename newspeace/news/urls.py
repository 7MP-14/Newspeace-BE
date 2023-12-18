from django.urls import path
from .import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('detail/<str:category>/<str:keyword>/', views.detail,name='detail'),
]