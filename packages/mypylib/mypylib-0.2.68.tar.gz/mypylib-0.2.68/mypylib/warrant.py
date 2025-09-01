import xlrd
import pandas as pd
from collections import defaultdict
import datetime
import re
import requests
import os
from os.path import expanduser
from io import StringIO
import shutil
from loguru import logger

headers = {'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/604.5.6 (KHTML, like Gecko) Version/11.0.3 Safari/604.5.6'}

# 讀取新上市的權證標的
# 從元富的網站讀取
# 有些新上市的權證，當天不會出現在權證達人寶典上面，這樣跟單不會跟到，很可惜，因此在每天開盤之前，讀取當天新上市的權證
# 資料來源: https://newjust.masterlink.com.tw/z/zx/zxc/zxc.djhtm?a=2&page=1
# 讀取進來之後轉換成
'''
{0: '031982',
  1: '中鴻永豐27購01',
  2: '認購',
  3: '111/12/14',
  4: '111/12/16',
  5: "<!-- \tGenLink2stk('AS2014','中鴻'); //-->",
  6: '34.78'},
'''


def get_proxy_settings():
    # Retrieve proxy settings using os.environ (like a dictionary)
    http_proxy = os.environ.get('HTTP_PROXY') or os.environ.get('http_proxy')
    https_proxy = os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')

    # Using os.getenv() method to specify a default value if the variable is not found
    # Example: os.getenv('HTTP_PROXY', 'Default Value')

    # logger.info(f'HTTP PROXY: {http_proxy}')
    # logger.info(f'HTTPS PROXY: {https_proxy}')

    if http_proxy is None:
        return None

    return {
        "HTTP Proxy": http_proxy,
        "HTTPS Proxy": https_proxy
    }


#
# 之後傳回 list
# ('T' or 'N', symbol, name, 上市日期)

@logger.catch
def get_new_warrant_list():
    import pandas as pd
    from time import sleep

    logger.info('下載新權證資料')

    df = pd.DataFrame()

    count_no_data = 0

    for i in range(1, 9999):
        url = f'https://newjust.masterlink.com.tw/z/zx/zxc/zxc.djhtm?a=2&page={i}'
        # 元富把 pd.read_html() 檔掉了...，所以得用別的方式去讀取
        # ret = requests.get(url, headers={'User-agent': 'Mozilla/5.0'}).text
        # df_tmp = pd.read_html(requests.get(url, headers={'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/604.5.6 (KHTML, like Gecko) Version/11.0.3 Safari/604.5.6'}).text)

        response = requests.get(url, headers=headers, proxies=get_proxy_settings(), verify=False)
        html_data = StringIO(response.text)
        df_tmp = pd.read_html(html_data)

        # sleep(1)
        df_tmp = df_tmp[2].iloc[2:]
        # df_tmp.columns = df_tmp.iloc[0]

        # logger.info(f'{i} {df_tmp.shape}')
        if df_tmp.shape[0] == 1:
            count_no_data += 1
            if count_no_data > 3:
                break
            else:
                continue
        # logger.info(df_tmp)
        df = pd.concat([df, df_tmp])

    df = df.dropna()
    df_list = df.to_dict('records')
    # {0: '720593', 1: '力致群益46購01', 2: '認購', 3: '113/06/21', 4: '113/06/25', 5: "<!-- \tGenLink2stk('AS3483','力致'); //-->", 6: '311.11'}
    # {0: '720594', 1: '中美晶群益42購01', 2: '認購', 3: '113/06/21', 4: '113/06/25', 5: "<!-- \tGenLink2stk('AS5483','中美晶'); //-->", 6: '256.00'}
    # {0: '720595', 1: '旺玖群益3C購01', 2: '認購', 3: '113/06/21', 4: '113/06/25', 5: "<!-- \tGenLink2stk('AS6233','旺玖'); //-->", 6: '46.66'}
    # {0: '720596', 1: '茂綸群益3C購01', 2: '認購', 3: '113/06/21', 4: '113/06/25', 5: "<!-- \tGenLink2stk('AS6227','茂綸'); //-->", 6: '100.00'}
    # {0: '720597', 1: '晟德群益3C購03', 2: '認購', 3: '113/06/21', 4: '113/06/25', 5: "<!-- \tGenLink2stk('AS4123','晟德'); //-->", 6: '82.00'}
    # {0: '720598', 1: '醫揚群益42購01', 2: '認購', 3: '113/06/21', 4: '113/06/25', 5: "<!-- \tGenLink2stk('AS6569','醫揚'); //-->", 6: '310.00'}

    print(df_list)

    list_new_warrants = []
    for d in df_list:

        if isinstance(d[5], str) and d[5][0] == '<':
            ret = re.search(r'.*GenLink2stk\((\'AS(.*)\',\'(.*)\')\)', d[5])
            if ret is None:
                continue
            symbol = ret.group(2)
            name = ret.group(3)
            list_new_warrants.append(('T', d[0], d[1], d[2], symbol, name, d[4], d[6]))
            # logger.info('T', symbol, name, d[4])
        else:
            list_new_warrants.append(('N', d[0], d[1], d[2], d[5], d[5], d[4], d[6]))
            # logger.info('N', d[5], d[4])

    return list_new_warrants


