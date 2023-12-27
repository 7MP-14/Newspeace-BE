from django.shortcuts import render
from .models import *
from django.http import HttpResponse, JsonResponse
import csv
import pandas as pd
from preprocess import process_news_keyword
from preprocess_version2 import process_news_paragraph_kakao
from django.views.decorators.csrf import csrf_exempt
import json


# # Create your views here.
        
@csrf_exempt
def search(request):
    data = json.loads(request.body)
    search_keyword = data.get('keyword')
    search_category_list = data.get('category')
    print(data.get('keyword'))
    print(data.get('category'))
    
    # search_keyword = '삼성'
    # search_category_list = ['사회']
    
    # KeywordCount 테이블 입력 단어 cnt 수정
    try:
        key_cnt = KeywordCount.objects.get(name=search_keyword)
        key_cnt.count += 1
        key_cnt.save()
    except KeywordCount.DoesNotExist:
        key_cnt = KeywordCount.objects.create(name=search_keyword, count=1)

    
    cate_articles = Article.objects.filter(category__in=search_category_list)
    key_cate_articles = cate_articles.filter(detail__icontains=search_keyword)

    if key_cate_articles:
        fields = ['id', 'title','detail', 'link', 'img']
        article_list = list(key_cate_articles.values(*fields))
        df = pd.DataFrame(article_list)
        df = df.iloc[:10, :]

        result_df, postive = process_news_keyword(df, search_keyword)
        
        json_data = {
        "긍정": result_df[result_df['sentiment'] == 1].to_dict(orient='records'),  
        "부정": result_df[result_df['sentiment'] == 0].to_dict(orient='records'),
        }
        
        # json_data = {
        # "긍정": df[df['id'] > 15000].to_dict(orient='records'),  
        # "부정": df[df['id'] < 15000].to_dict(orient='records'),
        # }
        
        return JsonResponse({'article': json_data, '긍정도':postive, '부정도' : (100-postive), 'keyword' : search_keyword})
        # return JsonResponse({'article': json_data, 'keyword' : search_keyword})

    else:
        return JsonResponse({'reply' : f"죄송합니다. {search_keyword}에 해당하는 뉴스 기사를 찾을 수 없습니다. 카테고리 재설정 또는 검색 단어를 수정해주세요."})


# 인기 검색어 조회
def hot_keyword(request):
    if request.method == "GET":
        keywords = KeywordCount.objects.order_by('-count')[:10]
        hot_keyword = []
        
        for i in keywords:
            hot_keyword.append(i.name)
            
    return JsonResponse({'hot_keyword' : hot_keyword})


# 기사 스크립트 누르면 db에 저장
@csrf_exempt
def newsScript(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_id = data.get('userId')
        news_id = data.get('newsId')

        try:
            article = Article.objects.get(id=news_id)
            user = User.objects.get(id=user_id)
        except Article.DoesNotExist:
            return JsonResponse({'return': '일치하는 기사가 없습니다.'})
        except User.DoesNotExist:
            return JsonResponse({'return': '일치하는 회원이 없습니다.'})

        try:
            mynews = MyNews.objects.get(newsid=news_id)
            return JsonResponse({'return': '스크립트 한 뉴스입니다.'})
        except MyNews.DoesNotExist:
            mynews = MyNews.objects.create(newsid=news_id, title=article.title, link=article.link, img=article.img)
            mynews.user.add(user)
            return JsonResponse({"return": "성공"})

        

# 기사 스크립트 확인하기
def MyNewsScript(request, no):
    if request.method == 'GET':
        
        user = User.objects.get(id=no)
        mynews = user.mynews_set.all()
        
        result = []
        for news in mynews:
            news_dict = {
                'title': news.title,
                'link': news.link,
                'img': news.img
            }
            result.append(news_dict)
        
        return JsonResponse({'myNews_script' : result})


# 키워드 구독한거, 필터링해서, ratio 구해서 1. update // 2. 새로운 db에 축적하기
# def realTimeRatio():



# db 데이터 csv 저장하기
# def test(request):
#     test = Article.objects.filter(id__lte=15000)
    
#     if test:
#         fields = ['id', 'title','detail', 'link', 'img']
#         article_list = list(test.values(*fields))
#         df = pd.DataFrame(article_list)

#     df.to_csv('test.csv')
#     return HttpResponse('heelo')

# sample 데이터 db에 삽입
# def import_csv_to_db(request):
#     csv_file_path = 'data.csv'

#     # CSV 파일 읽기
#     with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
#         reader = csv.DictReader(csvfile)
#         for row in reader:
#             new_instance = Article(**row)  # CSV 데이터로 새로운 모델 인스턴스 생성
#             new_instance.save()  # 데이터베이스에 저장

#     return HttpResponse("Data imported successfully")  # 성공적으로 데이터를 데이터베이스에 추가했음을 알리는 응답


