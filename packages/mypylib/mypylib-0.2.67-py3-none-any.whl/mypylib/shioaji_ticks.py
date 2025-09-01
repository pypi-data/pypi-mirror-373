from mypylib import parse_date_time
from mypylib.ti import Tick
import datetime


# tick:
# ts:
# ask_volume:
# bid_price:
# ask_price:
# volume:
# bid_volume:
# close
#
# 2021-09-23 09:00:04.599727      MKT/idcdmzpcr01/TSE/2607
#   {"AmountSum": [2260450.0], "Close": [31.0], "Date": "2021/09/23", "TickType": [1], "Time": "09:00:04.664112", "VolSum": [73], "Volume": [22]}
#
# 2021-09-23 09:00:04.670992      QUT/idcdmzpcr01/OTC/8086
#   {"AskPrice": [152.5, 153.0, 153.5, 154.0, 154.5], "AskVolume": [4, 8, 11, 53, 13], "BidPrice": [152.0, 151.5, 151.0, 150.5, 150.0],
#   "BidVolume": [4, 9, 45, 18, 75], "Date": "2021/09/23", "Time": "09:00:04.558015"}


class shioaji_ticks(Tick):
    def __init__(self, quote: dict):    # Not finished
        super().__init__(quote)

        self.bool_simtrade = quote.get('Simtrade', False) == 1
        self.ts: datetime.datetime = parse_date_time(quote['Date'], quote['Time'])
        self.close = quote.get('Close', [0])[0]     # 故意把default寫成 [0]，是因為後面的 quote.get()[0]
        self.volume = quote.get('Volume', [0])[0]
        self.price_ask = quote.get('AskPrice', [0])[0]
        self.price_bid = quote.get('BidPrice', [0])[0]
        self.volume_ask = quote.get('AskVolume', [0])[0]
        self.volume_bid = quote.get('BidVolume', [0])[0]