#
# 0 日期：
# 1
# 2
# 3 權證
# 4 代碼
# 5 03027Q
# 6 03028Q
#

# dict_warrant_to_info:
#   list_warrant.keys() = ['064474', '065228', '065395'.....
#    {'權證名稱': '世紀鋼兆豐23購02', '發行券商': '兆豐', '權證價格': 0.3, '權證漲跌': 0, '權證漲跌幅': 0, '權證成交量': 0,
#    '權證買價': 0.25, '權證賣價': 0.26, '權證買賣價差': 0.04, '溢價比率': 0.431, '價內價外': 0.27385, '理論價格': 0.251,
#    '隱含波動率': 0.4703, '有效槓桿': 5.39, '剩餘天數': 235, '最新行使比例': 0.059, '標的代碼': '9958', '標的名稱': '世紀鋼',
#    '標的價格': 94.4, '標的漲跌': -1.9, '標的漲跌幅': -0.0197, '最新履約價': 130, '最新界限價': '-', '標的20日波動率': 0.4206,
#    '標的60日波動率': 0.382046, '標的120日波動率': 0.380576, '權證DELTA': 0.0145, '權證GAMMA': 0.0005, '權證VEGA': 0.0137,
#    '權證THETA': -0.0021, '內含價值': 0, '時間價值': 0.255, '流通在外估計張數': 0, '流通在外增減張數': 0, '上市日期': '2022/07/08',
#    '到期日期': '2023/03/07', '最新發行量': 5000, '權證發行價': 0.691, '認購/售類別': '認購'}
#
#
# dict_stock_to_warrant:
#   stock_warrant_map.keys() = ['6548', '6568', '6582', '6589'...]
#   stock_warrant_map['6548'] = ['05184P', '05339P', '05360P'....]

def read_warrant_bible(path_file='權證達人寶典_NEWVOL_2022-07-15.xls') -> (dict, defaultdict[list]):
    # xls = pd.ExcelFile(r"權證達人寶典_NEWVOL_2022-06-29.xls")
    xls = pd.ExcelFile(path_file)

    # Parse Sheet 0: summary
    summary = xls.parse(0)

    name1 = list(summary.iloc[2])  # 權證
    name2 = list(summary.iloc[3])  # 代碼
    new_name = []
    # 合併這兩欄位
    for x, y in zip(name1, name2):
        new_name.append(x + y)

    df: pd.DataFrame = summary.copy()
    # 合併後的名稱變成欄位名稱，這樣才不會有重複
    df.columns = new_name
    df = df.iloc[4:, :]
    df.set_index('權證代碼', inplace=True)
    dict_warrant_to_info = df.to_dict(orient='index')

    dict_stock_to_warrant = defaultdict(list)

    date_today = datetime.datetime.today()

    del xls

    for x in dict_warrant_to_info:
        date_due = datetime.datetime.strptime(dict_warrant_to_info[x]['到期日期'], '%Y/%m/%d')
        days_number_due = (date_due - date_today).days
        dict_warrant_to_info[x]['到期天數'] = days_number_due
        dict_warrant_to_info[x]['Volume'] = 0
        code = dict_warrant_to_info[x]['標的代碼']
        dict_stock_to_warrant[code].append(x)

    # logger.info(stock_warrant_map)
    return dict_warrant_to_info, dict_stock_to_warrant


