# 중앙일보, 연예 없음.

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re
import pandas as pd


def joongang():
    category_map = {'정치' : 'politics',
                    '경제' : 'money',
                    '국제' : 'world',
                    '사회' : 'society',
                    '문화' : 'culture',
                    '스포츠' : 'sports'}

    items = []
    today = datetime.now()
    create_dt = today.strftime('%Y.%m.%d %H:%M')
    filter_time = (today - timedelta(hours=3)).strftime('%Y.%m.%d %H:%M')


    for category, code in category_map.items():
        for num in range(1,5):
            url = f'https://www.joongang.co.kr/{code}?page={num}'
            data = requests.get(url)
            soup = BeautifulSoup(data.text, 'html.parser')

            article = soup.find('ul', class_='story_list').find_all('li')
            article_num = len(article)

            
            for i in range(article_num):
                article_detail = article[i]
            
                write_dt = article_detail.find('div', class_='meta').find('p').text
                if write_dt >= filter_time:
                    detail_url = article_detail.find('a')['href']

                    try:
                        img_url = article_detail.find('img')['src']
                        title = article_detail.find('img')['alt']
                    except:
                        img_url = '0'
                        title = article_detail.find('a').text
                        title_filter = re.sub('\n', '', title)
                        title = title_filter

                    detail_data = requests.get(detail_url)
                    detail_soup = BeautifulSoup(detail_data.text, 'html.parser')

                    text_detail = detail_soup.find('div', class_='article_body fs3').text
                    text_detail = re.sub('\n', '', text_detail)

                    items.append({
                        'title' : title,
                        'detail' : text_detail,
                        'category' : category,
                        'link' : detail_url,
                        'img' : img_url,
                        'create_dt' : create_dt,
                        'write_dt' : write_dt,
                        'media' : '중앙일보'
                        })
                else:
                    break
    print(len(items))
    df = pd.DataFrame(items)
    
    return df
