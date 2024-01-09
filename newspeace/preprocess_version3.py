import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from torch import nn
import pandas as pd
# from crawling_수정 import *
from sqlalchemy import create_engine
from sqlalchemy.sql import text
from mykeyword_graph import mykeyword_negative_update, enterprise_update
from datetime import datetime, timedelta
import random
from keybert import KeyBERT
from mecab import MeCab
from collections import Counter
import json


# db 연결
con = create_engine("mysql+pymysql://admin:admin12345@joon-sql-db-1.cvtb5zj20jzi.ap-northeast-2.rds.amazonaws.com:3306/joon_db")

# 임시 db 데이터 받아오기
query = "SELECT * FROM news_temporalyarticle" 
crawling_df = pd.read_sql(query, con)
crawling_df.drop(columns='id', inplace=True)


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
            
        # article.iloc[idx,'sentiment'] = sentiment

        sentiments_list.append(sentiment)
    
    article['sentiment'] = sentiments_list

    middle_news = article[article['sentiment'] == 0]
    article_news = article[article['sentiment'] != 0]

    return article_news, middle_news

# 키워드 추출 함수
def extract_and_assign_keywords(data, top_n=5):
    kw_model = KeyBERT('distilbert-base-nli-mean-tokens')
    
    all_keywords = []
    filter_list = []

    for text in data['title']:
        keywords = kw_model.extract_keywords(text, top_n=top_n)#, keyphrase_ngram_range=(1, 1))
        filtered_keywords = []

        for keyword, _ in keywords:
            filtered_keywords.append(keyword)
            all_keywords.append(keyword)
        
        filter_list.append(filtered_keywords)

        # 다음 라인을 수정하여 iterable한 값을 할당합니다.
    data['keywords'] = filter_list
    # topiclist = [item[0] for item in Counter(all_keywords).most_common(top_n)]

    return data


# 로그 작성용 난수 생성
rand_num = random.randint(0, 100)

start_current_datetime_model = datetime.now()
print(f"{rand_num} 모델링 시작: {start_current_datetime_model}")

if not crawling_df.empty:

    # 모델링
    df_model, middle_news = process_news_keyword(crawling_df)
    
    
    # # 키워드 추출
    
    half_current_datetime_model = datetime.now()
    print(f"{rand_num} 키워드 추출 시작: {half_current_datetime_model}")
    
    df_news = extract_and_assign_keywords(df_model, top_n=5)
    df_news['keywords'] = df_news['keywords'].apply(json.dumps)
    
    
    print(rand_num, '기사 개수:', len(df_model.sentiment))
    print(rand_num, '중립 기사 개수:', len(middle_news.sentiment))
    

    #결과 db 저장
    df_news.to_sql('news_article', con, if_exists='append', index=False)
    
    # # 중립 기사 저장 / 확인용 코드 / 확인 완료 후 주석 처리 
    # middle_hour = start_current_datetime_model.hour
    # middle_news.to_csv(f'중립기사_{middle_hour}.csv')

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

start2_current_datetime = datetime.now()

response1 = mykeyword_negative_update(crwaling_day, crwaling_hour)
response2 = enterprise_update(crwaling_day, crwaling_hour)
print(response1)
print(response2)

end2_current_datetime = datetime.now()






