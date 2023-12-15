from django.urls import path
from .import views

app_name = 'board'
urlpatterns = [
    # 유지보수를 위해 name 속성으로 URL에 이름을 지정해줌
    path('', views.test1, name='test1'),                  # http://localhost:8000/board/
    path('test1/',views.test1),
]