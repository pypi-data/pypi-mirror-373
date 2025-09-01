
import datetime
import pandas as pd
import shioaji as sj
from shioaji import contracts
from shioaji.constant import SecurityType, OrderState
from shioaji.contracts import Contract
import os
from time import sleep
import json
from mypylib import get_trade_days
from typing import Union
from collections import defaultdict
from mypylib import parse_date_time
from loguru import logger
from dataclasses import dataclass
import pickle

@dataclass
class Stock:
    code: str = ''
    symbol: str = ''
    name: str = ''
    limit_up: float = 0.0
    limit_down: float = 0.0
    reference: float = 0.0
    day_trade: str = 'No'
    market: str = 'TSE'


# {"AskPrice": [46.9, 46.95, 47.0, 47.2, 47.3],
#  "AskVolume": [3, 1, 5, 9, 12],
#  "BidPrice": [46.75, 46.6, 46.5, 46.45, 46.4],
#  "BidVolume": [1, 24, 16, 11, 33],
#  "Date": "2022/06/07",
#  "Time": "09:01:41.876574"
#  }
class Quote(dict):
    def __init__(self, *args):
        super().__init__(*args)
        self.Ask: Union[dict, None] = None
        self.Bid: Union[dict, None] = None
        self.timestamp = None

    def ts(self) -> datetime :
        if self.timestamp is None:
            # self.timestamp = datetime.datetime.strptime(f'{self.Date()} {self.Time()}', '%Y/%m/%d %H:%M:%S.%f')
            self.timestamp = parse_date_time(self.Date(), self.Time())
        return self.timestamp

    def Simtrade(self) -> int:
        value = super().get('Simtrade')
        return value[0] if isinstance(value, list) else value

    def AskPrice(self) -> list[float]:
        return super().get('AskPrice')

    def AskVolume(self) -> list[int]:
        return super().get('AskVolume')

    def BidPrice(self) -> list[float]:
        return super().get('BidPrice')

    def BidVolume(self) -> list[int]:
        return super().get('BidVolume')

    def Date(self) -> str:
        return super().get('Date')

    def Time(self) -> str:
        return super().get('Time')

    def Pause(self) -> int:
        return super().get('Pause')

    def TradeType(self) -> int:
        return super().get('TradeType')

    def BestBuy(self) -> int:
        return super().get('BestBuy')

    def BestSell(self) -> int:
        return super().get('BestSell')

    # 'AskPrice': [14.4, 14.45, 14.5, 14.55, 14.6], 'AskVolume': [2239, 370, 428, 88, 316]
    # {14.4: 2239, 14.45: 370, 14.5: 428, 14.55: 88, 14.6: 316}
    def zipAsk(self):
        if self.Ask is None:
            self.Ask = defaultdict(int, dict(zip(self.AskPrice(), self.AskVolume())))

    def zipBid(self):
        if self.Bid is None:
            self.Bid = defaultdict(int, dict(zip(self.BidPrice(), self.BidVolume())))


