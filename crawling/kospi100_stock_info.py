import requests
import bs4, re

# 코스피100 코드번호
def get_kospi100_codes():
    codes = []

    for page_no in range(1, 11):  
        url = f'https://finance.naver.com/sise/entryJongmok.naver?&page={page_no}'
        source = requests.get(url).text
        soup = bs4.BeautifulSoup(source, 'html.parser')

        # td안에 모든 a태그 추출
        a_tags_list = soup.find_all('td', class_='ctg')[0:10]  # 10개씩
        for a_tags in a_tags_list:
            codes += [re.search(r'code=(\d+)', a['href']).group(1) for a in a_tags.find_all('a', href=True)]  # 코드만 정리

    return codes

data = get_kospi100_codes()
time = '20240214090100' # 설정필요  예시 // 2024.02.14. 09시 01분  *초는 X
no = '1'

headers = {
    'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
}

for code in data:
    day_stock = f'https://finance.naver.com/item/sise_day.naver?code={code}&page={no}'  # 일별 시세  (패이지는 필요 시 수정)

    #시간정해서 뽑을거면 설정필요
    # time_stock = f'https://finance.naver.com/item/sise_time.naver?code=005930&thistime={time}' # 당일 시간별 시세

    source = requests.get(day_stock, headers=headers).text
    soup = bs4.BeautifulSoup(source, 'html.parser')

    date_time = soup.find_all('span', class_='tah p10 gray03') ## 각각 날짜
    day_date = [span.text.replace(',', '') for span in date_time] # 금액만 추출

    names = soup.find_all('span', class_='tah p11')  ## 종가, 시가, 고가 , 저가, 거래량
    prices = [span.text.replace(',', '') for span in names] # 금액만 추출

    Close = []
    Open = []
    High = []
    Low = []
    volumes = []

    # prices 리스트를 순회하면서 각각의 값을 적절한 리스트에 저장
    for i in range(0, len(prices), 5):
        if i + 4 < len(prices):  # 리스트의 길이를 확인하여 범위 내에 있을 경우에만 추가
            Close.append(prices[i])
            Open.append(prices[i + 1])
            High.append(prices[i + 2])
            Low.append(prices[i + 3])
            volumes.append(prices[i + 4])

    print("기업 코드 : ", code)
    print("날짜 : ", day_date)
    print("종가 : ", Close)
    print("시초가 : ", Open)
    print("고가 : ", High)
    print("저가 : ", Low)
    print("거래량 : ", volumes)

    print('\n\n')



# 여기서 코드확인
## https://finance.naver.com/sise/entryJongmok.naver   # 기업리스트

# https://finance.naver.com/item/sise.naver?code={code}  삼성코드 005930  # 기업상세페이지

# https://finance.naver.com/item/sise_day.naver?code=005930  #일별 시세

# https://finance.naver.com/item/sise_time.naver?code=005930&thistime=20240214161052  #시간별 시세