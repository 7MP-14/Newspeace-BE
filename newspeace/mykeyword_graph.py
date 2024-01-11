import os
import django


# Django 프로젝트의 settings 모듈을 지정
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "newspeace.settings")  
django.setup()

from django.test import RequestFactory
from news.views import realTimeRatio 
from enterprise.views import realTimeGraph

def mykeyword_negative_update(day, hour):

    factory = RequestFactory()
    request = factory.get(f'/news/realtimeratio/{day}/{hour}/')  

    # view 함수 호출
    response = realTimeRatio(request, day=day, hour=hour)
    
    return response


def enterprise_update(day, hour):

    factory = RequestFactory()
    request = factory.get(f'/enterprise/realtimegraph/{day}/{hour}/')  

    # view 함수 호출
    response = realTimeGraph(request, day=day, hour=hour)
    
    return response