# {"AmountSum": [65246500.0],
#  "Close": [415.5],
#  "Date": "2022/06/07",
#  "TickType": [2],
#  "Time": "09:01:41.845465",
#  "VolSum": [156],
#  "Volume": [3]}
class Market(dict):
    def __init__(self, *args):
        super().__init__(*args)
        self.Ask: Union[dict, None] = None
        self.Bid: Union[dict, None] = None
        self.timestamp = None

    def ts(self) -> datetime:
        if self.timestamp is None:
            # self.timestamp = datetime.datetime.strptime(f'{self.Date()} {self.Time()}', '%Y/%m/%d %H:%M:%S.%f')
            self.timestamp = parse_date_time(self.Date(), self.Time())
        return self.timestamp

    def Simtrade(self) -> int:
        value = super().get('Simtrade')
        return value[0] if isinstance(value, list) else value

    def AmountSum(self) -> int:
        value = super().get('AmountSum')
        return value[0] if isinstance(value, list) else value

    def Close(self) -> float:
        value = super().get('Close')
        return value[0] if isinstance(value, list) else value

    def Date(self) -> str:
        return super().get('Date')

    def TickType(self) -> int:
        value = super().get('TickType')
        return value[0] if isinstance(value, list) else value

    def Time(self) -> str:
        return super().get('Time')

    def VolSum(self) -> int:
        value = super().get('VolSum')
        return value[0] if isinstance(value, list) else value

    def Volume(self) -> int:
        value = super().get('Volume')
        return value[0] if isinstance(value, list) else value

    def Pause(self) -> int:
        return super().get('Pause')

    def TradeType(self) -> int:
        return super().get('TradeType')

    def BestBuy(self) -> int:
        return super().get('BestBuy')

    def BestSell(self) -> int:
        return super().get('BestSell')

    def AskPrice(self) -> list[float]:
        return super().get('AskPrice', None)

    def AskVolume(self) -> list[int]:
        return super().get('AskVolume', None)

    def BidPrice(self) -> list[float]:
        return super().get('BidPrice', None)

    def BidVolume(self) -> list[int]:
        return super().get('BidVolume', None)

    def zipAsk(self):
        if self.Ask is None:
            self.Ask = defaultdict(int, dict(zip(self.AskPrice(), self.AskVolume())))

    def zipBid(self):
        if self.Bid is None:
            self.Bid = defaultdict(int, dict(zip(self.BidPrice(), self.BidVolume())))


class SJ_wrapper:
    def __init__(self,
                 api_key='6Dkp67EVdMQBWE8Z6DZ5zPQAFTbvVPxEGzAEFiZ5ByhN',
                 secret_key='2NCQAhfP73PfKYaAi8xJVHZSp4Y91mSNViiFU7zQ19T2',
                 bool_fake_login=False):

        if bool_fake_login:
            return

        self.api_key = api_key
        self.secret_key = secret_key

        self.bool_IND_fetched = False
        self.bool_FUT_fetched = False
        self.bool_STK_fetched = False
        self.bool_OPT_fetched = False


        logger.info(f'使用正式帳號')
        self.api = sj.Shioaji()
        self.api.login(self.api_key, self.secret_key, contracts_cb=self.contract_cb)

        while True:
            sleep(1)
            if self.bool_OPT_fetched and self.bool_STK_fetched and self.bool_FUT_fetched and self.bool_IND_fetched:
                break

        self.api.set_order_callback(self.order_callback)

    def order_callback(self, stat: OrderState, msg_dict: dict):
        logger.info(f'{stat} {msg_dict}')

    def activate_ca(self, ca_path, ca_passwd, person_id):
        self.api.activate_ca(ca_path=ca_path,
                             ca_passwd=ca_passwd,
                             person_id=person_id,
                             store=1000)

    def contract_cb(self, security_type: SecurityType):
        logger.info(f"{repr(security_type)} fetch done.")
        if security_type == SecurityType.Index:
            self.bool_IND_fetched = True
        elif security_type == SecurityType.Future:
            self.bool_FUT_fetched = True
        elif security_type == SecurityType.Stock:
            self.bool_STK_fetched = True
        elif security_type == SecurityType.Option:
            self.bool_OPT_fetched = True

    def save_all_contracts(self, path_to_save='all_stocks.pickle'):
        dict_all_stocks = {}
        c: Contract
        for c in self.api.Contracts.Stocks.OTC:
            stock = Stock(c.code, c.symbol, c.name, c.limit_up, c.limit_down, c.reference, c.day_trade, "OTC")
            dict_all_stocks[c.code] = stock

        for c in self.api.Contracts.Stocks.TSE:
            stock = Stock(c.code, c.symbol, c.name, c.limit_up, c.limit_down, c.reference, c.day_trade, "TSE")
            dict_all_stocks[c.code] = stock

        rows = path_to_save.split('.')
        c = self.api.Contracts.Stocks['2330']

        with open(path_to_save, 'wb') as fp:
            pickle.dump(dict_all_stocks, fp)

        with open(f'{rows[0]}.txt', 'w') as fp:
            for stock in dict_all_stocks.values():
                fp.write(f'{stock.code}\t{stock.name}\t{stock.limit_up}\t{stock.limit_down}\t{stock.reference}\t{stock.day_trade}\t{stock.market}\n')

        with open(f'{rows[0]}-{c.update_date.replace("/", "")}.{rows[1]}', 'wb') as fp:
            pickle.dump(dict_all_stocks, fp)

        with open(f'{rows[0]}-{c.update_date.replace("/", "")}.txt', 'w') as fp:
            for stock in dict_all_stocks.values():
                fp.write(f'{stock.code}\t{stock.name}\t{stock.limit_up}\t{stock.limit_down}\t{stock.reference}\t{stock.day_trade}\t{stock.market}\n')


    def load_all_contracts(self, path_to_load='all_stocks.pickle'):
        if os.path.exists(path_to_load):
            with open(path_to_load, 'rb') as fp:
                return pickle.load(fp)
        return None



