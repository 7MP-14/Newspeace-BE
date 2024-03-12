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
# def realTimeGraph(request, day, hour):
#     if request.method == 'GET':
#         enterprise_queryset = Enterprise.objects.all()
#         name_list = [enterprise.name for enterprise in enterprise_queryset]

#         for name in name_list:
#             enterprise_articles = Article.objects.filter(create_dt__day=day, create_dt__hour=hour,detail__icontains=name)

#             if enterprise_articles:  # 키워드에 해당하는 기사가 있을 경우
#                 fields = ['sentiment']
#                 article_list = list(enterprise_articles.values(*fields))
#                 df = pd.DataFrame(article_list)
            
#                 positive_len = len(df[df['sentiment'] == 1])
#                 negative_len = len(df[df['sentiment'] == -1])
                
#                 if negative_len != 0:
#                     negative_percentage = (negative_len/(positive_len+negative_len)) * 100
#                     negative = round(negative_percentage, 1)
#                 else:
#                     negative = 0
#             else:
#                 negative = 0
                
#             inst = Enterprise.objects.get(name=name)
#             price = utils.get_price(inst.code)[0]
   
#             keywordinfo = EnterpriseGraph.objects.create(enterprise=inst, negative=negative, present=price)
#             keywordinfo.save()
                
#         return JsonResponse({'return' : '성공'})
    

import yfinance as yf
from pandas_datareader import data as pdr
# 구독 키워드의 시간 당 부정도 축적 데이터 그래프화
@csrf_exempt
def Graph0(request):
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
            
            
            ######################
            data = pd.read_csv("/home/ubuntu/deploy/newspeace/data_2331_20240215.csv")
            data.rename(columns={"일자":"date", "종가":'close',
                                '대비':'dod', '등락률':'dod_rate',
                                "시가":'open', "고가":'high',
                                "저가":'low',
                                },
                        inplace=True)
            
            aa = sorted(list(data['date']))
            bb = list(data['open'])
            new_data = []
            for value in bb:
                deviation = value * 0.3  # 최대 허용 편차
                new_value = value + random.uniform(-deviation, deviation)
                new_data.append(round(new_value))
            
            
            
            return JsonResponse({'result_time' : result_time[:50],
                        'result_negative' : result_negative[:50],
                        'result_present':result_present[:50],
                        # 주식 페이지 들어가면 렉 걸려서 
                        # 위 3개 리스트에 인덱싱 걸어 놓았습니다.
                        # 2024 01 30 1740 정솔
                        'result_dod':result_dod,
                        'result_open':result_open,
                        'result_high':result_high,
                        'result_low':result_low,
                        
                        'result_time_date' : aa,
                        'result_present_date': 73900,
                        'result_close_date': new_data,
                        'result_dod_date': list(data['dod']),
                        'result_open_date': list(data['open']),
                        'result_high_date': list(data['high']),
                        'result_low_date': list(data['low']),
                    })

        
        else:
            return JsonResponse({'return': '일치하는 회사의 정보가 없습니다.'})
        

import random
@csrf_exempt
def Graph2(request):
    data = pd.read_csv("/home/ubuntu/deploy/newspeace/data_2331_20240215.csv")
    data.rename(columns={"일자":"date", "종가":'close',
                         '대비':'dod', '등락률':'dod_rate',
                         "시가":'open', "고가":'high',
                         "저가":'low',
                         },
                inplace=True)
    
    aa = sorted(list(data['date']))
    bb = list(data['open'])
    new_data = []
    for value in bb:
        deviation = value * 0.3  # 최대 허용 편차
        new_value = value + random.uniform(-deviation, deviation)
        new_data.append(round(new_value))
    
    
    print("asdfasdf55556666", aa)
    return JsonResponse({'result_time' : aa,
                        'result_present': 73900,
                        'result_close': new_data,
                        'result_dod': list(data['dod']),
                        'result_open': list(data['open']),
                        'result_high': list(data['high']),
                        'result_low': list(data['low']),
                    })


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

            
            enterprise_list = pd.read_csv("/home/ubuntu/deploy/newspeace/enterprise_list.csv")
            enterprise_list['code'] = [str(num).zfill(6) for num in enterprise_list['code']]
                
            
            from datetime import datetime, timedelta
            import yfinance as yf
            from pandas_datareader import data as pdr
            def stock_price_info(code):
                # 오늘 날짜 구하기
                today = datetime.today()

                # 6개월 전 날짜 계산
                six_months_ago = today - timedelta(days=180)  # 6개월은 대략 180일로 가정

                # 포맷팅하여 문자열로 변환
                six_months_ago_str = six_months_ago.strftime("%Y-%m-%d")

                yf.pdr_override()
                data = pdr.get_data_yahoo(code + '.KS', start=six_months_ago_str)
                data['Dod'] = data['Close'] - data['Close'].shift(1)
                data = data.iloc[1:]

                return data
            
            
            stock_data = stock_price_info(stock_code)
            
            # stock_data = stock_data.sort_values(by='date')
            
            # react or js는 list 밖에 못 받나?
            # array나 dataframe같은 거는 못 받나?
            # 아니면 프론트쪽에서 그렇게 설정을 해서 그런건가?
            
            
            result_time_date = stock_data.index.strftime('%Y-%m-%d').tolist()
            
            print(stock_data.iloc[-10:])
            print()
            print()
            print()
            
            
            temp = 10
            print('temp')
            result_close_date = stock_data['Close'].tolist()
            print("result_close_date")
            print(result_close_date[-temp:])
            result_dod_date = stock_data['Dod'].tolist()
            print("result_dod_date")
            print(result_dod_date[-temp:])
            result_open_date = stock_data['Open'].tolist()
            print("result_open_date")
            print(result_open_date[-temp:])
            result_high_date = stock_data['High'].tolist()
            print("result_high_date")
            print(result_high_date[-temp:])
            result_low_date = stock_data['Low'].tolist()
            print("result_low_date")
            print(result_low_date[-temp:])
            print()
            print()
            
            temp = 10
            return JsonResponse({'result_time' : result_time[:temp],
                                 'result_negative' : result_negative[:temp],
                                 'result_present':result_present[:temp],
                                 'result_dod':result_dod,
                                 'result_open':result_open,
                                 'result_high':result_high,
                                 'result_low':result_low,
                                 
                                 'result_time_date' : result_time_date[-temp:],
                                 'result_present_date': result_present[-1],
                                 'result_close_date': result_close_date[-temp:],
                                 'result_dod_date': result_dod_date[-temp:],
                                 'result_open_date': result_open_date[-temp:],
                                 'result_high_date': result_high_date[-temp:],
                                 'result_low_date': result_low_date[-temp:],
                                 
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