from django.urls import path
from . import views
# from . import test_1227  # 테스트_1227


urlpatterns = [
    path('search/', views.search, name="news-search"),
    path('newsscript/', views.newsScript, name="news-script"),
    path('mynewsscript/<int:no>/', views.MyNewsScript, name="mynews-script"),
    path('realtimeratio/<int:day>/<int:hour>/', views.realTimeRatio),
    path('delete/<int:id>/<int:no>/', views.MyNewsDelete),
    # path('test3/', test_1226.realTimeRatio22, name="teset3"),  # 테스트_1226
    path('test2/', views.search2222),  # 테스트_1227
    
]