def add_new_issued_warrant_to_bible(dict_warrant_to_info, dict_stock_to_warrant, list_new_warrants):
    # ('T', '06227P', '南電麥證26售01', '認售', '8046', '南電', '111/12/22')
    # ('N', '06228P', '臺股指麥證26售15', '認售', '加權指數', '加權指數', '111/12/22')

    for x in list_new_warrants:
        if x[0] == 'N':
            continue
        if x[3] != '認購':
            continue
        if x[1] not in dict_warrant_to_info.keys():
            year, month, day = x[6].split('/')
            year = int(year) + 1911
            date_to_file = f'{year}/{month}/{day}'

            logger.info(f'新權證: {x[1]} {x[2]} {x[6]} {date_to_file} {x[7]}')

            dict_warrant_to_info[x[1]] = {
                '權證名稱': x[2],
                '發行券商': x[2],
                '權證價格': 0,
                '權證漲跌': 0,
                '權證漲跌幅': 0,
                '權證成交量': 0,
                '權證買價': 0,
                '權證賣價': 0,
                '權證買賣價差': 2,
                '溢價比率': '-',
                '價內價外': '-',
                '理論價格': '-',
                '隱含波動率': '-',
                '有效槓桿': '-',
                '剩餘天數': 999,    # 用 999 天來代表今天才新加入的權證
                '最新行使比例': 0,
                '標的代碼': x[4],
                '標的名稱': x[5],
                '標的價格': '-',
                '標的漲跌': '-',
                '標的漲跌幅': '-',
                '最新履約價': x[7],
                '最新界限價': '-',
                '標的20日波動率': 0,
                '標的60日波動率': 0,
                '標的120日波動率': 0,
                '權證DELTA': '-',
                '權證GAMMA': '-',
                '權證VEGA': '-',
                '權證THETA': '-',
                '內含價值': '-',
                '時間價值': '-',
                '流通在外估計張數': 0,
                '流通在外增減張數': 0,
                '上市日期': date_to_file,
                '到期日期': (datetime.datetime.today() + datetime.timedelta(days=1000)).strftime('%Y/%m/%d'),
                '最新發行量': 0,
                '權證發行價': 0,
                '認購/售類別': x[3],
                '到期天數': 180,
                'Volume': 0
            }

            dict_stock_to_warrant[x[4]].append(x[1])
    return dict_warrant_to_info, dict_stock_to_warrant


def warrant_bible_convert_to_c_need(dict_warrant_to_info, str_date=None):
    if str_date is None:
        today = datetime.datetime.today()
    else:
        today = datetime.datetime.strptime(str_date, '%Y-%m-%d')

    target_file = f'/home/william/warrant/warrant_bible.txt'
    target_file2 = f'/home/william/warrant/warrant_bible_{today.strftime("%Y-%m-%d")}.txt'

    with open(target_file2, 'w+') as fp2:
        with open(target_file, "w+") as fp:
            for warrant in dict_warrant_to_info:
                day_end = datetime.datetime.strptime(dict_warrant_to_info[warrant]['到期日期'], '%Y/%m/%d')
                fp.write(f'{warrant}\t'
                        f'{dict_warrant_to_info[warrant]["標的代碼"]}\t'
                        f'{dict_warrant_to_info[warrant]["認購/售類別"]}\t'
                        f'{dict_warrant_to_info[warrant]["流通在外估計張數"]}\t'
                        f'{(day_end - today).days}\t'
                        f'{dict_warrant_to_info[warrant]["發行券商"]}\t'
                        f'{dict_warrant_to_info[warrant]["最新行使比例"]}\t'
                        f'{dict_warrant_to_info[warrant]["有效槓桿"]}\t'
                        f'{dict_warrant_to_info[warrant]["最新履約價"]}\t'
                        f'{dict_warrant_to_info[warrant]["權證DELTA"]}\n')
                fp2.write(f'{warrant}\t'
                        f'{dict_warrant_to_info[warrant]["標的代碼"]}\t'
                        f'{dict_warrant_to_info[warrant]["認購/售類別"]}\t'
                        f'{dict_warrant_to_info[warrant]["流通在外估計張數"]}\t'
                        f'{(day_end - today).days}\t'
                        f'{dict_warrant_to_info[warrant]["發行券商"]}\t'
                        f'{dict_warrant_to_info[warrant]["最新行使比例"]}\t'
                        f'{dict_warrant_to_info[warrant]["有效槓桿"]}\t'
                        f'{dict_warrant_to_info[warrant]["最新履約價"]}\t'
                        f'{dict_warrant_to_info[warrant]["權證DELTA"]}\n')


