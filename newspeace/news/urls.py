from django.urls import path
from .import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('search/', views.search, name="news-search"),
    path('newsscript/', views.newsScript, name="news-script"),
    path('mynewsscript/', views.MyNewsScript, name="mynews-script")
]