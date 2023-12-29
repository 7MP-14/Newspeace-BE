import os
import django

# Django 프로젝트의 settings 모듈을 지정
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "newspeace.settings")  # 'your_project.settings'를 본인의 실제 프로젝트 설정 파일로 변경하세요
django.setup()

from django.test import RequestFactory
from news.views import realTimeRatio  # 여기에 본인이 정의한 view 함수를 import하세요
from datetime import datetime
def mykeyword_negative_update(day, hour):
# 가상의 request 생성
    factory = RequestFactory()
    request = factory.get(f'/news/realtimeratio/{day}/{hour}/')  # 호출하려는 URL을 지정하세요

    # view 함수 호출
    response = realTimeRatio(request, day=day, hour=hour)
    
    return response

# response = mykeyword_negative_update()
# print(response)
