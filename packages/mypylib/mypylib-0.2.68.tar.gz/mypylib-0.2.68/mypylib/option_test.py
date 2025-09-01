#
# Yahoo拍賣選擇權小宏的方法四，無風險套利。
#
# 結論：真的可以套利喔！！
# 限制：要實際測試看看滑價情況
#


import datetime
import json

from mypylib import timeIt
import gzip


# Call 1:A 2:B 3:C 4:D 5:E 6:F 7:G 8:H 9:I 10:J 11:K 12:L
# Put  1:M 2:N 3:O 4:P 5:Q 6:R 7:S 8:T 9:U 10:V 11:W 12:X

class w:
    AskPrice = 'AskPrice'
    BidPrice = 'BidPrice'
    Time = 'Time'


class Option_analysis:
    def __init__(self):

        self.CallAskPrice: dict[int, float] = {}
        self.CallBidPrice: dict[int, float] = {}
        self.PutAskPrice: dict[int, float] = {}
        self.PutBidPrice: dict[int, float] = {}

    def read_from_file(self, path_file):

        bool_call = False
        list_ticks = []

        with timeIt('read from file'):
            with gzip.open(path_file) as fp:
                for line in fp.readlines():
                    ts, topic, q = line.decode().split('\t')
                    try:
                        quote = json.loads(q)
                        list_ticks.append((topic, quote))
                    except Exception as e:
                        continue

        with timeIt('test all option ticks'):
            for topic, quote in list_ticks:
                try:
                    price = int(topic[-7:-2])
                    bool_call = True if 'A' <= topic[-2] <= 'L' else False
                    TargetKindPrice = int(quote['TargetKindPrice'] // 25 * 25)
                    if quote.get('Simtrade', None) is not None:
                        continue
                except Exception as e:
                    continue

                if topic[0] != 'Q':
                    continue

                if bool_call:
                    self.CallAskPrice[price] = quote[w.AskPrice][0]
                    self.CallBidPrice[price] = quote[w.BidPrice][0]
                else:
                    self.PutAskPrice[price] = quote[w.AskPrice][0]
                    self.PutBidPrice[price] = quote[w.BidPrice][0]

                # 17, 2 seconds here

                for P1 in range(TargetKindPrice - 500, TargetKindPrice + 500, 50):
                    for P2 in range(P1 + 50, TargetKindPrice + 500 + 50, 50):

                        # 45, 20 seconds here

                        # P1 and P2 都可以在 Call & Put 裡面找到價格
                        if P1 in self.CallAskPrice.keys() and P1 in self.PutAskPrice.keys() and P2 in self.CallAskPrice.keys() and P2 in self.PutAskPrice.keys():

                            # 118 / 108 seconds here

                            delta_base_price = P2 - P1

                            # Sell Call - Buy Call + Sell Put - Buy Put
                            delta_price = self.CallBidPrice[P1] - self.CallAskPrice[P2] + self.PutBidPrice[P2] - self.PutAskPrice[P1]

                            # 376 / 165 seconds here

                            if delta_price > delta_base_price + 2:
                                delta_percentage = (delta_price - delta_base_price) / delta_base_price
                                if delta_percentage > 0.01:
                                    print(f'{quote[w.Time]} P1/P2: {P1}/{P2}, Price/Base price: {delta_price}/{delta_base_price} '
                                          f'{round(10 * (delta_price - delta_base_price) / delta_base_price, 2)}%')

                            # 400 / 177 / 158 seconds here


if __name__ == '__main__':
    oa = Option_analysis()
    oa.read_from_file('../data/TXO-2022-06-10-AM.txt.gz')
    oa.read_from_file('../data/TXO-2022-06-10-PM.txt.gz')
