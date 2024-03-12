import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from concurrent.futures import ProcessPoolExecutor
import random
from sqlalchemy import create_engine
from sqlalchemy.sql import text

# 기사를 크롤링하는 함수
def crawling(media, start_time):
    items = []
    i = 1
    # while 4 > i:  # test용 반복
    while i >= 1:
        url = f"https://news.naver.com/main/list.naver?mode=LPOD&mid=sec&oid={media}&page={i}"
        response = requests.get(url)
        dom = BeautifulSoup(response.text, 'lxml')  # html.parser -> lxml 속도 개선
        elements = dom.select('#main_content > div.list_body.newsflash_body > ul.type06_headline > li')
        stop_check = False  # 크롤링 중단 여부 체크

        # 마지막 페이지까지 도달했을 경우 while문 종료
        if int(dom.select_one('#main_content > div.paging > strong').text) != i:    
            break
        
        # print(i, '페이지까지 했음')
        for element in elements:
            link = element.select_one('dl > dt > a').get('href')
            result_detail = detail(link, start_time)

            # 기준 시간(start_time) 이후에 작성된 기사인 경우
            if result_detail is not None:
                items.append({
                'title':result_detail[0],
                'detail': result_detail[1],
                'category': result_detail[2],
                'link':link,
                'img': result_detail[3],
                'create_dt': datetime.now(),
                'write_dt': result_detail[4],
                'media': media,
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


# 해당 링크에 들어가서 기사 데이터 가져오는 함수
def detail(url, start_time):
    response = requests.get(url)
    dom = BeautifulSoup(response.text, 'lxml')  # html.parser -> lxml 속도 개선

    try:
        # 일반 기사
        if dom.select_one('div.media_end_head_info_datestamp > div > span') is not None:
            # "2024-03-03 22:18:05"
            time = dom.select_one('div.media_end_head_info_datestamp > div > span').get('data-date-time')
            time = datetime.strptime(time, "%Y-%m-%d %H:%M:%S")

            # 기준 시간(start_time) 이후에 작성된 기사인 경우
            if start_time <= time:
                title = dom.select_one('#title_area > span').text
                detail = dom.select_one('#dic_area').text.strip()       # strip() : 앞뒤 공백 제거

                # 이미지가 있으면 가져오기
                try:
                    img = dom.select_one('#img1').get('data-src')
                except:
                    img = None

                # 카테고리 가져올때 에러 예시
                # https://n.news.naver.com/mnews/article/005/0001678611
                try:
                    category = dom.select_one('#_LNB > ul > li.Nlist_item._LNB_ITEM.is_active > a > span').text     # 네이버 상단 카테고리
                except:
                    category = "-"
                # category2 = dom.select_one('#contents > div.media_end_categorize > a > em').text                # 이 기사는 언론사에서 '' 섹션으로 분류했습니다. 
                
                return title, detail, category, img, time
            # 기준 시간(start_time) 이전에 작성된 기사인 경우
            else:
                return

        # 스포츠 기사
        elif dom.select_one('#content > div > div.content > div > div.news_headline > div > span:nth-child(1)') is not None:
            # 에러 예시 https://sports.naver.com/news?oid=005&aid=0001678817
            # "기사입력 2024.03.05. 오후 10:35"
            time = dom.select_one('#content > div > div.content > div > div.news_headline > div > span:nth-child(1)').text
            time = time[5:]  # '기사입력' 문자열 삭제 
            time = time.replace("오후", "PM").replace("오전", "AM")
            time = datetime.strptime(time, '%Y.%m.%d. %p %I:%M')  # 문자열을 datetime 객체로 변환

            # 기준 시간(start_time) 이후에 작성된 기사인 경우
            if start_time <= time:
                title = dom.select_one('#content > div > div.content > div > div.news_headline > h4').text
                detail = dom.select_one('#newsEndContents').text.strip()
                category = "스포츠"

                # 이미지가 있으면 가져오기
                try:
                    img = dom.select_one('#newsEndContents > span > img').get('src')
                except:
                    img = None
                
                return title, detail, category, img, time
            # 기준 시간(start_time) 이전에 작성된 기사인 경우
            else:
                return
    except:
        print('detail 에러', url)
        return 


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

thirty_minutes_ago = start_current_datetime - timedelta(minutes=30)   # 30분을 뺀 datetime


# 크롤링 시작
media_list = ['032', '005', '020', '021', '081', '022', '023', '025', '028', '469'] # 종합 언론사 리스트

# 윈도우에서 ProcessPoolExecutor을 사용하려면 아래의 3줄을 추가해야함
# 리눅스에서는 아래의 3줄을 없앤 뒤 들여쓰기 한칸 빼고 실행하기
from multiprocessing import freeze_support
if __name__ == "__main__":
    freeze_support()

    with ProcessPoolExecutor(max_workers=len(media_list)) as executor:
        results = list(executor.map(crawling, media_list, [thirty_minutes_ago]*len(media_list)))

    # 모든 크롤링 결과를 하나의 데이터프레임으로 합치기
    result_df = pd.concat(results, ignore_index=True)

    # 인덱스 재정렬
    result_df = result_df.reset_index(drop=True)

    # media 필드 한글 변경
    media_map = {'032': '경향신문', '005': '국민일보', '020': '동아일보', '021': '문화일보', 
                 '081': '서울신문', '022': '세계일보', '023': '조선일보', '025': '중앙일보',
                 '028': '한겨레', '469': '한국일보'}
    if not result_df.empty: # 데이터프레임이 비어있지 않다면
        result_df['media'] = result_df['media'].map(media_map)

    print(rand_num, '기사 개수 :', len(result_df))
    
    # 데이터프레임을 json 파일로 저장하기
    result_df.to_json(f'./result/crawling_{start_current_datetime.strftime("%Y-%m-%d_%H-%M")}.json', orient='records', force_ascii=False, indent=4)
    # 데이터프레임을 csv 파일로 저장하기
    result_df.to_csv(f'./result/crawling_{start_current_datetime.strftime("%Y-%m-%d_%H-%M")}.csv', index=False)
    
    # # db 저장
    # result_df_total.to_sql('news_temporalyarticle', con, if_exists='append', index=False)

    # 크롤링 끝 
    end_current_datetime = datetime.now()
    print(f"{rand_num} 크롤링 끝 : {end_current_datetime}")
    print(f"{rand_num} 걸린시간 : {end_current_datetime - start_current_datetime}")