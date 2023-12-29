import pandas as pd
import os

# 현재 스크립트 파일이 위치한 디렉토리
current_directory = os.path.dirname(os.path.abspath(__file__))

# df_krx.csv 파일의 절대 경로
file_path = os.path.join(current_directory, 'static', 'api', 'df_krx.csv')

def get_code_from_df_krx(name):
    # df_krx.csv 파일에서 name에 해당하는 code를 찾아 반환하는 로직을 작성
    df_krx = pd.read_csv(file_path)  # 실제 파일 경로로 수정

    # 키워드가 기업명이면 기업코드를 반환한다.
    matching_row = df_krx[df_krx['Name'] == name]
    if not matching_row.empty:
        return matching_row.iloc[0]['Code']
    else:
        return None  # 일치하는 데이터가 없을 경우 None 반환
    

import mojito
import pprint

# print(mojito.__version__)

file_path2 = os.path.join(current_directory, 'static', 'api', 'koreainvestment.key')

f = open(file_path2)
lines = f.readlines()
key = lines[0].strip()
secret = lines[1].strip()
acc_no = lines[2].strip()
f.close()


broker=mojito.KoreaInvestment(
    api_key=key,
    api_secret=secret,
    acc_no=acc_no
)

# print(broker)

# resp = broker.fetch_price("035720")
 
def get_price(code):
    if code==None:
        present=0
    else:
        resp = broker.fetch_price(code)
    # pprint.pprint(resp)
    # print("Open:  ", resp['output']['stck_oprc'])  # 시가
    # print("High : ", resp['output']['stck_hgpr'])  # 고가
    # print("Low  : ", resp['output']['stck_lwpr'])  # 저가
    # print("Close: ", resp['output']['stck_prpr'])  # 현재가&종가
    
        present = resp['output']['stck_prpr']
    
    return present

