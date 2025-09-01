#
# Memo
# For MAC: xattr -d com.apple.quarantine chromedriver
#

import threading
from loguru import logger
import os
import json
from mypylib import tLineNotify
import requests
from time import sleep


# {'code': '000000',
#  'message': None,
#  'messageDetail': None,
#  'data': {'otherPositionRetList': [{'symbol': 'RAYUSDT',
#     'entryPrice': 0.868,
#     'markPrice': 0.84455693,
#     'pnl': -10.80256665,
#     'roe': -0.27757833,
#     'updateTime': [2022, 7, 15, 2, 6, 45, 216000000],
#     'amount': 460.8,
#     'updateTimeStamp': 1657850805216,
#     'yellow': False,
#     'tradeBefore': False},

class w:
    symbol = 'symbol'
    entryPrice = 'entryPrice'
    markPrice = 'markPrice'
    pnl = 'pnl'
    roe = 'roe'
    updateTime = 'updateTime'
    amount = 'amount'
    updateTimeStamp = 'updateTimeStamp'
    yellow = 'yellow'
    tradeBefore = 'tradeBefore'


def binance_leaderboard_getOtherPosition2(trader_UID):
    url = "https://binance-futures-leaderboard1.p.rapidapi.com/v1/getOtherPosition"
    querystring = {"encryptedUid": trader_UID}
    headers = {"X-RapidAPI-Key": "51ff4172e5mshc2031f8b0b43d3ep134274jsnf5ecaf5c38ef",
               "X-RapidAPI-Host": "binance-futures-leaderboard1.p.rapidapi.com"
               }
    response = requests.request("GET", url, headers=headers, params=querystring)
    # print(response.json())
    return response.json()


def binance_leaderboard_getOtherPosition(trader_UID):
    endpoint = "https://www.binance.com/bapi/futures/v1/public/future/leaderboard/getOtherPosition"
    params = {"encryptedUid": trader_UID, "tradeType": "PERPETUAL"}
    headers = {"content-type": "application/json;charset=UTF-8"}
    response = requests.post(endpoint, json=params, headers=headers)  # Add proxies = proxyDict # Attention to JSON = PARAMS
    logger.debug(response.text)
    result = response.json()
    return result


class Binance_position_monitor(threading.Thread):
    url_format = 'https://www.binance.com/en/futures-activity/leaderboard/user?uid={}&tradeType=PERPETUAL'

    def __init__(self,
                 file_monitor_list='./binance_watch_list.txt',
                 dir_positions_logger='.',
                 api_version=1):
        threading.Thread.__init__(self)
        self.to_stop = threading.Event()

        self.file_monitor_list = file_monitor_list
        self.dir_positions_logger = dir_positions_logger

        self.time_to_sleep = 1

        self.list_victim = []

        self.count_usage = 0
        self.count_max_usages = 60

        self.line_sender: tLineNotify = None

        self.api_version = api_version

    @logger.catch
    def load_victim_list(self):
        with open(self.file_monitor_list) as fp:
            for line in fp.readlines():
                if len(line) == 0:
                    continue
                if line[0] == '#':
                    continue
                fields = line.split(' ')
                if len(fields) != 2:
                    continue
                self.list_victim.append([fields[0], fields[1].rstrip()])

    def run(self):
        while not self.to_stop.is_set():

            self.load_victim_list()

            for name, uid in self.list_victim:

                sleep(self.time_to_sleep)

                # logger.info(f'{name} {uid}')

                try:
                    if self.api_version == 1:
                        ret = binance_leaderboard_getOtherPosition(uid)
                    elif self.api_version == 2:
                        ret = binance_leaderboard_getOtherPosition2(uid)
                    else:
                        ret = binance_leaderboard_getOtherPosition(uid)
                except Exception as e:
                    logger.error(f'binance_leaderboard_getOtherPosition\n{e}')
                    continue

                dict_now_positions = {}
                # print(ret)
                for x in ret['data']['otherPositionRetList']:
                    dict_now_positions[x['symbol']] = x

                path_position_logger = f'{self.dir_positions_logger}/{uid}_{self.api_version}.json'
                if not os.path.isfile(path_position_logger):
                    with open(path_position_logger, 'w+') as fp:
                        json.dump(dict_now_positions, fp)
                    continue

                with open(path_position_logger) as fp:
                    dict_org_positions = json.load(fp)

                # print(dict_org_positions)

                for symbol in dict_now_positions.keys():
                    if symbol not in dict_org_positions.keys():
                        msg = f'{self.api_version} {name} 建立新部位: {symbol}, ' \
                              f'Amount: {dict_now_positions[symbol][w.amount]}, ' \
                              f'Enter price: {dict_now_positions[symbol][w.entryPrice]}, ' \
                              f'Mark price: {dict_now_positions[symbol][w.markPrice]}'
                        if self.line_sender is not None:
                            self.line_sender.send(msg)
                        logger.info(msg)

                for symbol in dict_org_positions.keys():
                    if symbol not in dict_now_positions.keys():
                        msg = f'{self.api_version} {name} 平倉舊部位: {symbol}, ' \
                              f'Amount: {dict_org_positions[symbol][w.amount]}, ' \
                              f'Enter price: {dict_org_positions[symbol][w.entryPrice]}, ' \
                              f'Mark price: {dict_org_positions[symbol][w.markPrice]}'
                        if self.line_sender is not None:
                            self.line_sender.send(msg)
                        logger.info(msg)

                for symbol in dict_now_positions.keys():
                    if symbol not in dict_org_positions.keys():
                        continue
                    if dict_now_positions[symbol][w.amount] != dict_org_positions[symbol][w.amount]:
                        msg = f'{self.api_version} {name} 部位改變: {symbol}, Amount: [{dict_org_positions[symbol][w.amount]}] -> [{dict_now_positions[symbol][w.amount]}]'
                        if self.line_sender is not None:
                            self.line_sender.send(msg)
                        logger.info(msg)

                with open(path_position_logger, 'w+') as fp:
                    json.dump(dict_now_positions, fp)

    def stop(self):
        self.to_stop.set()


if __name__ == '__main__':

    logger.add("binance_copy_bot.log", enqueue=True, rotation="100 MB")
    list_bpm = []
    bpm1 = Binance_position_monitor(api_version=1)
    list_bpm.append(bpm1)
    # bpm2 = Binance_position_monitor(api_version=2)
    # list_bpm.append(bpm2)
    # bpm.line_sender = tLineNotify('9RV6KI0eN0sqI8SlvvGiMTrd7tPYu9qB4m3L2rnQNVl')

    for x in list_bpm:
        x.start()

    index = 0
    while True:
        index += 1
        sleep(1)
        if index > 10000000000:
            for x in list_bpm:
                x.stop()
            break

    for x in list_bpm:
        x.join()
    print('exited....')


