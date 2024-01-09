import os
import pandas as pd
from datetime import datetime

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
import pprint as pp

# print(mojito.__version__)

# file_path2 = os.path.join(current_directory, 'static', 'api', 'koreainvestment.key')

# f = open(file_path2)
# lines = f.readlines()
# key = lines[0].strip()
# secret = lines[1].strip()
# acc_no = lines[2].strip()
# f.close()


# broker=mojito.KoreaInvestment(
#     api_key=key,
#     api_secret=secret,
#     acc_no=acc_no
# )

# print(broker)

# resp = broker.fetch_price("035720")


def broker_run_once_daily():
    today = datetime.today().date()
    current_directory = os.path.dirname(os.path.abspath(__file__))
    log_file_path = os.path.join(current_directory, 'static', 'api', 'logfile_date.log')

    # Check if the function has already run today
    if os.path.exists(log_file_path):
        with open(log_file_path, "r") as log_file:
            log_content = str(log_file.read().strip())
            
            try:
                last_run_date = datetime.strptime(log_content, "%Y-%m-%d").date()
            except ValueError as e:
                print(f"Error parsing log content: {e}")
                # Handle the error accordingly
                return

            if last_run_date == today:
                # print('run in broker_run_once_daily')
                print("my_function has already run today. Exiting.")
                return 
            else:
                print('run!!')

    else:
        today_date = datetime.today().date()
    
        with open(log_file_path, "w") as log_file:
            log_file.write(today_date.strftime("%Y-%m-%d"))
        

    # Execute the function
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

    # Save the current date to the log file
    with open(log_file_path, "w") as log_file:
        log_file.write(today.strftime("%Y-%m-%d"))
        
    return broker

 
 
def get_broker():
    current_directory = os.path.dirname(os.path.abspath(__file__))
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
    
    return broker
 
 
def get_price(code, add=None):
    # broker = broker_run_once_daily()

    # if broker:
    #     print("get_price in utils")
    #     print("my_function has already run today. Exiting.")
    #     print()
    #     pass
    # else:
    #     print("today run")
    #     broker=mojito.KoreaInvestment(
    #     api_key=key,
    #     api_secret=secret,
    #     acc_no=acc_no
    #     )

    # broker=mojito.KoreaInvestment(
    #     api_key=key,
    #     api_secret=secret,
    #     acc_no=acc_no
    #     )
    
    try:
        broker = get_broker()
    except:
        current_directory = os.path.dirname(os.path.abspath(__file__))
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
    
    if code==None:
        present = 0
        return [present]
    else:
        try:
            resp = broker.fetch_price(code)
        except:
            broker=mojito.KoreaInvestment(
            api_key=key,
            api_secret=secret,
            acc_no=acc_no
            )
            
            resp = broker.fetch_price(code)
              
        present = resp['output']['stck_prpr']
        dod = resp['output']['prdy_vrss']  # 전일 대비 (DayofDay)
        open = resp['output']['stck_oprc']  # 시가
        high = resp['output']['stck_hgpr']  # 고가
        low = resp['output']['stck_lwpr']  # 저가
    
        if add:
            add = resp['output'][add]  # 추가 데이터
            return present, dod, open, high, low, add
    
        return present, dod, open, high, low



