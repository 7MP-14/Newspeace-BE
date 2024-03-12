from crawling_finance import finance
from sqlalchemy import create_engine
from sqlalchemy.sql import text
import pandas as pd
from datetime import datetime, timedelta

import sys
sys.path.append('../')  # 상위 폴더를 모듈 검색 경로에 추가

from db_info import DATABASES

def update(collection):
    # # mongo
    df_article = pd.DataFrame(list(collection.find())).drop(columns=['_id'])

    # # mysql
    sql_db = DATABASES['default']
    con = create_engine(f"mysql+pymysql://{sql_db['USER']}:{sql_db['PASSWORD']}@{sql_db['HOST']}:{sql_db['PORT']}/{sql_db['NAME']}")
    connection = con.connect()


    query_keyword = "SELECT * FROM accounts_keyword"
    df_keyword = pd.read_sql(query_keyword, con)

    query_enterprise = "SELECT * FROM enterprise_enterprise"
    df_enterprise = pd.read_sql(query_enterprise, con)


    #############################
    # mykeyword 부정도 업데이트
    def contains_keyword(keyword, text):
        if keyword in text:
            return '0'
        else:
            return None

    keywords_list = list(df_keyword.keyword_text)

    negative_list = []
    for keyword in keywords_list:
        df_articles = df_article.copy()
        df_articles.detail = df_articles.detail.apply(lambda x : contains_keyword(keyword, x))
        df_articles.dropna(axis=0, inplace=True)
        
        if not df_articles.empty:
            sentiment = df_articles.sentiment.value_counts()
            total = sentiment.sum()
            
            if -1 in sentiment.index:
                negative = int(round((sentiment[-1] / total), 2) * 100)
                negative_list.append(negative)
            else:
                negative_list.append(0)
        else:
            negative_list.append(0)

    df_keyword['ratio'] = negative_list
    results = df_keyword.to_dict(orient='records')


    # 업데이트 쿼리 생성
    for result in results:
        query = text(f"UPDATE accounts_keyword SET ratio = :ratio WHERE keyword_text = :keyword")
        result = connection.execute(query, {"ratio" : result['ratio'], "keyword" : result['keyword_text']})
        connection.commit()




    #############################
    # 코스피 100 그래프 업데이트
    price = finance(con)
    df_enterprise['price'] = price
    dict_enterprise = df_enterprise.to_dict(orient='records')

    current_datetime = datetime.now()

    result = []
    for enterprise in dict_enterprise:
        df_articles = df_article.copy()
        df_articles.detail = df_articles.detail.apply(lambda x : contains_keyword(enterprise['name'], x))
        df_articles.dropna(axis=0, inplace=True)
        
        if not df_articles.empty:
            sentiment = df_articles.sentiment.value_counts()
            total = sentiment.sum()
            
            if -1 in sentiment.index:
                negative = int(round((sentiment[-1] / total), 2) * 100)
            else:
                negative = 0
        else:
            negative = 0
        
        result.append({
            'negative' : negative,
            'present' : int(enterprise['price'].replace(',', '')),
            'create_dt' : current_datetime,
            'enterprise_id' : enterprise['id']
        })


    # db에 데이터 삽입
    df = pd.DataFrame(result)
    df.to_sql('enterprise_enterprisegraph', con, if_exists='append', index=False)
    
    # db에 데이터 삭제
    time_to_delete = current_datetime - timedelta(days=14) + timedelta(hours=1)

    query = text("DELETE FROM enterprise_enterprisegraph WHERE CREATE_DT < :time_to_delete")
    result = connection.execute(query, {"time_to_delete" : time_to_delete})
    connection.commit()
    
    con.dispose()
    return 'success'
