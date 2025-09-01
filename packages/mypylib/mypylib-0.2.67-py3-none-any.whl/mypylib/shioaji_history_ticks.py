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
class shioaji_history_ticks(Tick):
    def __init__(self, tick_dict: dict):
        super().__init__(tick_dict)
        self.tick_dict = tick_dict
        self.ts: datetime.datetime = tick_dict.get('ts', datetime.datetime(year=2020, month=1, day=1, hour=9, minute=0, second=0))
        self.ask_price = tick_dict.get('ask_price', 0)
        self.bid_price = tick_dict.get('bid_price', 0)
        self.ask_volume = tick_dict.get('ask_volume', 0)
        self.bid_volume = tick_dict.get('bid_volume', 0)
        self.close = tick_dict.get('close', 0)
        self.volume = tick_dict.get('volume', 0)
        self.index = tick_dict.get('index', 0)
