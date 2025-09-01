# Org binance data path: https://data.binance.vision/
#
# 這個是用來下載幣安 Binance 的歷史資料做回測
#



import requests
import xmltodict
import json
import wget
from enum import Enum
import os

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18362',
}


class Future_option_spot:
    future = 'futures'
    option = 'option'
    spot = 'spot'

class Cm_um:
    cm = 'cm'
    um = 'um'

class Daily_monthly:
    daily = 'daily'
    monthly = 'monthly'

class Klines_others:
    klines = 'klines'
    aggTrades = 'aggTrades'
    bookTicker = 'bookTicker'
    fundingRate = 'fundingRate'
    indexPriceKlines = 'indexPriceKlines'
    markPriceKlines = 'markPriceKlines'
    premiumIndexKlines = 'premiumIndexKlines'
    trades = 'trades'

class Period:
    _12h = '12h'
    _15m = '15m'
    _1d = '1d'
    _1h = '1h'
    _1m = '1m'
    _2h = '2h'
    _30m = '30m'
    _3m = '3m'
    _4h = '4h'
    _5m = '5m'
    _6h = '6h'
    _8h = '8h'


# 列出幣安歷史資料上的所有標地
def binance_get_history_list_targets(future_option_spot, cm_um, daily_monthly, klines_others):
    # https://s3-ap-northeast-1.amazonaws.com/data.binance.vision?delimiter=/&prefix=data/futures/um/monthly/klines/
    url = f'https://s3-ap-northeast-1.amazonaws.com/data.binance.vision?delimiter=/&prefix=data/{future_option_spot}/{cm_um}/{daily_monthly}/{klines_others}/'
    # print(url)
    r = requests.get(url, headers=headers)
    xpars = xmltodict.parse(r.text)
    ret = []
    # print(xpars)
    for x in xpars['ListBucketResult']['CommonPrefixes']:
        ret.append(x['Prefix'].split('/')[-2])
    return ret


# 列出幣安歷史資料上的所有檔案
def binance_get_history_list_files_by_target(future_option_spot, cm_um, daily_monthly, klines_others, str_target, period):
    url = f'https://s3-ap-northeast-1.amazonaws.com/data.binance.vision?delimiter=/&prefix=data/{future_option_spot}/{cm_um}/{daily_monthly}/{klines_others}/{str_target}/{period}/'
    print(url)
    r = requests.get(url, headers=headers)
    print(r.text)
    xpars = xmltodict.parse(r.text)
    ret = []
    for x in xpars['ListBucketResult']['Contents']:
        ret.append(x['Key'])
    return ret


def binance_get_history_download_file(str_file_URI, str_dest):
    url = f'https://data.binance.vision/{str_file_URI}'
    try:
        wget.download(url, out=str_dest)
    except:
        print(f"download {url} failed")
        return False
    return True


if __name__ == '__main__':
    # 列出幣安所有標地
    list_targets = binance_get_history_list_targets(Future_option_spot.future, Cm_um.um, Daily_monthly.monthly, Klines_others.klines)
    print(list_targets)


    list_files = binance_get_history_list_files_by_target(Future_option_spot.future, Cm_um.um, Daily_monthly.monthly, Klines_others.klines, list_targets[0], Period._5m)
    print(list_files)


    binance_get_history_download_file(list_files[0], list_files[0].split('/')[-1])

    for target in list_targets:
        if not target.endswith('USDT'):
            continue
        list_files = binance_get_history_list_files_by_target(Future_option_spot.future, Cm_um.um, Daily_monthly.monthly, Klines_others.klines, target, Period._1m)
        for file_url in list_files:
            if not file_url.endswith('.zip'):
                continue
            file_name = file_url.split('/')[-1]

            if os.path.isfile(file_name):
                continue

            print(f'Donwload {file_url} {file_name}')
            binance_get_history_download_file(file_url, file_name)

