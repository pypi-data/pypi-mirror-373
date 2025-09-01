
import pandas as pd

import datetime as datetime
import requests
import os
from pandasql import sqldf


dataset_future_daily = "TaiwanFuturesDaily"  # 期貨日K
dataset_future_ticks = "TaiwanFuturesTick"  # 期貨tick
dataset_major3 = "TaiwanFuturesInstitutionalInvestors"  # 期貨三大法人買賣表
dataset_index_5sec = "TaiwanStockEvery5SecondsIndex"  # 每5秒指數統計
dataset_TWSE_5sec = "TaiwanVariousIndicators5Seconds"  # 加權指數5秒

dataset_TWSE_order_5sec = "TaiwanStockStatisticsOfOrderBookAndTrade"  # 每5秒委託成交統計

token_default = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJkYXRlIjoiMjAyMS0wNi0wNyA" \
                "yMToyNTo1MSIsInVzZXJfaWQiOiJjYXJleWpvdSIsImlwIjoiMTAzLjIyNC4y" \
                "MDEuOTUifQ.ncFRCARkaezyI711PlZtauprfDDSwg_7VNYgh8SDET0"



def get_finMind_date_range(date_start: datetime.datetime,
                           date_end: datetime.datetime,
                           target,
                           folder,
                           dataset,
                           bool_force_download=False,
                           token=token_default,
                           ):

    print(f'Download {dataset} to {folder} since {date_start} to {date_end}.')

    url = "https://api.finmindtrade.com/api/v4/data"

    if not os.path.exists(folder):
        os.makedirs(folder)
    folder_days = folder + "/days"
    path_daily_csv = f'{folder}/{folder}.csv'
    if not os.path.exists(folder_days):
        os.makedirs(folder_days)

    if bool_force_download is False:
        files = os.listdir(folder_days)
        files.sort()
        if len(files) > 0:
            date_start_tmp = datetime.datetime.strptime(files[-1][0:10], '%Y-%m-%d')
            date_start = date_start if date_start_tmp < date_start else date_start_tmp

    while date_start <= date_end:
        if date_start.weekday() > 5:
            date_start = date_start + datetime.timedelta(days=1)
            continue

        date = str(date_start.date())
        print(date, date_start.weekday())
        if dataset in [dataset_future_daily, dataset_future_ticks]:
            parameter = {
                "dataset": dataset,
                "data_id": target,
                "start_date": date,
                "token": token,
            }
        elif dataset == dataset_major3:
            parameter = {
                "dataset": dataset,
                "data_id": target,
                "start_date": date,
                "end_date": date,
                "token": token,
            }
        else:
            parameter = {
                "dataset": dataset,
                "start_date": date,
                "token": token,
            }
        filepath = f'{folder_days}/{date}.csv'
        if os.path.isfile(filepath):
            date_start = date_start + datetime.timedelta(days=1)
            continue
        # print(url, parameter)
        data = requests.get(url, params=parameter)
        # print(data)
        data = data.json()
        data = pd.DataFrame(data['data'])

        # 將每日所有股票當沖的資料存在TaiwanStockDayTrading/days的目錄中
        if data.shape[0] > 60 or (dataset == dataset_major3 and data.shape[0] > 3):
            data.to_csv(filepath)
            print(f"success to save {filepath}, shape:{data.shape[0]}")
            data.to_csv(path_daily_csv)
        else:
            if data.shape[0] > 0:
                print(f"fail to save {filepath}, shape:{data.shape[0]}")
            else:
                print(data)
        date_start = date_start + datetime.timedelta(days=1)


# 可以擴充成 TX EX FX
def get_finMind_TX_ticks(date_start,
                         date_end,
                         folder_dest,
                         bool_force_download=False,
                         token=token_default):

    get_finMind_date_range(date_start=date_start,
                           date_end=date_end,
                           target='TX',
                           folder=folder_dest,
                           dataset='TaiwanFuturesTick',
                           bool_force_download=bool_force_download,
                           token=token)


def get_finMind_TAIEX_day_KLine(date_start: datetime.datetime, date_end: datetime.datetime, filename_dest):
    url = "https://api.finmindtrade.com/api/v4/data"
    parameter = {
        "dataset": 'TaiwanStockPrice',
        "data_id": "TAIEX",
        "start_date": str(date_start.date()),
        "end_date": str(date_end.date()),
        "token": token_default,
    }
    data = requests.get(url, params=parameter)
    data = data.json()
    data = pd.DataFrame(data['data'])
    print(data)

    data.to_csv(filename_dest)


def get_finMind_TaiwanStockDayTrading(date_start: datetime.datetime, date_end: datetime.datetime):
    get_finMind_date_range(date_start=date_start,
                           date_end=date_end,
                           target='TaiwanStockDayTrading',
                           folder='TaiwanStockDayTrading',
                           dataset='TaiwanStockDayTrading',
                           bool_force_download=False,
                           token=token_default)


def get_findMind_TaiwanStockPrice(date_start: datetime.datetime, date_end: datetime.datetime):
    get_finMind_date_range(date_start=date_start,
                           date_end=date_end,
                           target='TAIEX',
                           folder='TaiwanStockPrice',
                           dataset='TaiwanStockPrice',
                           bool_force_download=False,
                           token=token_default)




if __name__ == '__main__':
    date_end = datetime.datetime.today()
    date_start = date_end - datetime.timedelta(days=10)

    if False:
        get_finMind_TX_ticks(date_start=date_start,
                             date_end=date_end,
                             folder_dest='TaiwanFuturesTick')

    if False:
        get_finMind_TAIEX_day_KLine(date_start, date_end, 'TAIEX.txt')

    if False:
        get_finMind_TaiwanStockDayTrading(date_start, date_end)

    if True:
        get_findMind_TaiwanStockPrice(date_start, date_end)
