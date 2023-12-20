from django.urls import path
from rest_framework import routers
from . import views

app_name = 'notice'
urlpatterns = [
    path('', views.NoticeListAPIView.as_view(), name='notice_list'),
    path('<int:pk>/', views.NoticeRetrieveAPIView.as_view(), name="notice_detail"),
    path('create/', views.NoticeCreateAPIView.as_view(), name="notice_create"),
    path('<int:pk>/delete', views.NoticeDestroyAPIView.as_view(), name="notice_delete"),
]