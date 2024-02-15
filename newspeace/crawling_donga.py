# 동아일보,

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re
import pandas as pd


def donga():
    category_map = {'정치' : 'Politics',
                    '경제' : 'Economy',
                    '국제' : 'Inter',
                    '사회' : 'Society',
                    '문화' : 'Culture',
                    '연예' : 'Entertainment',
                    '스포츠' : 'Sports'}

    items = []
    today = datetime.now()
    create_dt = today.strftime('%Y-%m-%d %H:%M')
    filter_time = (today - timedelta(hours=3)).strftime('%Y-%m-%d %H:%M')

    for category, code in category_map.items():
        num = 1
        while 1:
            temp = []
            url = f'https://www.donga.com/news/{code}/List?p={num}&prod=news&ymd=&m='
            data = requests.get(url)
            soup = BeautifulSoup(data.text, 'html.parser')    
            filter_list = soup.find_all('div', class_='articleList article_list')
            list_num = len(filter_list)
            
            for i in range(list_num):
                filter = filter_list[i]
                write_dt = filter.find('div', class_='rightList').find(class_='date').text

                if write_dt >= filter_time:
                    
                    url = filter.find('a')['href']
                    try:
                        title = filter.find('img')['alt']
                    except:
                        title = filter.find('span', class_='tit').text
                        
                    try:
                        img_url = filter.find('img')['src']
                    except:
                        img_url = img_url
                    
                    data_detail = requests.get(url)
                    soup_detail = BeautifulSoup(data_detail.text, 'html.parser')
                    text_detail = soup_detail.find('div', class_='article_txt').text
                    text_detail = re.sub('\n', '', text_detail)
                            
                    temp.append({
                        'title' : title,
                        'detail' : text_detail,
                        'category' : category,
                        'link' : url,
                        'img' : img_url,
                        'create_dt' : create_dt,
                        'write_dt' : write_dt,
                        'media' : '동아일보'
                    })

                else:
                    break
                
            if len(temp) != 0:
                items.extend(temp)
                num += 20
            else:
                break
            
    df = pd.DataFrame(items)
    return df