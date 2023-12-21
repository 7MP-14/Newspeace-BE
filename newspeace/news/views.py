from .models import *
from django.http import JsonResponse
import csv
import pandas as pd
from preprocess import process_news_keyword


# # Create your views here.


def search(request):
    # search_keyword = request.GET.get('keyword')
    # search_category_list = request.GET.getlist('category')
    
    search_keyword = 'kt'
    search_category_list = ['society']
    
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
        
        result_df, postive = process_news_keyword(df, search_keyword)
        
        json_data = {
        "긍정": result_df[result_df['sentiment'] == 1].to_dict(orient='records'),  
        "부정": result_df[result_df['sentiment'] == 0].to_dict(orient='records'),
        }
        
        return JsonResponse({'article': json_data, '긍정도':postive, '부정도' : (100-postive), 'keyword' : search_keyword})

    else:
        return JsonResponse({'reply' : f"죄송합니다. {search_keyword}에 해당하는 뉴스 기사를 찾을 수 없습니다. 카테고리 재설정 또는 검색 단어를 수정해주세요."})


# 인기 검색어 조회
def topkeyword(request):
    if request.method == "GET":
        keywords = KeywordCount.objects.order_by('-count')[:10]
        keywords_list = []
        
        for i in keywords:
            keywords_list.append(i.name)
            
    return JsonResponse({'keyword_list' : keywords_list})


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


