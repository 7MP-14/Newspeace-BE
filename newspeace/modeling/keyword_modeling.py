import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.sql import text
from datetime import datetime, timedelta
import random
from keybert import KeyBERT
from kiwipiepy import Kiwi
import json
from pymongo import MongoClient
import sys
sys.path.append('../')  # 상위 폴더를 모듈 검색 경로에 추가

from db_info import DATABASES
from mongodb_info import MONGO_DATABASES
sql_db = DATABASES['default']
mongo_db = MONGO_DATABASES['default']
    
    
client = MongoClient(f"mongodb://{mongo_db['USER']}:{mongo_db['PASSWORD']}@{mongo_db['HOST']}:{mongo_db['PORT']}/{mongo_db['NAME']}")
collection = client.newspeace.articles
collection_articles = list(collection.find())
crawling_df = pd.DataFrame(collection_articles)
crawling_df.drop(columns=['_id'], inplace=True)


# db 연결
con = create_engine(f"mysql+pymysql://{sql_db['USER']}:{sql_db['PASSWORD']}@{sql_db['HOST']}:{sql_db['PORT']}/{sql_db['NAME']}")


query_media = "SELECT `id`, `name` FROM news_smallmedia"
media_dict = pd.read_sql(query_media, con).to_dict(orient='records')

media_map = {}
media_map.update({item['name']: item['id'] for item in media_dict})

crawling_df.media = crawling_df.media.map(media_map)
crawling_df.rename(columns={'media' : 'smallmedia_id'}, inplace=True)



# 키워드 추출 함수
def extract_and_assign_keywords(data):
    kw_model = KeyBERT('distilbert-base-nli-mean-tokens')
    kw_model_2 = KeyBERT('distiluse-base-multilingual-cased-v1')
    data = data.copy()  # 데이터프레임의 복사본을 만듭니다.
    data['keywords'] = ''   # 데이터프레임에 'keywords' 열 초기화

    for idx, row in data.iterrows():
        filtered_keywords = set()  # 집합으로 초기화

        keywords_title = kw_model.extract_keywords(str(row['title']), top_n=5)
        # keywords_detail = kw_model.extract_keywords(str(row['detail']), top_n=5)
        filtered_keywords.update(keyword for keyword, _ in keywords_title)
        # filtered_keywords.update(keyword for keyword, _ in keywords_detail)

        # 모델2
        keywords_title = kw_model_2.extract_keywords(str(row['title']), top_n=5)
        # keywords_detail = kw_model_2.extract_keywords(str(row['detail']), top_n=5)
        filtered_keywords.update(keyword for keyword, _ in keywords_title)
        # filtered_keywords.update(keyword for keyword, _ in keywords_detail)

        data.at[idx, 'keywords'] = filter_nouns(filtered_keywords)
        
    return data

# 명사만 추출하는 함수
def filter_nouns(keywords):
    kiwi = Kiwi()
    nouns = set()
    for keyword in keywords:
        text = ''
        result = kiwi.analyze(keyword)
        for token, pos, _, _ in result[0][0]:
            # 한 글자가 아닌 명사와 외국어(SL)만을 선택하여 문자열에 추가
            if pos in {'NNG', 'NNP', 'NR', 'NP', 'SL', 'SH', 'SN'}:
                text += token
        if text and not text.isdigit(): # 숫자로만 이루어져있는지 검사
            # 생성된 문자열을 명사 목록에 추가
            nouns.add(text)
    return list(nouns)


# 로그 작성용 난수 생성
rand_num = random.randint(0, 100)

start_current_datetime_model = datetime.now()
print(f"{rand_num} 모델링 시작: {start_current_datetime_model}")

if not crawling_df.empty:

    # 키워드 추출
    
    df_news = extract_and_assign_keywords(crawling_df)
    df_news['keywords'] = df_news['keywords'].apply(json.dumps)
    
    #결과 db 저장
    df_news.to_sql('news_article', con, if_exists='append', index=False)
    

end_current_datetime_model = datetime.now()
print(f"{rand_num} 모델링 끝: {end_current_datetime_model}")



# 현재 시간으로부터 2일 전의 시간 계산
current_datetime = datetime.now()
time_to_delete = current_datetime - timedelta(days=7) + timedelta(hours=1)

# db에 데이터 삭제
with con.connect() as connection:
    query = text("DELETE FROM news_article WHERE CREATE_DT < :time_to_delete")
    result = connection.execute(query, {"time_to_delete" : time_to_delete})
    connection.commit()
    


end2_current_datetime = datetime.now()
print(f"{rand_num} 키워드 추출 끝: {end2_current_datetime}")





