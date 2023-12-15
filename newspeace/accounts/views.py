from django.shortcuts import render
from django.http import HttpResponse

def test1(request):
    return HttpResponse('accounts/test1 응답!')
