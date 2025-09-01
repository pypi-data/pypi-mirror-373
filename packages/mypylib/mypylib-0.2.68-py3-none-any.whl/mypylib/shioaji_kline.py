from collections import defaultdict
import datetime
from typing import Union
import json


class OHLC:
    def __init__(self, timestamp=0, Open=0, High=0, Low=0, Close=0):
        self.timestamp = timestamp
        self.datetime = datetime.datetime.fromtimestamp(self.timestamp)
        self.Open = Open
        self.High = High
        self.Low = Low
        self.Close = Close

    def push(self, close):
        self.Open = close if self.Open == 0 else self.Open
        self.High = close if close > self.High else self.High
        self.Low = close if close < self.Low or self.Low == 0 else self.Low
        self.Close = close


class KLine:

    def __init__(self, symbol, seconds=60):
        self.symbol = symbol
        self.seconds = seconds
        self.list_OHLC = []
        self.OHLC: Union[OHLC, None] = None
        self.ts_end = 0

    # 有的標的tick非常少，有可能會造成中間好幾分鐘沒有kline，
    # 所以需要在別的標的有tick來的時候，就更新 OHLC
    def feed(self):
        if self.ts_end == 0:
            return
        self.ts_end += self.seconds
        self.list_OHLC.append(self.OHLC)
        self.OHLC = OHLC(self.ts_end,
                         self.OHLC.Close,
                         self.OHLC.Close,
                         self.OHLC.Close,
                         self.OHLC.Close)

    def feed_shioaji_quote(self, quote):
        ts_now = datetime.datetime.strptime(f'{quote["Date"]} {quote["Time"]}', '%Y/%m/%d %H:%M:%S.%f').timestamp()

        if self.ts_end == 0:
            self.ts_end = (int(ts_now) // self.seconds + 1) * self.seconds
            self.OHLC = OHLC(self.ts_end)

        if ts_now > self.ts_end and self.OHLC is not None:
            self.feed()

        self.OHLC.push(quote['Close'][0])

    def __getitem__(self, index):
        return self.list_OHLC.__getitem__(index)


if __name__ == '__main__':
    import gzip

    test_file = '../data/2021-09-23_list6.txt.gz'
    test_symbol = '2368'

    kline = KLine(test_symbol, seconds=300)

    with gzip.open(test_file) as fp:
        for line in fp.readlines():
            _, topic, quote = line.decode().split('\t')
            quote = json.loads(quote)

            if topic[-4:] != test_symbol:
                continue
            if topic[0] != 'M':
                continue

            kline.feed_shioaji_quote(quote)

    for OHLC in kline.list_OHLC:
        print(f'{OHLC.datetime} {OHLC.Open} {OHLC.High} {OHLC.Low} {OHLC.Close}')
