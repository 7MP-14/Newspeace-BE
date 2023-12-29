from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from accounts.models import *
from .models import *

import csv
import pandas as pd
import json
from datetime import datetime, timedelta

from preprocess import process_news_keyword
from preprocess_version2 import process_news_paragraph_kakao
from api import utils


# # Create your views here.
        
@csrf_exempt
def search(request):
    data = json.loads(request.body)
    search_keyword = data.get('keyword')
    search_category_list = data.get('category')
    print(data.get('keyword'))
    print(data.get('category'))
    
    # test용 키워드 & 카테고리 직접 변수로 전달
    # 코드 실행 체크용 strat_time
    # search_keyword = '제약'
    # search_category_list = ['사회', '경제']
    start_time = datetime.now()
    
    # KeywordCount 테이블 입력 단어 cnt 수정
    try:
        key_cnt = KeywordCount.objects.get(name=search_keyword)
        key_cnt.count += 1
        key_cnt.save()
    except KeywordCount.DoesNotExist:  # 해당 키워드가 db에 존재하지 않을 경우 새롭게 insert
        key_cnt = KeywordCount.objects.create(name=search_keyword, count=1)

    if search_category_list:
        cate_articles = Article.objects.filter(category__in=search_category_list)  # 카테고리 필터링
        key_cate_articles = cate_articles.filter(detail__icontains=search_keyword)  # 키워드 필터링
    else:
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
        
        end_time = datetime.now()
        running_time =  end_time - start_time
        return JsonResponse({'article': json_data, '긍정도':(100-negative), '부정도' : negative, 'keyword' : search_keyword, 'time' : running_time})

    else:  # 키워드에 해당하는 기사가 없을 경우
        return JsonResponse({'reply' : False})


# 인기 검색어 조회
def hot_keyword(request):
    if request.method == "GET":
        keywords = KeywordCount.objects.order_by('-count')[:20]
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
        


# 스크립트 한 기사 삭제하기
@csrf_exempt
def MyNewsDelete(request, no):
    if request.method == 'DELETE':
        
        print(no)
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


# 키워드 구독한거, 필터링해서, ratio 구해서 1. update // 2. 새로운 db에 축적하기
def realTimeRatio(request, day, hour):
    if request.method == 'GET':
        
        keyword_queryset = Keyword.objects.all()
        keyword_list = [keyword.keyword_text for keyword in keyword_queryset]
 
        for keyword in keyword_list:
            key_cate_articles = Article.objects.filter(create_dt__day=day, create_dt__hour=hour, detail__icontains=keyword)[20:30]

            if key_cate_articles:  # 키워드에 해당하는 기사가 있을 경우
                fields = ['sentiment']
                article_list = list(key_cate_articles.values(*fields))
                df = pd.DataFrame(article_list)
            
                positive_len = len(df[df['sentiment'] == 1])
                negative_len = len(df[df['sentiment'] == -1])
                negative_percentage = (negative_len/(positive_len+negative_len)) * 100
                negative = round(negative_percentage, 1)
            
            else:
                negative = -2
                
            # 부정도 최신화
            target_keyword = Keyword.objects.get(keyword_text=keyword)
            target_keyword.ratio = negative
            target_keyword.save()
            
            # NegativeKeywordInfo 객체 생성
            if negative != -2:
                stock_code = target_keyword.code
                price = utils.get_price(stock_code)

                keywordinfo = NegativeKeywordInfo.objects.create(keyword = target_keyword, 
                                                   negative = negative, 
                                                   present = price,
                                                   )
                
                keywordinfo.save()
        return JsonResponse({'return' : '성공'})
        

