from django.shortcuts import render
from django.http import JsonResponse
from .models import *

# Create your views here.

def detail(request, category, keyword):
    category = category.split('+')
    keyword = keyword.split('+')
    
    keyword_ins = Keywords.objects.filter(keyword=keyword)[0]
    articles = keyword_ins.article.filter(category__in=category)
    title_list = []
    url_list = []
    imageUrl_list = []
    
    for article in articles:
        title_list.append(article.title)
        url_list.append(article.articleUrl)
        imageUrl_list.append(article.articleImgUrl)
    
    news_list = {'title' : title_list, 'articleUrl_list' : url_list, 'imageUrl_list' : imageUrl_list}
    
    return JsonResponse(data=news_list, status=200)
    
    