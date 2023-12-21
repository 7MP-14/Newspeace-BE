from django.urls import path
from .import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('search/', views.search, name="news-search"),
    path('mynews/', views.newsScript, name="news-script"),
]