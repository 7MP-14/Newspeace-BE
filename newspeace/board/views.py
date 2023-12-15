from django.shortcuts import render
from django.http import HttpResponse

def test1(request):
    return HttpResponse('board/test1 응답!')