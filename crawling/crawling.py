# 실행 시각으로 부터 1시간 동안의 기사만 크롤링

import warnings
warnings.filterwarnings('ignore')
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from concurrent.futures import ProcessPoolExecutor
from functools import partial

# 기사를 크롤링하는 함수
def crawling(category, start_time, today_date):
    items = []
    i = 1
    # while 4 > i:  # test용 반복
    while i >= 1:
        url = f'https://news.daum.net/breakingnews/{category}?page={i}&regDate={today_date}'   # i번째 페이지

        response = requests.get(url)  
        dom = BeautifulSoup(response.text, 'lxml')  # html.parser -> lxml 속도 개선
        elements = dom.select('#mArticle > div.box_etc > ul > li')
        stop_check = False  # 크롤링 중단 여부 체크

        for j, element in enumerate(elements):
            link = element.select_one('.cont_thumb > .tit_thumb > .link_txt').get('href')
            time = element.select_one('.cont_thumb > .tit_thumb > .info_news > .info_time').text
            # 기준 시간(start_time) 이후에 작성된 기사인 경우
            if time >= start_time:
                detail_text, img = detail(link)
                items.append({
                    'title': element.select_one('.cont_thumb > .tit_thumb > .link_txt').text,       # 기사 제목
                    'detail': detail_text,
                    'category': category,
                    'link': link,
                    'img': img,
                    'create_dt' : datetime.now(),                                              # 크롤링된 시간
                    'write_dt' : datetime.strptime(today_date + " " + time, "%Y%m%d %H:%M")   # 기사 작성 시간
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
    dom = BeautifulSoup(response.text, 'lxml')  # html.parser -> lxml 속도 개선
    try:
        elements = dom.select('#mArticle > div.news_view.fs_type1 > div.article_view > section')[0]
        element = elements.find_all(attrs={'dmcf-ptype':'general'})
    except:
        print("elements 불러오는데 실패했습니다.")
        return None, None

    detail = ''
    for i in element:
        detail += i.text + ' '

    # 이미지가 있으면 가져오기
    try:
        img = elements.select_one('figure > p > img').get('src')    # 이미지 링크
    except:
        try:
            # 동영상이 있으면 가져오고, 없으면 None을 넣기
            img = elements.find('iframe').get('poster')             # 동영상 썸네일
        except:
            img = None

    return detail, img


def process_category(category, ago_time, ago_date, now_date):
            return pd.concat([crawling(category, '00:00', now_date),
                            crawling(category, ago_time, ago_date)])


# 시간 설정
now = datetime.now()                        # 현재 datetime
one_hour_ago = now - timedelta(hours=1)     # 1시간을 뺀 datetime

now_date = now.strftime("%Y%m%d")           # 현재 날짜 
now_time = now.strftime("%H:%M")            # 현재 시각

ago_date = one_hour_ago.strftime("%Y%m%d")  # 1시간 전 날짜 
ago_time = one_hour_ago.strftime("%H:%M")   # 1시간 전 시각


# 크롤링 시작
category_list = ['society', 'politics', 'economic', 'culture', 'entertain', 'sports', 'digital']


# 윈도우에서 ProcessPoolExecutor을 사용하려면 아래의 3줄을 추가해야함
# 리눅스에서는 아래의 3줄을 없앤 뒤 들여쓰기 한칸 빼고 실행하기
from multiprocessing import freeze_support
if __name__ == "__main__":
    freeze_support()
    
    # 현재 날짜와 1시간 전 날짜가 같으면 같은 날짜 crawling 수행
    if now_date == ago_date:
        with ProcessPoolExecutor(max_workers=len(category_list)) as executor:
            results = list(executor.map(crawling, category_list, [ago_time]*len(category_list), [now_date]*len(category_list)))
    # 현재 날짜와 1시간 전 날짜가 다르면 URL이 다르므로 crawling 따로 수행 
    else:
        with ProcessPoolExecutor(max_workers=len(category_list)) as executor:
            print("여기가 실행됩니다")
            results = list(executor.map(partial(process_category, ago_time=ago_time, ago_date=ago_date, now_date=now_date), category_list))

    # 모든 카테고리 결과를 하나의 데이터프레임으로 합치고 인덱스 초기화하기
    result_df = pd.concat(results, ignore_index=True)

    # 데이터프레임을 json 파일로 저장하기
    result_df.to_json(f'./result/crawling_{now.strftime("%Y-%m-%d_%H-%M")}.json', orient='records', force_ascii=False, indent=4)
    # 데이터프레임을 csv 파일로 저장하기
    result_df.to_csv(f'./result/crawling_{now.strftime("%Y-%m-%d_%H-%M")}.csv', index=False)