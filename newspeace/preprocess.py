
import re
import torch
from mecab import MeCab
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from torch import nn
import pandas as pd

def process_news_keyword(news, keyword):
    # Mecab과 KoBERT 모델 초기화
    mecab = MeCab()
    tokenizer = AutoTokenizer.from_pretrained("monologg/kobert")
    model = AutoModelForSequenceClassification.from_pretrained("monologg/kobert")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    # 불용어 목록 불러오기
    with open('stopwords.txt', 'r', encoding='utf-8-sig') as f:
        stopwords_list = [line.strip() for line in f.readlines()]

    def filter_sentences_by_keyword(sentences, keyword):
        return [sentence for sentence in sentences if keyword in sentence]

    def clean_text_mecab(text):
        text = text.replace('\xa0', ' ')
        text = re.sub(r'[^A-Za-z0-9가-힣]', '', text)
        tokens = mecab.morphs(text)
        return ' '.join(word for word in tokens if word not in stopwords_list)

    # DataFrame의 'detail' 열에서 각 항목을 마침표로 분리
    news['sentences'] = news['detail'].apply(lambda x: str(x).split('.'))

    # 키워드 기반으로 문장 필터링 및 정제
    news['filtered_sentences'] = news['sentences'].apply(lambda x: filter_sentences_by_keyword(x, keyword))
    filtered_news = news[news['filtered_sentences'].apply(lambda x: len(x) > 0)]
    filtered_news['filtered_sentences_cleaned'] = filtered_news['filtered_sentences'].apply(
        lambda sentences: [clean_text_mecab(sentence) for sentence in sentences])

    # 감성 분석
    for index, row in filtered_news.iterrows():
        positive_scores = []
        negative_scores = []

        for sentence in row['filtered_sentences_cleaned']:
            inputs = tokenizer(sentence, return_tensors="pt", padding=True, truncation=True, max_length=512)
            inputs = inputs.to(device)

            with torch.no_grad():
                outputs = model(**inputs)

            prediction = nn.functional.softmax(outputs.logits, dim=1)
            positive_scores.append(prediction[:, 1].item())
            negative_scores.append(prediction[:, 0].item())

        # 평균 점수 계산
        avg_positive = sum(positive_scores) / len(positive_scores) if positive_scores else 0
        avg_negative = sum(negative_scores) / len(negative_scores) if negative_scores else 0

        # 기사 분류
        sentiment = 1 if avg_positive > avg_negative else 0
        filtered_news.at[index, 'sentiment'] = sentiment
        
        percent_positive = (len([score for score in positive_scores if score > 0.5]) / len(positive_scores)) * 100 if positive_scores else 0
        filtered_news_sel = filtered_news.loc[:,['id', 'title', 'link', 'img', 'sentiment']]
        # filtered_news.drop(columns=['sentences'], inplace=True)
    
    return filtered_news_sel, percent_positive

