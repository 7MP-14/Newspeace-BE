import warnings
warnings.filterwarnings('ignore')
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from concurrent.futures import ProcessPoolExecutor
from sqlalchemy import create_engine
from sqlalchemy.sql import text
from functools import partial
import random

# 기사를 크롤링하는 함수
def crawling(category, start_time, today_date):
    items = []
    i = 1
    # while 4 > i:  # test용 반복 (반복 횟수를 줄였음)
    while i >= 1:
        url = f'https://news.daum.net/breakingnews/{category}?page={i}&regDate={today_date}'   # i번째 페이지

        response = requests.get(url)  
        dom = BeautifulSoup(response.text, 'lxml')  # html.parser -> lxml 속도 개선
        elements = dom.select('#mArticle > div.box_etc > ul > li')
        stop_check = False  # 크롤링 중단 여부 체크
        
        if not elements:    # 마지막 페이지까지 도달했을 경우 반복문 종료
            break

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
        print("elements 불러오는데 실패했습니다.", url)
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


# # db 연결
# con = create_engine("mysql+pymysql://admin:admin12345@joon-sql-db-1.cvtb5zj20jzi.ap-northeast-2.rds.amazonaws.com:3306/joon_db")

# # db에 데이터 삭제
# with con.connect() as connection:
#     query = text("DELETE FROM news_temporalyarticle")
#     result = connection.execute(query)
#     connection.commit()




# 로그 작성용 난수 생성
rand_num = random.randint(0, 100)


# 시작시간 설정
start_current_datetime = datetime.now()     # 현재 datetime
print(f"{rand_num} 크롤링 시작 : {start_current_datetime}")

now_date = start_current_datetime.strftime("%Y%m%d")            # 현재 날짜 
now_time = start_current_datetime.strftime("%H:%M")             # 현재 시각

thirty_minutes_ago = start_current_datetime - timedelta(minutes=30)   # 30분을 뺀 datetime
ago_date = thirty_minutes_ago.strftime("%Y%m%d")                      # 1시간 전 날짜 
ago_time = thirty_minutes_ago.strftime("%H:%M")                       # 1시간 전 시각

# 크롤링 시작
category_list = ['society', 'politics', 'economic', 'culture', 'entertain', 'sports', 'digital']    

# 현재 날짜와 1시간 전 날짜가 같으면 같은 날짜 crawling 수행
if now_date == ago_date:
    with ProcessPoolExecutor(max_workers=len(category_list)) as executor:
        results = list(executor.map(crawling, category_list, [ago_time]*len(category_list), [now_date]*len(category_list)))
# 현재 날짜와 1시간 전 날짜가 다르면 URL이 다르므로 crawling 따로 수행 
else:
    with ProcessPoolExecutor(max_workers=len(category_list)) as executor:
        print(f"{rand_num} 여기가 실행됩니다")
        results = list(executor.map(partial(process_category, ago_time=ago_time, ago_date=ago_date, now_date=now_date), category_list))

# 모든 카테고리 결과를 하나의 데이터프레임으로 합치기
result_df = pd.concat(results, ignore_index=True)

# 'detail' 컬럼을 기준으로 중복된 행 제거
pattern = r'\b([가-힣]+)\s기자\s='  # 한글 기자 이름 패턴
result_df['reporter_name'] = result_df['detail'].str.extract(pattern)

# 중복된 기자 이름을 가진 행을 제거하고 유일한 값을 남김
result_df = result_df.drop_duplicates(subset=['title', 'reporter_name'], keep='first')
result_df.drop(columns='reporter_name', inplace=True)

# 중복 제거 후 DataFrame을 다시 인덱스 재정렬
result_df = result_df.reset_index(drop=True)


# Remove outliers
alpha = 0.05
result_df['text_length'] = result_df['detail'].apply(len)
low = result_df['text_length'].quantile(alpha)
high = result_df['text_length'].quantile(1 - alpha)
ret_trim = result_df[(result_df['text_length'] > low) & (result_df['text_length'] < high)]
result_df = ret_trim.drop(columns=['text_length']).reset_index(drop=True)


# category 필드 한글 변경
category_map = {'society': '사회', 'politics': '정치', 'economic': '경제',
                    'culture': '문화', 'entertain': '연예', 'sports': '스포츠', 'digital': 'IT'}
result_df.category = result_df.category.map(category_map)

# 크롤링 끝 
end_current_datetime = datetime.now()


print(rand_num, '기사 개수 :', len(result_df.category))

# # db 저장
# result_df.to_sql('news_temporalyarticle', con, if_exists='append', index=False)

print(f"{rand_num} 크롤링 끝 : {end_current_datetime}")
print(f"{rand_num} 걸린시간 : {end_current_datetime - start_current_datetime}")

