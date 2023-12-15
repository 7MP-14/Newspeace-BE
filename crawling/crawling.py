# 실행 시각으로 부터 1시간 동안의 기사만 크롤링

import warnings
warnings.filterwarnings('ignore')
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

# 기사를 크롤링하는 함수
def crawling(category, start_time):
    items = []
    i = 1
    # while i >= 1:
    while 3 > i:  # test용 반복 (반복 횟수를 줄였음)
        url = f'https://news.daum.net/breakingnews/{category}?page={i+1}'   # i번째 페이지

        response = requests.get(url)  
        dom = BeautifulSoup(response.text, 'html.parser')
        elements = dom.select('#mArticle > div.box_etc > ul > li')
        stop_check = False  # 크롤링 중단 여부 체크

        for j, element in enumerate(elements):
            link = element.select_one('.cont_thumb > .tit_thumb > .link_txt').get('href')
            time = element.select_one('.cont_thumb > .tit_thumb > .info_news > .info_time').text
            # 기준 시간(start_time) 이후에 작성된 기사인 경우
            if time >= start_time:
                  items.append({
                  'category': category,
                  'title': element.select_one('.cont_thumb > .tit_thumb > .link_txt').text,
                  'link': link,
                  'img': detail(link)[1],
                  'time': time,
                  'detail': detail(link)[0],
                  })
            # 기준 시간(start_time) 이전에 작성된 기사인 경우
            else:
                stop_check = True
                break
        if stop_check:
            break
        i += 1
        
    df = pd.DataFrame(items)

    return df


# 해당 링크에 들어가서 기사 본문 가져오는 함수
def detail(url):
  response = requests.get(url)
  dom = BeautifulSoup(response.text, 'html.parser')
  elements = dom.select('#mArticle > div.news_view.fs_type1 > div.article_view > section')[0]
  element = elements.find_all(attrs={'dmcf-ptype':'general'})
  
  detail = ''
  for i in element:
    detail += i.text + ' '

  try:
    img = elements.select_one('figure > p > img').get('src')
  except:
    try:
      img = elements.find('iframe').get('poster')
    except:
      img = None

  return detail, img

category_list = ['society', 'politics', 'economic', 'foreign', 'culture', 'entertain', 'sports', 'digital']
now_time = datetime.now()                       # 현재 시각
one_hour_ago =  now_time - timedelta(hours=1)   # 1시간 전 시각
one_hour_ago = one_hour_ago.strftime("%H:%M")   # HH:MM 형태 문자열로 저장
now_time = now_time.strftime("%Y-%m-%d_%H-%M")  # 결과 저장 파일 이름에 사용하기 위한 현재 시각을 문자열로 저장

result_df = pd.DataFrame()
for category in category_list:
    result_df = pd.concat([result_df, crawling(category, one_hour_ago)])
    
result_df = result_df.reset_index(drop=True)    # index 초기화

# 데이터프레임을 json 파일로 저장하기
result_df.to_json(f'./result/crawling_{now_time}.json', orient='records', force_ascii=False, indent=4)
# 데이터프레임을 csv 파일로 저장하기
result_df.to_csv(f'./result/crawling_{now_time}.csv', index=False)