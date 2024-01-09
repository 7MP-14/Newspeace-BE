from django.urls import path
from . import views


urlpatterns = [
    path('', views.enterpriseList, name='enterprise_list_name'),
    path('add/', views.enterpiseAdd, name='enterprise_add'),
    path('delete/', views.delete),
    path('modify/', views.enterpriseCode),
    path('realtimegraph/<int:day>/<int:hour>/', views.realTimeGraph),
]