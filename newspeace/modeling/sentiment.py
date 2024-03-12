# 감정분석 모델링 함수
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from torch import nn
import pandas as pd

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
    
    positive_articles = article[article['sentiment'] == 1].head(200)
    negative_articles = article[article['sentiment'] == -1].head(200)
    neutral_articles = article[article['sentiment'] == 0].head(200)

    new_df = pd.concat([positive_articles, negative_articles, neutral_articles])

    return new_df

