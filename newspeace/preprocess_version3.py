
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from torch import nn
import pandas as pd
# from crawling_수정 import *
from sqlalchemy import create_engine
from sqlalchemy.sql import text
from mykeyword_graph import mykeyword_negative_update
from datetime import datetime, timedelta



# db 연결
con = create_engine("mysql+pymysql://admin:admin12345@joon-sql-db-1.cvtb5zj20jzi.ap-northeast-2.rds.amazonaws.com:3306/joon_db")

# 임시 db 데이터 받아오기
query = "SELECT * FROM news_temporalyarticle" 
crawling_df = pd.read_sql(query, con)
crawling_df.drop(columns='id', inplace=True)


# 모델링 함수
def process_news_keyword(news):
    tokenizer = AutoTokenizer.from_pretrained("snunlp/KR-FinBert-SC")
    model = AutoModelForSequenceClassification.from_pretrained("snunlp/KR-FinBert-SC")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    
    # 감성 분석 결과 초기화
    sentiments = []

    # 각 제목에 대한 감성 분석 수행
    for text in news['title']:
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

        sentiments.append(sentiment)

    # 결과를 DataFrame에 추가
    news['sentiment'] = sentiments

    # 중립 의견 제외
    news = news[news['sentiment'] != 0]

    return news


start_current_datetime_model = datetime.now()
print(f"모델링 시작: {start_current_datetime_model}")

if not crawling_df.empty:
    # 모델링
    news = process_news_keyword(crawling_df)

    # 결과 db 저장
    news.to_sql('news_article', con, if_exists='append', index=False)

end_current_datetime_model = datetime.now()
print(f"모델링 끝: {end_current_datetime_model}")

# # 크롤링 시작 시간을 log.txt 파일에 기록
# with open('cron_log_model.txt', 'a') as log_file:
#     log_file.write(f"모델링 시작 시간 : {start_current_datetime_model}\n")

# # 크롤링 끝 시간을 log.txt 파일에 기록
# with open('cron_log_model.txt', 'a') as log_file:
#     log_file.write(f"모델링 끝 시간 : {end_current_datetime_model}\n")
    



# 현재 시간으로부터 2일 전의 시간 계산
current_datetime = datetime.now()
time_to_delete = current_datetime - timedelta(days=2) + timedelta(hours=1)

# db에 데이터 삭제
with con.connect() as connection:
    query = text("DELETE FROM news_article WHERE CREATE_DT < :time_to_delete")
    result = connection.execute(query, {"time_to_delete" : time_to_delete})
    connection.commit()
    

# 구독 키워드 부정도 업데이트 및 데이터 축적
crwaling_day = start_current_datetime_model.day
crwaling_hour = start_current_datetime_model.hour

start2_current_datetime = datetime.now()

response = mykeyword_negative_update(crwaling_day, crwaling_hour)
print(response)

end2_current_datetime = datetime.now()

# # 크롤링 시작 시간을 log.txt 파일에 기록
# with open('cron_log_model.txt', 'a') as log_file:
#     log_file.write(f"부정도 업데이트 시작 시간 : {start2_current_datetime}\n")

# # 크롤링 끝 시간을 log.txt 파일에 기록
# with open('cron_log_model.txt', 'a') as log_file:
#     log_file.write(f"부정도 업데이트 끝 시간 : {end2_current_datetime}\n")