@logger.catch
def download_latest_warrant_bible():
    day_now = datetime.datetime.now()

    while True:
        str_date = day_now.strftime('%Y-%m-%d')
        target_file = f'/home/william/warrant/warrant-{str_date}.xls'
        url = f'https://iwarrant.capital.com.tw/wdataV2/canonical/capital-newvol/%E6%AC%8A%E8%AD%89%E9%81%94%E4%BA%BA%E5%AF%B6%E5%85%B8_NEWVOL_{str_date}.xls'
        logger.info(f'下載權證達人寶典: {url}')

        try:
            # Use verify=True for proper HTTPS certificate verification
            with requests.get(url, proxies=get_proxy_settings(), headers=headers, verify=True) as r:
                r.raise_for_status()
            with open(target_file, 'wb') as f:
                for chunk in r:
                    if chunk:
                        f.write(chunk)

            break
        except requests.exceptions.SSLError as e:
            logger.error(f"SSL Certificate error: {e}")
            # If SSL verification fails, try with verify=False as fallback
            try:
                with requests.get(url, proxies=get_proxy_settings(), headers=headers, verify=False) as r:
                    r.raise_for_status()
                with open(target_file, 'wb') as f:
                    for chunk in r:
                        if chunk:
                            f.write(chunk)
                break
            except Exception as e:
                logger.error(e)
                day_now -= datetime.timedelta(days=1)
        except Exception as e:
            logger.error(e)
            day_now -= datetime.timedelta(days=1)


def get_last_warrant_bible_date():
    files = os.listdir(f'/home/william/warrant')
    files.sort(reverse=True)
    file = ''
    for file in files:
        if file.startswith('warrant') and file.endswith('.xls'):
            bool_found = True
            # warrant-2024-04-12.xls
            return file[8:18]
    return None


def warrant_bible_do_all():
    logger.info('download_latest_warrant_bible')
    download_latest_warrant_bible()
    logger.info('get_last_warrant_bible_date')
    date_str = get_last_warrant_bible_date()
    logger.info('read_warrant_bible')
    dict_warrant_to_info, dict_stock_to_warrant = read_warrant_bible(f'/home/william/warrant/warrant-{date_str}.xls')
    logger.info('get_new_warrant_list')
    list_new_warrants = get_new_warrant_list()
    logger.info('add_new_issued_warrant_to_bible')
    dict_warrant_to_info, dict_stock_to_warrant = add_new_issued_warrant_to_bible(dict_warrant_to_info,
                                                                                  dict_stock_to_warrant,
                                                                                  list_new_warrants)
    logger.info('warrant_bible_convert_to_c_need')
    warrant_bible_convert_to_c_need(dict_warrant_to_info)


if __name__ == '__main__':
    import datetime

    download_latest_warrant_bible()

    if False:
        # 2024-04-12
        date_str = get_last_warrant_bible_date()

        dict_warrant_to_info, dict_stock_to_warrant = read_warrant_bible(f'/home/william/warrant/warrant-{date_str}.xls')
        list_new_warrants = get_new_warrant_list()

        dict_warrant_to_info, dict_stock_to_warrant = add_new_issued_warrant_to_bible(dict_warrant_to_info,
                                                                                    dict_stock_to_warrant,
                                                                                    list_new_warrants)
        warrant_bible_convert_to_c_need(dict_warrant_to_info, str_date=date_str)
