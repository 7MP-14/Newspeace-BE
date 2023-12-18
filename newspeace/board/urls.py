from django.urls import path
from .import views

app_name = 'board'
urlpatterns = [
    # 유지보수를 위해 name 속성으로 URL에 이름을 지정해줌
    path('', views.list, name='list'),
    path('<int:id>/', views.detail, name='detail'),
    path('write/', views.write, name='write'),
    path('delete/<id>/', views.delete, name='delete'),
]