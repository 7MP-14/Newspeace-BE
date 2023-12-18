from django.shortcuts import render
from django.http import HttpResponse
from .models import *

def test1(request):
    return HttpResponse('board/test1 응답!')

# Board 전체 목록 보기
def list(request):
    board_list = Board.objects.all()
    return render(request, 'board/list.html', {'board_all':board_list}) # HttpRequest()로 list.html 템플릿 페이지를 Response의 body에 응답

# # Form 기반으로 Board Data 추가 작업
def write(request):
    return render(request, 'board/write.html')