class SJ_downloader(SJ_wrapper):
    def __init__(self, api_key, secret_key):
        super(SJ_downloader, self).__init__(api_key, secret_key)

        self.ticks = None

    def download_ticks(self, contract: contracts, date: Union[str, datetime.datetime]):
        print(contract, date)
        ticks = self.api.ticks(contract=contract, date=date if isinstance(date, str) else datetime.datetime.strftime('%Y-%m-%d'))
        self.ticks = ticks
        return ticks

    def save_ticks(self, filename):
        df = pd.DataFrame({**self.ticks})
        df.ts = pd.to_datetime(df.ts)

        df.to_csv(filename)


def unit_test_SJ_downloader():
    downloader = SJ_downloader(api_key='6Dkp67EVdMQBWE8Z6DZ5zPQAFTbvVPxEGzAEFiZ5ByhN',
                               secret_key='2NCQAhfP73PfKYaAi8xJVHZSp4Y91mSNViiFU7zQ19T2')

    if not os.path.isfile('trade_days.txt'):
        trade_days = get_trade_days('2018-01-01', datetime.datetime.today())
        trade_days.reverse()
        with open('trade_days.txt', 'w+') as fp:
            json.dump(trade_days, fp)
    else:
        with open('trade_days.txt') as fp:
            trade_days = json.load(fp)

    for day in trade_days:
        print(day)
        file = f'days/TXF-{day}.txt'
        if not os.path.isfile(file):
            downloader.download_ticks(contract=downloader.api.Contracts.Futures.TXF.TXFR1, date=day)
            downloader.save_ticks(file)

            sleep(3)

        file = f'days/EXF-{day}.txt'
        if not os.path.isfile(file):
            downloader.download_ticks(contract=downloader.api.Contracts.Futures.EXF.EXFR1, date=day)
            downloader.save_ticks(file)

            sleep(3)

        file = f'days/FXF-{day}.txt'
        if not os.path.isfile(file):
            downloader.download_ticks(contract=downloader.api.Contracts.Futures.FXF.FXFR1, date=day)
            downloader.save_ticks(file)

            sleep(3)


def converter_SJ_ticks_to_MC():
    files = os.listdir('days')
    files.sort()
    print(files)

    with open('EXF_ticks_for_MC.txt', 'w+') as ex:
        with open('FXF_ticks_for_MC.txt', 'w+') as fx:
            with open('TXF_ticks_for_MC.txt', 'w+') as tx:
                fp = None
                for file in files:
                    if file[0:3] == 'EXF':
                        fp = ex
                    if file[0:3] == 'FXF':
                        fp = fx
                    if file[0:3] == 'TXF':
                        fp = tx


if __name__ == '__main__':

    sj = SJ_wrapper()
    sj.save_all_contracts()
    ret = sj.load_all_contracts()
    print(ret)


    if False:
        unit_test_SJ_downloader()

    if False:
        converter_SJ_ticks_to_MC()
