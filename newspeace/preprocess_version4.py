import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from torch import nn
import pandas as pd
from sqlalchemy import create_engine
from mykeyword_graph import mykeyword_negative_update, enterprise_update
from datetime import datetime, timedelta
import random
from keybert import KeyBERT
from kiwipiepy import Kiwi
import json
import db_info


db = db_info.DATABASES['default']

# db 연결
con = create_engine(f"mysql+pymysql://{db['USER']}:{db['PASSWORD']}@{db['HOST']}:{db['PORT']}/{db['NAME']}")

# 임시 db 데이터 받아오기
query = "SELECT * FROM news_temporalyarticle"
crawling_df = pd.read_sql(query, con)
crawling_df.drop(columns=['id'], inplace=True)

query_media = "SELECT `id`, `name` FROM news_smallmedia"
media_dict = pd.read_sql(query_media, con).to_dict(orient='records')

media_map = {}
media_map.update({item['name']: item['id'] for item in media_dict})

crawling_df.media = crawling_df.media.map(media_map)
crawling_df.rename(columns={'media' : 'smallmedia_id'}, inplace=True)


# 감정분석 모델링 함수
def process_news_keyword(article):
    tokenizer = AutoTokenizer.from_pretrained("snunlp/KR-FinBert-SC")
    model = AutoModelForSequenceClassification.from_pretrained("snunlp/KR-FinBert-SC")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    
    # 감성 분석 결과 초기화
    sentiments_list = []

    # 각 제목에 대한 감성 분석 수행
    for idx,text in enumerate(article['title']):
        inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
        inputs = inputs.to(device)

        with torch.no_grad():
            outputs = model(**inputs)

        prediction = nn.functional.softmax(outputs.logits, dim=1)
        positive_score = prediction[:, 2].item()
        negative_score = prediction[:, 0].item()
        neutral_score = prediction[:, 1].item()

        # 긍정, 부정, 중립 점수에 따른 감성 결정
        if positive_score > max(negative_score, neutral_score):
            sentiment = 1  # 긍정
        elif negative_score > max(positive_score, neutral_score):
            sentiment = -1  # 부정
        else:
            sentiment = 0  # 중립
            
        sentiments_list.append(sentiment)
    
    article['sentiment'] = sentiments_list

    return article

# 키워드 추출 함수
def extract_and_assign_keywords(data):
    kw_model = KeyBERT('distilbert-base-nli-mean-tokens')
    kw_model_2 = KeyBERT('distiluse-base-multilingual-cased-v1')
    data = data.copy()  # 데이터프레임의 복사본을 만듭니다.
    data['keywords'] = ''   # 데이터프레임에 'keywords' 열 초기화

    for idx, row in data.iterrows():
        filtered_keywords = set()  # 집합으로 초기화

        keywords_title = kw_model.extract_keywords(str(row['title']), top_n=5)
        keywords_detail = kw_model.extract_keywords(str(row['detail']), top_n=5)
        filtered_keywords.update(keyword for keyword, _ in keywords_title)
        filtered_keywords.update(keyword for keyword, _ in keywords_detail)

        # 모델2
        keywords_title = kw_model_2.extract_keywords(str(row['title']), top_n=5)
        keywords_detail = kw_model_2.extract_keywords(str(row['detail']), top_n=5)
        filtered_keywords.update(keyword for keyword, _ in keywords_title)
        filtered_keywords.update(keyword for keyword, _ in keywords_detail)

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

    # 모델링
    df_model = process_news_keyword(crawling_df)
    
    print(rand_num, '기사 개수:', len(df_model.sentiment))
    
    # # 키워드 추출
    
    half_current_datetime_model = datetime.now()
    print(f"{rand_num} 키워드 추출 시작: {half_current_datetime_model}")
    
    df_news = extract_and_assign_keywords(df_model)
    df_news['keywords'] = df_news['keywords'].apply(json.dumps)
    
    #결과 db 저장
    df_news.to_sql('news_article', con, if_exists='append', index=False)
    

end_current_datetime_model = datetime.now()
print(f"{rand_num} 모델링 끝: {end_current_datetime_model}")



# 현재 시간으로부터 2일 전의 시간 계산
current_datetime = datetime.now()
time_to_delete = current_datetime - timedelta(days=7) + timedelta(hours=1)

# db에 데이터 삭제
# with con.connect() as connection:
#     query = text("DELETE FROM news_article WHERE CREATE_DT < :time_to_delete")
#     result = connection.execute(query, {"time_to_delete" : time_to_delete})
#     connection.commit()
    

# 구독 키워드 부정도 업데이트 및 데이터 축적
crwaling_day = start_current_datetime_model.day
crwaling_hour = start_current_datetime_model.hour


response1 = mykeyword_negative_update(crwaling_day, crwaling_hour)
response2 = enterprise_update(crwaling_day, crwaling_hour)
print(response1)
print(response2)

end2_current_datetime = datetime.now()
print(f"{rand_num} 키워드 추출 끝: {end2_current_datetime}")





