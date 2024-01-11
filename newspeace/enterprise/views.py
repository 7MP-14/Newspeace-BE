from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from accounts.models import *
from news.models import Article
from .models import *
from api import utils
import pandas as pd
import json

# Create your views here.



# 데이터 축적
def realTimeGraph(request, day, hour):
    if request.method == 'GET':
        enterprise_queryset = Enterprise.objects.all()
        name_list = [enterprise.name for enterprise in enterprise_queryset]

        for name in name_list:
            enterprise_articles = Article.objects.filter(create_dt__day=day, create_dt__hour=hour,detail__icontains=name)

            if enterprise_articles:  # 키워드에 해당하는 기사가 있을 경우
                fields = ['sentiment']
                article_list = list(enterprise_articles.values(*fields))
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
                
            inst = Enterprise.objects.get(name=name)
            price = utils.get_price(inst.code)[0]
   
            keywordinfo = EnterpriseGraph.objects.create(enterprise=inst, negative=negative, present=price)
            keywordinfo.save()
                
        return JsonResponse({'return' : '성공'})
    


# 구독 키워드의 시간 당 부정도 축적 데이터 그래프화
@csrf_exempt
def Graph(request):
    if request.method == "POST":
        data = json.loads(request.body)
        name = data.get('name')        
    
        try:
            enterprise_name = Enterprise.objects.get(name=name)    
        except Enterprise.DoesNotExist:
            return JsonResponse({'return': '일치하는 회사 이름이 없습니다.'})
        
        
        enterprise_list = enterprise_name.enterprisegraph_set.all()
        if enterprise_list:
                    
            # 정상적으로 try문이 실행됐을 경우
            # negativekeywordinfo 테이블에서 정상적으로 정보를 가져온 경우
            result_time = []
            result_negative = []
            result_present = []
            
            # 불러온 negative_info_list를 돌면서 (시간, 부정도, 현재가)를 리스트로 저장
            for enterprise_info in enterprise_list:
                result_time.append(enterprise_info.create_dt)
                result_negative.append(enterprise_info.negative)
                result_present.append(enterprise_info.present)

            
            # 위 3개의 리스트를 시간순으로 정렬
            sorted_data = sorted(zip(result_time, result_negative, result_present), key=lambda x: x[0])
            
            # 현재가 없는 데이터 삭제
            result_time, result_negative, result_present = map(list, zip(*sorted_data))
            zero_indices = [index for index, value in enumerate(result_present) if value == 0]
            
            for index in reversed(zero_indices):
                del result_time[index]
                del result_negative[index]
                del result_present[index]
                        
            stock_code = enterprise_name.code
            
            result_temp = utils.get_price(stock_code) 
            
            result_dod = result_temp[1]  # 전일 대비 (DayofDay)
            result_open = result_temp[2]  # 시가
            result_high = result_temp[3]  # 고가
            result_low = result_temp[4]  # 저가
            
            return JsonResponse({'result_time' : result_time,
                        'result_negative' : result_negative,
                        'result_present':result_present,
                        'result_dod':result_dod,
                        'result_open':result_open,
                        'result_high':result_high,
                        'result_low':result_low,
                    })
        
        else:
            return JsonResponse({'return': '일치하는 회사의 정보가 없습니다.'})
        
    
    
def enterpriseList(request):
    if request.method == 'GET':
        enterprise_list = Enterprise.objects.all()
        
        name_list = []
        for enterprise in enterprise_list:
            name_list.append(enterprise.name)
            
        return JsonResponse({'return' : name_list})