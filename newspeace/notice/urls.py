from django.urls import path
from rest_framework import routers
from . import views

app_name = 'notice'
urlpatterns = [
    path('', views.NoticeListAPIView.as_view(), name='notice_list'),                        # 게시판 목록, 게시글 세부
    path('create/', views.NoticeCreateAPIView.as_view(), name="notice_create"),             # 게시글 추가
    path('<int:pk>/', views.NoticeRetrieveUpdateAPIView.as_view(), name="notice_update"),   # 게시글 수정
    path('<int:pk>/delete/', views.NoticeDestroyAPIView.as_view(), name="notice_delete"),   # 게시글 삭제
]