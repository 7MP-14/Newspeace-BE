from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import *
from accounts.models import *
from keyword_model import extract_and_assign_keywords
from enterprise.models import *
from api import utils

import random
import pandas as pd
import json
from datetime import datetime, timedelta
from collections import Counter


# Create your views here.

# 검색에 대한 결과 response 함수
@csrf_exempt
def search(request):
    data = json.loads(request.body)              # request를 json형태로 load
    search_keyword = data.get('keyword')         # keyword 인자 추출 (프론트의 요청에 포함되어 있는)
    search_category_list = data.get('category')  # category 인자 추출 (프론트의 요청에 포함되어 있는)
    
    # KeywordCount 테이블 입력 단어 cnt 수정
    try:
        key_cnt = KeywordCount.objects.get(name=search_keyword)
        key_cnt.count += 1
        key_cnt.save()
    except KeywordCount.DoesNotExist:  # 해당 키워드가 db에 존재하지 않을 경우 새롭게 insert
        key_cnt = KeywordCount.objects.create(name=search_keyword, count=1)

    # 사용자가 카테고리를 입력했을 경우
    if search_category_list:
        cate_articles = Article.objects.filter(category__in=search_category_list)   # 카테고리 필터링
        key_cate_articles = cate_articles.filter(title__icontains=search_keyword)  # 키워드 필터링
    else:
        key_cate_articles = Article.objects.filter(title__icontains=search_keyword)

    # 키워드에 해당하는 기사가 있을 경우
    if key_cate_articles:
        fields = ['id', 'title','detail', 'link', 'img', 'write_dt', 'sentiment', 'keywords']
        article_list = list(key_cate_articles.values(*fields))
        result_df = pd.DataFrame(article_list)

        positive_len = len(result_df[result_df['sentiment'] == 1])
        negative_len = len(result_df[result_df['sentiment'] == -1])
        negative_percentage = (negative_len/(positive_len+negative_len)) * 100
        negative = round(negative_percentage, 1)
        postitive = round((100-negative), 1)
        
        # 연관검색어 추출
        def related_keyword_extraction(df,word):
            
            all_keywords = []
            for keywords in df.keywords:
                if len(keywords) == 1:
                    keywords = keywords[0]
                    
                all_keywords.extend(keywords)

            # 각 키워드 별 기사 수 집계
            keyword_counter = Counter(all_keywords)

            # 가장 많이 등장하는 상위 N개 키워드 추출
            top_n = 6
            topiclist = [item[0] for item in keyword_counter.most_common(top_n)]
            topiclist.remove(word)
            
            if len(topiclist) == 6:
                topiclist = topiclist[:5]
            
            return topiclist
        
        related_keyword = related_keyword_extraction(result_df, search_keyword)
        
        
        target = ['keywords']
        result_df.drop(columns=target, inplace=True)
        
        positive_df = result_df[result_df['sentiment'] == 1]
        negative_df = result_df[result_df['sentiment'] == -1]
        
        # 검색 기사 데이터
        json_data = {
        "긍정": positive_df.to_dict(orient='records'),  
        "부정": negative_df.to_dict(orient='records'),
        }
        

        return JsonResponse({'article': json_data, '긍정도':postitive, '부정도' : negative, 'search_keyword' : search_keyword, 'related_keyword' : related_keyword})

    else:  # 키워드에 해당하는 기사가 없을 경우
        return JsonResponse({'reply' : False})


# 인기 검색어 조회
def hot_keyword(request):
    if request.method == "GET":
        
        keywords = KeywordCount.objects.order_by('-count')[:10]
        hot_keyword = []
        
        for i in keywords:
            hot_keyword.append(i.name)
        
        time_now = datetime.now()
        articles = Article.objects.filter(create_dt__day=time_now.day, create_dt__hour=time_now.hour)
        if not articles:
            now_hour_ago = time_now - timezone.timedelta(hours=1)
            articles = Article.objects.filter(create_dt__day=now_hour_ago.day, create_dt__hour=now_hour_ago.hour)
            
        all_keywords = []
        for article in articles:
            all_keywords.extend(article.keywords)

        # 각 키워드 별 기사 수 집계
        keyword_counter = Counter(all_keywords)

        # 가장 많이 등장하는 상위 N개 키워드 추출
        top_n = 5
        topiclist = [item[0] for item in keyword_counter.most_common(top_n)]
        

        matching_articles = {}
        for keyword in topiclist:
            articles_with_keyword = Article.objects.filter(keywords__contains=keyword)
            
            if articles_with_keyword.exists():
                random_articles = random.sample(list(articles_with_keyword), 5)
                matching_articles[keyword] = [
                    {
                        'title': article.title,
                        'link' : article.link,
                    }
                    for article in random_articles
                ]

    return JsonResponse({'hot_search_keyword' : hot_keyword, 'hot_5_keyword' : topiclist,'hot_5_keyword_info': matching_articles})


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
        

