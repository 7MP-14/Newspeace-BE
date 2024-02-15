# 디지털타임스

import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from datetime import datetime, timedelta


def times():
    def decoding(text):
        filter_text = text.encode('latin1').decode('cp949')
        return filter_text

    today = datetime.now()
    create_dt = today.strftime('%Y-%m-%d %H:%M')
    start_time = (today - timedelta(hours=3)).strftime('%Y-%m-%d %H:%M')

    category_map = {'정치' : '2400',
                    '경제' : '3200',
                    '국제' : '2300',
                    '사회' : '3700',
                    '금융' : '3100'}

    items = []


    for category, code in category_map.items():
        url = f'https://www.dt.co.kr/section.html?section_num={code}'
        data = requests.get(url)
        soup = BeautifulSoup(data.text, 'html.parser')

        page_list = soup.find('div', class_='page').text.split('\n')[:-1]
        page = len(page_list)
        
        for i in range(1,page+1):
            url = f'https://www.dt.co.kr/section.html?section_num={code}&cpage={i}'
            data = requests.get(url)
            soup = BeautifulSoup(data.text, 'html.parser')
            
            article = soup.find_all('dl', class_='article_list')
            num = len(article)
            for j in range(num):
                write_dt = article[j].find(class_='date').text.split(': ')[1]
                
                if write_dt >= start_time:
                    url = 'https:'+article[j].find('a')['href']
                    try:
                        img_url = 'https:'+article[j].find('img')['src']
                    except:
                        img_url = '0'

                    detail_data = requests.get(url)
                    detail_soup = BeautifulSoup(detail_data.text, 'html.parser')

                    title = decoding(detail_soup.find('h1', class_='art_tit').text)

                    detail = decoding(detail_soup.find('div', class_='article_view').text)
                    text_detail = re.sub('\n', '', detail)
                    
                    items.append({
                        'title' : title,
                        'detail' : text_detail,
                        'category' : category,
                        'link' : url,
                        'img' : img_url,
                        'create_dt' : create_dt,
                        'write_dt' : write_dt,
                        'media' : '디지털타임스'
                    })

    df = pd.DataFrame(items)

    return df
