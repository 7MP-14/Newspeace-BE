# kbs

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re
import pandas as pd
import json

def kbs():
    today = datetime.now()
    date = today.strftime('%Y%m%d')
    create_dt = today.strftime('%Y-%m-%d %H:%M')

    end_time = today.strftime('%Y%m%d%H%M%S')
    start_time = (today - timedelta(hours=3)).strftime('%Y%m%d%H%M%S')

    url = f'https://news.kbs.co.kr/news/pc/category/category.do#{date}'
    data = requests.get(url)
    soup = BeautifulSoup(data.text, 'html.parser')

    category_list = ['정치', '경제', '사회', '문화', 'IT·과학', '국제', '스포츠', '연예']


    category_list_all = soup.find(class_='menues').find_all('li')
    num = len(category_list_all)

    cate_link = []
    sports_code = '0002%2C0010%2C0011%2C0012%2C0013%2C0014%2C0015%2C0047%2C0048%2C0049%2C0050%2C0051%2C0052%2C0065%2C0053%2C0054%2C0055%2C0056%2C0057%2C0058%2C0059%2C0060%2C0061%2C0062%2C0063%2C0066'
    entertainments_code = '0039%2C0041%2C0043%2C0093'

    for i in range(num):
        category = category_list_all[i].text[1:-1]
        if category in category_list:
            if category == '스포츠':
                cate_link.append({f'{category}' : sports_code})
            elif category == '연예':
                cate_link.append({f'{category}' : entertainments_code})
            else:
                cate_link.append({f'{category}' : soup.find(class_='menues').find_all('a')[i]['href'][-4:]})
                
    items = []
    for cate in cate_link:
        for category, code in cate.items():
            cnt = 1
            while 1:
                link = f'https://news.kbs.co.kr/api/getNewsList?currentPageNo={cnt}&rowsPerPage=12&exceptPhotoYn=Y&datetimeBegin={start_time}&datetimeEnd={end_time}&contentsCode={code}&localCode=00'

                response = requests.get(link)
                filter = response.json()['data']

                num = len(filter)
                
                if num != 0:
                    for i in range(num):
                        article = filter[i]
                        try:
                            text_detail = article['originNewsContents']
                            text_detail = re.sub('\n', '', text_detail)
                        except:
                            text_detail = article['newsContents']

                        try:
                            img_url = 'https://news.kbs.co.kr' + article['imgUrl']
                        except:
                            img_url = '0'
                            
                        items.append({
                            'title' : article['newsTitle'],
                            'detail' : text_detail,
                            'category' : category,
                            'link' : 'https://news.kbs.co.kr/news/pc/view/view.do?ncd=' + article['newsCode'],
                            'img' : img_url,
                            'create_dt' : create_dt,
                            'write_dt' : article['regDate'][:-3],
                            'media' : 'kbs'
                        })
                    cnt += 1
                else:
                    break
                
    df = pd.DataFrame(items)
    return df
