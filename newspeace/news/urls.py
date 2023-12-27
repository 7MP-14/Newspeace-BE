from django.urls import path
from .import views

urlpatterns = [
    path('search/', views.search, name="news-search"),
    path('newsscript/', views.newsScript, name="news-script"),
    path('mynewsscript/<int:no>/', views.MyNewsScript, name="mynews-script"),
    # path('test/', views.test),
]