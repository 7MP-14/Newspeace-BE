from keybert import KeyBERT
from mecab import MeCab
from collections import Counter
import pandas as pd

def extract_and_assign_keywords(data, top_n=5):
    kw_model = KeyBERT('distilbert-base-nli-mean-tokens')
    mecab = MeCab()

    all_keywords = []
    data['keywords'] = '' 

    for idx, text in enumerate(data['title']):
        keywords = kw_model.extract_keywords(text, top_n=top_n, keyphrase_ngram_range=(1, 1))
        filtered_keywords = []

        for keyword, _ in keywords:
            pos = mecab.pos(keyword)
            if any(tag in ['NNG', 'NNP'] for word, tag in pos):
                filtered_keywords.append(keyword)
                all_keywords.append(keyword)

        data.at[idx, 'keywords'] = filtered_keywords[:top_n]

    topiclist = [item[0] for item in Counter(all_keywords).most_common(top_n)]

    return data, topiclist


data = pd.read_csv('data.csv')


# Usage example
updated_data, topiclist = extract_and_assign_keywords(data, top_n=5)
print(updated_data['keywords'])
print(topiclist)

def filter_rows_by_keyword(data, keyword):
    return data[data['keywords'].apply(lambda x: any(keyword in sublist for sublist in x))]

def extract_related_keywords(filtered_data, top_n=5):
    all_nouns = []
    mecab = MeCab()

    for text in filtered_data['title']:
        pos = mecab.pos(text)
        nouns = [word for word, tag in pos if tag in ['NNG', 'NNP']]
        all_nouns.extend(nouns)

    return [item[0] for item in Counter(all_nouns).most_common(top_n)]

keyword_to_search = "박물관" 
filtered_data = filter_rows_by_keyword(updated_data, keyword_to_search)

related_keywords = extract_related_keywords(data[10:30], top_n=5)


# print("필터링 :", filtered_data)
print("연관 검색어:", related_keywords)
