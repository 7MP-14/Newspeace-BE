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