# 스크립트 한 기사 삭제하기
@csrf_exempt
def MyNewsDelete(request, no):
    if request.method == 'DELETE':
        mynews = MyNews.objects.get(id=no)
        
        try:
            mynews.delete()
            return JsonResponse({'return': '삭제 완료'})
        except Exception as e:
            return JsonResponse({'return': '삭제 실패', 'error': str(e)})
        

# 기사 스크립트 확인하기
def MyNewsScript(request, no):
    if request.method == 'GET':
        user = User.objects.get(id=no)
        mynews = user.mynews_set.all()
        
        result = []
        for news in mynews:
            news_dict = {
                'id' : news.id,
                'title': news.title,
                'link': news.link,
                'img': news.img,
                'time' : news.save_dt
            }
            result.append(news_dict)
        
        return JsonResponse({'myNews_script' : result})


# 구독 키워드 부정도 최신화
def realTimeRatio(request, day, hour):
    if request.method == 'GET':
        keyword_queryset = Keyword.objects.all()
        keyword_list = [keyword.keyword_text for keyword in keyword_queryset]

        for keyword in keyword_list:
            key_cate_articles = Article.objects.filter(create_dt__day=day, create_dt__hour=hour, detail__icontains=keyword)

            if key_cate_articles:  # 키워드에 해당하는 기사가 있을 경우
                fields = ['sentiment']
                article_list = list(key_cate_articles.values(*fields))
                df = pd.DataFrame(article_list)
            
                positive_len = len(df[df['sentiment'] == 1])
                negative_len = len(df[df['sentiment'] == -1])
                
                if negative_len != 0:
                    negative_percentage = (negative_len/(positive_len+negative_len)) * 100
                    negative = round(negative_percentage, 1)
                else:
                    negative = 0
            else:
                negative = 0    
                
            # 부정도 최신화
            target_keyword = Keyword.objects.get(keyword_text=keyword)
            target_keyword.ratio = negative
            target_keyword.save()
     
        return JsonResponse({'return' : '성공'})


# db 데이터 넣기
def db_keyword(request):
    start = datetime.now()
    articles = Article.objects.all()[:5]
    
    fields = ['id', 'title','detail','keywords']
    article_list = list(articles.values(*fields))
    result_df = pd.DataFrame(article_list)
    
    df_news, kkk = extract_and_assign_keywords(result_df)
    for id in df_news.id:
        keywords_list = df_news.loc[df_news['id'] == id, 'keywords']
        article = Article.objects.get(id=id)
        article.keywords = list(keywords_list)
        article.save()
    end = datetime.now()
    flow = end-start

    return JsonResponse({'return': flow, 'kkk' : kkk})


# 카카오 챗봇에 대한 응답 함수
@csrf_exempt
def search_kakao(request):
    data = json.loads(request.body)
    # search_keyword = data['action']['params']['keyword']  # 스킬 테스트
    search_keyword = data['userRequest']['utterance']  # 챗봇 서비스
            
    try:
        key_cnt = KeywordCount.objects.get(name=search_keyword)
        key_cnt.count += 1
        key_cnt.save()
    except KeywordCount.DoesNotExist:  # 해당 키워드가 db에 존재하지 않을 경우 새롭게 insert
        key_cnt = KeywordCount.objects.create(name=search_keyword, count=1)

    key_cate_articles = Article.objects.filter(detail__icontains=search_keyword)

    if key_cate_articles:  # 키워드에 해당하는 기사가 있을 경우
        fields = ['id', 'title','detail', 'link', 'img', 'write_dt', 'sentiment']
        article_list = list(key_cate_articles.values(*fields))
        result_df = pd.DataFrame(article_list)

        positive_len = len(result_df[result_df['sentiment'] == 1])
        negative_len = len(result_df[result_df['sentiment'] == -1])
        negative_percentage = (negative_len/(positive_len+negative_len)) * 100
        negative = round(negative_percentage, 1)
        
        json_data = {
            "긍정": result_df[result_df['sentiment'] == 1].to_dict(orient='records'),
            "부정": result_df[result_df['sentiment'] == 0].to_dict(orient='records'),
            }
                
        name = search_keyword
        # target_keyword = Keyword.objects.get(keyword_text=keyword)
        # stock_code = target_keyword.code

        try:
            enterprise_name = Enterprise.objects.get(name=name)    
            stock_code = enterprise_name.code
        except Enterprise.DoesNotExist:
            return JsonResponse({'return': '일치하는 회사 이름이 없습니다.'})

        if stock_code:
            addmi = utils.get_price(stock_code, 'prdy_ctrt')[-1]  # 등략
            result_add = search_keyword + '의 전일대비 등락률은' + addmi + '% 입니다.'
        else:
            result_add =search_keyword + '의 주가정보가 없습니다 :('
        
        return JsonResponse({"data": {'P': round((100-negative),1),
                                      'N': negative,
                                      'keyword': search_keyword,
                                      'market_cap': result_add,   
                                      },
                             })

    else:  # 키워드에 해당하는 기사가 없을 경우
        return JsonResponse({'reply' : False})


