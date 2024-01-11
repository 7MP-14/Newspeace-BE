from django.urls import path
from . import views


urlpatterns = [
    path('', views.enterpriseList, name='enterprise_list_name'),
    path('realtimegraph/<int:day>/<int:hour>/', views.realTimeGraph),
]