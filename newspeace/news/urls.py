from django.urls import path
from . import views


urlpatterns = [
    path('search/', views.search, name="news-search"),
    path('newsscript/', views.newsScript, name="news-script"),
    path('mynewsscript/<int:no>/', views.MyNewsScript, name="mynews-script"),
    path('realtimeratio/<int:day>/<int:hour>/', views.realTimeRatio),
    path('delete/<int:no>/', views.MyNewsDelete),
    path('kakao-news/', views.search_kakao),
    path('db/', views.db_keyword),
    
]