# 구독 키워드의 시간 당 부정도 축적 데이터 그래프화
@csrf_exempt
def myKeyword(request):
    if request.method == "POST":
        
        data = json.loads(request.body)
        keyword = data.get('keyword')
        
        try:
            target_keyword = Keyword.objects.get(keyword_text=keyword)
            negative_info_list = target_keyword.negativekeywordinfo_set.all()
        except Keyword.DoesNotExist:
            return JsonResponse({'return': '일치하는 키워드가 없습니다.'})
        except NegativeKeywordInfo.DoesNotExist:
            return JsonResponse({'return': '일치하는 키워드의 정보가 없습니다.'})
        
        # original
        # result_time = []
        # result_negative = []
        # result_present = []
        
        # for negative_info in negative_info_list:
        #     result_time.append(negative_info.create_dt)
        #     result_negative.append(negative_info.negative)
        #     result_present.append(negative_info.present)
        
        # test                
        import datetime as dt
        import pandas as pd
        start_time = dt.datetime.strptime("2023-12-27T06:00:00", "%Y-%m-%dT%H:%M:%S")
        end_time = dt.datetime.strptime("2023-12-27T18:00:00", "%Y-%m-%dT%H:%M:%S")
        result_time = []
        while start_time <= end_time:
            result_time.append(start_time.strftime("%Y-%m-%dT%H:%M:%S"))
            start_time += dt.timedelta(minutes=30)                        
                
        
        import random
        result_negative = [random.randint(1, 99) for _ in range(26)]
        
        result_present = [random.randint(50000, 60000) for _ in range(26)]
            
        return JsonResponse({'result_time' : result_time, 'result_negative' : result_negative, 'result_present':result_present})


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


# test1227
from django.core.serializers import serialize
def search2222(request):
    print('*Start**Start***Start**Start*Start***Start**Start**Start**Start*')
    
    price = utils.get_price('035720')
    print(price)
    
    search_keyword = '제약'
    search_category_list = ['사회', '경제']
    start_time = datetime.now()
    
    # KeywordCount 테이블 입력 단어 cnt 수정
    # try:
    #     key_cnt = KeywordCount.objects.get(name=search_keyword)
    #     key_cnt.count += 1
    #     key_cnt.save()
    # except KeywordCount.DoesNotExist:  # 해당 키워드가 db에 존재하지 않을 경우 새롭게 insert
    #     key_cnt = KeywordCount.objects.create(name=search_keyword, count=1)

    cate_articles = Article.objects.filter(category__in=search_category_list)  # 카테고리 필터링
    key_cate_articles = cate_articles.filter(detail__icontains=search_keyword)  # 위 결과에 대해 키워드로 다시 필터링
    print('cate_articles: ', len(cate_articles))
    print('key_cate_articles: ', len(key_cate_articles))

    if key_cate_articles:  # 키워드에 해당하는 기사가 있을 경우
        # cate_articles = serialize('json', cate_articles)
        # key_cate_articles = serialize('json', key_cate_articles)
        
        fields = ['id', 'title','detail', 'link', 'img']  # category, create_dt 제외
        article_list = list(key_cate_articles.values(*fields))
        # print(article_list[:5])
        df = pd.DataFrame(article_list)
        print('df.shape: ', df.shape)
        df = df.iloc[:10, :]
        # print(df)
        
        # result_df, postive = process_news_paragraph_kakao(df, search_keyword)
        
        # json_data = {
        # "긍정": result_df[result_df['sentiment'] == 1].to_dict(orient='records'),  
        # "부정": result_df[result_df['sentiment'] == 0].to_dict(orient='records'),
        # }
        
        # json_data = {
        # "긍정": df[df['id'] > 15000].to_dict(orient='records'),  
        # "부정": df[df['id'] < 15000].to_dict(orient='records'),
        # }
        
        end_time = datetime.now()
        running_time =  end_time - start_time
        print('running_time: ', running_time)
        # return JsonResponse({'카카오 현재가': price, '긍정도':postive, '부정도' : (100-postive), 'keyword' : search_keyword, 'time' : running_time})
        return JsonResponse({'카카오 현재가': price,})
        

        
    else:  # 키워드에 해당하는 기사가 없을 경우
        return JsonResponse({'reply' : f"죄송합니다. {search_keyword}에 해당하는 뉴스 기사를 찾을 수 없습니다. 카테고리 재설정 또는 검색 단어를 수정해주세요."})
     
 

