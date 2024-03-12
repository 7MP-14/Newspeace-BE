import pandas as pd
import requests
from bs4 import BeautifulSoup

def finance(con):
    # db 연결
    query = 'SELECT * FROM enterprise_enterprise'
    df_t = pd.read_sql(query, con).to_dict(orient='records')

    current_price = []
    for dict_t in df_t:
        code = dict_t['code']

        data = requests.get(f'https://finance.naver.com/item/main.naver?code={code}')
        soup = BeautifulSoup(data.text, 'html.parser')
        res = soup.find('p', class_='no_today').find(class_='blind').text
        current_price.append(res)

    return current_price

