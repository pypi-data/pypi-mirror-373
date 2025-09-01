import pandas as pd
from termcolor import cprint

from mypylib.ti import *

import matplotlib

matplotlib.use('PS')
import matplotlib.pyplot as plt
import gc
import plotly.express as px


class mvp(Base_Technical_Indicator):
    class w:
        stop_trading_already = 'stop trading already'

    def __init__(self, symbol='', date='', period_seconds=10, volume_burst=1000.0, volume_lot=1000.0, volume_moving=1000.0, yesterday_close=0.0, volume_burst_30s=1000.0, volume_lot_30s=1000.0,
                 rule=1):
        cprint(f'MVP: symbol: {symbol}, '
               f'date: {date}, '
               f'period second: {period_seconds}, '
               f'volume burst: {volume_burst}, '
               f'volume burst_30s: {volume_burst_30s}, '
               f'volume lot: {volume_lot}, '
               f'volume moving: {volume_moving}',
               'yellow')

        super().__init__(symbol, date, period_seconds=period_seconds)

        self.symbol = symbol

        self.rule = rule

        # Percentage
        self.percentage_trigger_and_down_tolerance = 0.99

        # MVP index
        self.bool_reach_limit_up = False
        self.bool_has_mvp_data = False
        self.bool_mvp_price_triggered: bool = False
        self.mvp_sell_index = 0
        self.counter_trade_delay = 0
        self.bool_skip_burst = False

        # 不再交易
        self.bool_stop_trading_already = False

        if volume_burst == 0:
            volume_burst = 1000
        if volume_lot == 0:
            volume_lot = 1000

        self.volume_burst = volume_burst
        self.volume_lot = volume_lot
        self.volume_burst_30s = volume_burst_30s
        self.volume_lot_30s = volume_lot_30s
        self.volume_moving = volume_moving
        self.volume_current = 0
        self.volume_previous = 0

        # Limit up minus 2 ticks. Only available for 'PUT'
        self.price_limit_up_stop_lose = 0

        self.price_threshold_trigger = 0
        self.index_price_enter = 0
        self.price_enter = 0
        self.price_open = 0
        self.count_volume_burst = 0
        self.price_yesterday_close = yesterday_close
        self.mvp_index = pd.DataFrame()
        self.mvp_tmp = {'ts': [],
                        'close': [],
                        'volume': []
                        }

    def period_accumulate(self, tick: Tick):
        # print(f'acc: {tick.ts} {tick.close} {tick.volume}')
        super().period_accumulate(tick)

        self.mvp_tmp['ts'].append(tick.datetime)
        self.mvp_tmp['close'].append(tick.close)
        self.mvp_tmp['volume'].append(tick.volume)
        self.volume_current = sum(self.mvp_tmp['volume'])
        if self.price_open == 0:
            self.price_open = tick.close

    def period_calculate(self, tick: Tick):
        # print(f'cal: {tick.ts} {tick.close} {tick.volume}')
        super().period_calculate(tick)

        self.add_mvp_index()

        self.mvp_tmp['ts'].clear()
        self.mvp_tmp['close'].clear()
        self.mvp_tmp['volume'].clear()

    def push(self, tick: Tick):
        if self.bool_stop_trading_already:
            return

        super().push(tick)

    def check_place_cover(self, tick: Tick, price) -> bool:
        index = self.mvp_index.shape[0] - 1
        cur_mvp = self.mvp_index.iloc[index]
        pre1_mvp = self.mvp_index.iloc[index - 1]
        pre2_mvp = self.mvp_index.iloc[index - 3]
        ts = cur_mvp['ts']
        mvp_score = cur_mvp['score']
        pre1_score = pre1_mvp['score']
        pre2_score = pre2_mvp['score']
        mvp_ratio = cur_mvp['mvp_ratio']
        pre1_mvp_ratio = pre1_mvp['mvp_ratio']
        if False and mvp_score < pre1_score and mvp_score < -0.5 and pre1_score < -0.5 and pre2_score < 0:
            # if mvp_score < pre1_score and mvp_ratio < -0.5:
            return True
        price_raise = (price - self.price_yesterday_close) / self.price_yesterday_close
        threshold = 0.089
        ratio = 0.6 - ((price_raise - threshold) * 60)
        if ratio < 0.2:
            ratio = 0.2
        if price_raise >= threshold:
            if self.volume_current + self.volume_previous >= self.volume_lot * ratio:
                return True

        return False

    def check_place_order(self, tick: Tick, price_threshold_trigger) -> bool:
        if self.bool_stop_trading_already:
            # cprint(f'{self.symbol} stop trading already', 'red')
            return False

        self.price_threshold_trigger = price_threshold_trigger
        if not self.bool_reach_limit_up:
            if tick.close >= price_threshold_trigger:
                if not self.bool_mvp_price_triggered:
                    cprint(f'{self.symbol} price triggered at {tick.close}, wait for mvp trigger.', 'red')
                self.bool_mvp_price_triggered = True

            if self.bool_mvp_price_triggered:

                ret = self.check_mvp(bool_put=True)

                if isinstance(ret, str) and ret == self.w.stop_trading_already:
                    self.bool_stop_trading_already = True
                    cprint(f'{self.symbol} stop trading already', 'red')
                    return False

                if ret and tick.close >= price_threshold_trigger * self.percentage_trigger_and_down_tolerance:
                    return True

        return False

    # MVP
    def add_mvp_index(self):

        if len(self.mvp_tmp['ts']) == 0:
            return
        # print(f"{self.burst_volume}, {self.lot_volume}")
        volume = sum(self.mvp_tmp['volume'])
        self.volume_previous = volume
        close = float(self.mvp_tmp['close'][-1])
        high = max(self.mvp_tmp['close'])
        low = min(self.mvp_tmp['close'])
        burst = 0
        lot = 0
        if self.mvp_index.shape[0] == 0:
            close = float(self.mvp_tmp['close'][0])
            ratio = round(100 * ((close / self.price_yesterday_close) - 1), 2)
            if volume > self.volume_burst_30s:
                if close < self.price_yesterday_close:
                    burst = -1
                elif close > self.price_yesterday_close:
                    burst = 1
            self.mvp_index = pd.DataFrame({'ts': [self.mvp_tmp['ts'][0]],
                                           'volume': [volume],
                                           'high': [high],
                                           'low': [low],
                                           'close': [close],
                                           'score': [0],
                                           'ratio': [ratio],
                                           'mvp_ratio': [ratio * 2],
                                           'burst': [burst],
                                           'lot': [lot]})
            return
        previous_close = self.mvp_index.iloc[-1]['close']
        previous_ratio = self.mvp_index.iloc[-1]['ratio']
        score = 0
        volume_burst = self.volume_burst
        volume_lot = self.volume_lot
        if close < previous_close:
            if volume > volume_burst:
                burst = -1
            elif volume > volume_lot:
                lot = -1
            if volume > self.volume_burst:
                score = -9 * (1 + ((volume * previous_close) / (close * self.volume_burst)))
            elif volume > self.volume_lot:
                score = -3 * (1 + ((volume * previous_close) / (close * self.volume_lot)))
            else:
                score = -2 * ((volume * previous_close) / (close * self.volume_lot))
        elif close > previous_close:
            if volume > volume_burst:
                burst = 1
            elif volume > volume_lot:
                lot = 1
            if volume > self.volume_burst:
                score = 9 * (1 + ((volume * close) / (previous_close * self.volume_burst)))
            elif volume > self.volume_lot:
                score = 3 * (1 + ((volume * close) / (previous_close * self.volume_lot)))
            else:
                score = 2 * ((volume * close) / (previous_close * self.volume_lot))
        score = round(score, 3)
        ratio = round((previous_ratio * 0.95) + (score * 0.15), 3)
        mvp_ratio = ratio * 2
        # print(f"{ratio}:ratio, {score}:score")
        df_tmp = pd.DataFrame(
            {'ts': [self.mvp_tmp['ts'][0]], 'volume': [volume], 'high': [high], 'low': [low], 'close': [close], 'score': [score], 'ratio': [ratio], 'mvp_ratio': [mvp_ratio], 'burst': [burst],
             'lot': [lot]})
        self.mvp_index = pd.concat([self.mvp_index, df_tmp], axis=0, ignore_index=True)
        # print(tmp_df)

    def check_mvp(self, bool_put: bool = True):
        index = self.mvp_index.shape[0] - 1
        try:
            if 0 < self.price_limit_up_stop_lose <= self.mvp_index['high'].max():
                return self.w.stop_trading_already
        except:
            print(self.mvp_index)
            exit(0)

        if self.volume_moving / 1000 < 1000:
            cprint(f'{int(self.volume_moving / 1000)} volume low', 'blue')
            # return True
            return self.w.stop_trading_already

        if index < 6:
            return False

        # if False:
        #     volume_burst = self.volume_burst
        #     volume_lot = self.volume_lot
        #     lot_buy = self.mvp_index.loc[self.mvp_index['lot'] == 1].shape[0]
        #     lot_sell = self.mvp_index.loc[self.mvp_index['lot'] == -1].shape[0]
        #     burst_buy = self.mvp_index.loc[self.mvp_index['burst'] == 1].shape[0]
        #     burst_sell = self.mvp_index.loc[self.mvp_index['burst'] == -1].shape[0]
        #     burst_count = self.mvp_index.iloc[2:].loc[self.mvp_index['volume'] >= volume_burst].shape[0]
        #     lot_count = self.mvp_index.loc[self.mvp_index['volume'] >= volume_lot].shape[0]
        #     last_burst_buy = self.mvp_index.iloc[-10:].loc[self.mvp_index['burst'] == 1].shape[0]
        #     last_burst_sell = self.mvp_index.iloc[-10:].loc[self.mvp_index['burst'] == -1].shape[0]
        #     price_min = self.mvp_index['low'].min()
        #     if burst_count > 0 and burst_buy > -1 and burst_sell < 1 and price_min >= self.price_open * 0.99:
        #         self.count_volume_burst = burst_count
        #         self.index_price_enter = index
        #         self.price_enter = self.mvp_index.iloc[index]['close']
        #         return True
        #         if burst_buy > 0 and burst_sell - burst_buy <= 0 and burst_count < 10:
        #             self.index_price_enter = index
        #             self.price_enter = self.mvp_index.iloc[index]['close']
        #             print(f'count:{burst_count} buy:{burst_buy} sell:{burst_sell}')
        #             return True
        #         else:
        #             return self.w.stop_trading_already
        #         if not self.bool_skip_burst:
        #             if burst_sell < burst_buy:
        #                 if last_burst_sell > 0:
        #                     self.bool_skip_burst = True
        #                     return False
        #                 cprint(f'symbol:{self.symbol},count:{burst_count}, buy:{burst_buy}, sell:{burst_sell}, last:{last_burst_buy}, burst:{self.volume_burst_30s}', 'red')
        #                 return self.w.stop_trading_already
        #     else:
        #         return self.w.stop_trading_already

        if bool_put:
            cur_mvp = self.mvp_index.iloc[index]
            pre1_mvp = self.mvp_index.iloc[index - 1]
            pre2_mvp = self.mvp_index.iloc[index - 3]
            pre3_mvp = self.mvp_index.iloc[index - 6]
            ts = cur_mvp['ts']
            mvp_score = cur_mvp['score']
            pre1_score = pre1_mvp['score']
            pre2_score = pre2_mvp['score']
            mvp_ratio = cur_mvp['mvp_ratio']
            pre1_mvp_ratio = pre1_mvp['mvp_ratio']
            pre2_mvp_ratio = pre2_mvp['mvp_ratio']
            pre3_mvp_ratio = pre3_mvp['mvp_ratio']
            close = cur_mvp['close']
            pre1_close = pre1_mvp['close']
            pre2_close = pre2_mvp['close']
            ts = cur_mvp['ts']
            rolling = 9
            price_high_all = self.mvp_index.iloc[:index]['high'].max()
            if index > rolling:
                price_high = self.mvp_index.iloc[:index]['high'].rolling(window=rolling).max().iloc[-1]
                price_low = self.mvp_index.iloc[:index]['low'].rolling(window=rolling).min().iloc[-1]
                mvp_high = self.mvp_index.iloc[:index]['mvp_ratio'].rolling(window=rolling).max().iloc[-1]
                mvp_low = self.mvp_index.iloc[:index]['mvp_ratio'].rolling(window=rolling).min().iloc[-1]
            else:
                if index < 2:
                    price_high = close
                    price_low = close
                    mvp_high = mvp_ratio
                    mvp_low = mvp_ratio
                else:
                    rolling = index - 1
                    price_high = self.mvp_index.iloc[:index]['high'].rolling(window=rolling).max().iloc[-1]
                    price_low = self.mvp_index.iloc[:index]['low'].rolling(window=rolling).min().iloc[-1]
                    mvp_high = self.mvp_index.iloc[:index]['mvp_ratio'].rolling(window=rolling).max().iloc[-1]
                    mvp_low = self.mvp_index.iloc[:index]['mvp_ratio'].rolling(window=rolling).min().iloc[-1]
            if mvp_low == 0:
                mvp_low = 0.0001
            debug = False

            if self.rule == 1:
                if price_high_all == price_high and price_high > self.price_yesterday_close * 1.08 and mvp_high / mvp_low > 1.02:
                    from pathlib import Path
                    self.counter_trade_delay = index + 30
                    return False
                if mvp_ratio < -0.5:
                    self.counter_trade_delay = index + 30
                    if mvp_ratio < -1.5:
                        self.counter_trade_delay = index + 60
                    return False
                if self.counter_trade_delay > index:
                    from pathlib import Path
                    # self.counter_trade_delay -= 1
                    # Path(f'tmp/{self.symbol}-{self.date}').touch()
                    return False
                if pre2_close / close < 0.99 or (mvp_ratio >= pre3_mvp_ratio and mvp_high / mvp_low > 1.02):
                    if debug:
                        print(f"{self.symbol}, ret: False, c:{close * 0.99}, pc2:{pre2_close}, r:{mvp_ratio}, r3:{pre3_mvp_ratio},rh:{mvp_high}, rl:{mvp_low}/{mvp_low * 1.02}")
                        print(self.mvp_index.iloc[index - 5:index]['score'])
                    return False
            else:
                if pre2_close / close < 0.99 or price_high / price_low > 1.02:
                    if debug:
                        print(f"{self.symbol}, s:{mvp_score}, ps1:{pre1_score}, ps2:{pre2_score}, phl:{price_high / price_low}, "
                              f"close:{pre2_close / close}, r:{mvp_ratio}, r1:{pre1_mvp_ratio}, r2:{pre2_mvp_ratio}, "
                              f"rh:{mvp_high}, rl:{mvp_low}/{mvp_low * 1.2}")
                        print(self.mvp_index.iloc[index - 5:index]['score'])
                    return False

            # if  mvp_score < 1 or (pre1_score > mvp_score * 2 and pre2_score > pre1_score):
            # if mvp_score < 3 or pre1_score > mvp_score * 2:
            if -0.1 < mvp_ratio and mvp_ratio < pre1_mvp_ratio < pre2_mvp_ratio and mvp_score < 0:
                if debug:
                    print(
                        f"{self.symbol}, ret:True, s:{mvp_score}, ps1:{pre1_score}, ps2:{pre2_score}, phl:{price_high / price_low}, close:{pre2_close / close},\
                        r:{mvp_ratio}, r1:{pre1_mvp_ratio}, r2:{pre2_mvp_ratio},rh:{mvp_high}, rl:{mvp_low}/{mvp_low * 1.02}")
                    print(self.mvp_index.iloc[index - 5:index]['score'])
                return True
            if -0.1 < mvp_ratio < pre1_mvp_ratio < pre2_mvp_ratio and mvp_score < 0:
                return False

        return False

    def draw(self, symbol, date, filename):
        super(mvp, self).draw(symbol, date, filename)
        folder = '../png/png_test'
        if not os.path.exists(folder):
            os.makedirs(folder)
        # print(self.mvp_index)
        print(f'draw {symbol} {date}')
        # Draw of MVP
        df_ticks_10s = self.mvp_index
        df_ticks_10s['ts'] = pd.to_datetime(df_ticks_10s['ts'])
        df_ticks_10s['volume_ratio'] = (1 + (df_ticks_10s['ratio'] / 100)) * self.price_yesterday_close
        price_enter_time = df_ticks_10s.iloc[self.index_price_enter]['ts']

        index_09_30 = df_ticks_10s.loc[(df_ticks_10s['ts'].dt.second >= 0) & \
                                       (df_ticks_10s['ts'].dt.minute >= 30) & \
                                       (df_ticks_10s['ts'].dt.hour == 9)]
        if index_09_30.shape[0] > 0:
            index_09_30 = index_09_30.index[0]
        else:
            index_09_30 = 0
        index_10_00 = df_ticks_10s.loc[(df_ticks_10s['ts'].dt.second >= 0) & \
                                       (df_ticks_10s['ts'].dt.minute >= 00) & \
                                       (df_ticks_10s['ts'].dt.hour == 10)]
        if index_10_00.shape[0] > 0:
            index_10_00 = index_10_00.index[0]
        else:
            index_10_00 = 0
        index_11_00 = df_ticks_10s.loc[(df_ticks_10s['ts'].dt.second >= 0) & \
                                       (df_ticks_10s['ts'].dt.minute >= 00) & \
                                       (df_ticks_10s['ts'].dt.hour == 11)]
        if index_11_00.shape[0] > 0:
            index_11_00 = index_11_00.index[0]
        else:
            index_11_00 = 0
        index_12_30 = df_ticks_10s.loc[(df_ticks_10s['ts'].dt.second >= 0) & \
                                       (df_ticks_10s['ts'].dt.minute >= 30) & \
                                       (df_ticks_10s['ts'].dt.hour == 12)]
        if index_12_30.shape[0] > 0:
            index_12_30 = index_12_30.index[0]
        else:
            index_12_30 = 0
        index_13_00 = df_ticks_10s.loc[(df_ticks_10s['ts'].dt.second >= 0) & \
                                       (df_ticks_10s['ts'].dt.minute >= 00) & \
                                       (df_ticks_10s['ts'].dt.hour == 13)]
        if index_13_00.shape[0] > 0:
            index_13_00 = index_13_00.index[0]
        else:
            index_13_00 = 0
        if df_ticks_10s.iloc[0]['close'] >= self.price_yesterday_close:
            df_ticks_10s.loc[[0], 'buy_volume'] = df_ticks_10s['volume']
        else:
            df_ticks_10s.loc[[0], 'sell_volume'] = df_ticks_10s['volume']
        df_ticks_10s.loc[(df_ticks_10s['close'] > df_ticks_10s['close'].shift(1)), 'buy_volume'] = df_ticks_10s['volume']
        df_ticks_10s.loc[(df_ticks_10s['close'] < df_ticks_10s['close'].shift(1)), 'sell_volume'] = df_ticks_10s['volume']
        df_ticks_10s.loc[(df_ticks_10s['close'] == df_ticks_10s['close'].shift(1)), 'unknown_volume'] = df_ticks_10s['volume']
        print(f' date:{date} symbol:{symbol} price_enter: {self.price_enter} @ {self.index_price_enter} ')
        # plt.style.use('dark_background')
        plt.style.use('bmh')
        # plt.style.use('ggplot')
        # plt.style.use('classic')
        price_limit_up = self.price_yesterday_close * 1.1
        price_limit_down = self.price_yesterday_close * 0.9
        volume_avg = df_ticks_10s['volume'].mean()
        volume_sum = df_ticks_10s['volume'].sum()
        volume_max = df_ticks_10s['volume'].max()
        volume_limit_up = volume_avg * 50
        if volume_max < volume_limit_up:
            volume_limit_up = volume_max
        df_ticks_10s['ma'] = df_ticks_10s['close'].cumsum() / (df_ticks_10s.index + 1)

        line_width = 2
        alpha = 0.6
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(38, 22))
        ax.set_title(f'{date} {symbol}  vol:{volume_sum} {self.price_enter} {self.volume_burst_30s} {self.count_volume_burst}', fontsize=16)
        ax.plot(df_ticks_10s.index, df_ticks_10s.close, c='red', linewidth=1)
        ax.plot(df_ticks_10s.index, df_ticks_10s.ma, c='blue')
        ax.plot(df_ticks_10s.index, df_ticks_10s.volume_ratio, c='grey', linewidth=1)
        ax.vlines(self.index_price_enter, price_limit_up, price_limit_down, linestyles='dashed', colors="darkred")
        ax.vlines(index_09_30, price_limit_up, price_limit_down, alpha=0.6, linestyles='dashed', colors="grey")
        ax.vlines(index_10_00, price_limit_up, price_limit_down, alpha=0.6, linestyles='dashed', colors="grey")
        ax.vlines(index_11_00, price_limit_up, price_limit_down, alpha=0.6, linestyles='dashed', colors="grey")
        ax.vlines(index_12_30, price_limit_up, price_limit_down, alpha=0.6, linestyles='dashed', colors="grey")
        ax.vlines(index_13_00, price_limit_up, price_limit_down, alpha=0.6, linestyles='dashed', colors="grey")
        ax.hlines(self.price_threshold_trigger, 0, df_ticks_10s.shape[0], linewidth=1, colors="orange")
        ax.hlines(self.price_enter, 0, df_ticks_10s.shape[0], colors="red")
        ax.hlines(self.price_yesterday_close * 1.02, 0, df_ticks_10s.shape[0], linewidth=1.5, alpha=0.6, linestyles='dashed', colors="darkred")
        ax.hlines(self.price_yesterday_close * 1.01, 0, df_ticks_10s.shape[0], linewidth=1.5, alpha=0.3, linestyles='dashed', colors="darkred")
        ax.hlines(self.price_open, 0, df_ticks_10s.shape[0], linewidth=1, linestyles='dashed', colors="green")
        ax.hlines(price_limit_down, 0, df_ticks_10s.shape[0], linewidth=2.5, colors="black")
        ax.hlines(price_limit_up, 0, df_ticks_10s.shape[0], linewidth=2.5, colors="black")
        ax.hlines(self.price_yesterday_close, 0, df_ticks_10s.shape[0], colors="black")
        ax.set_ylim((price_limit_down, price_limit_up * 1.01))
        if self.volume_lot > 0:
            df_ticks_10s.sell_volume = ((1 + (df_ticks_10s.sell_volume / (self.volume_lot_30s * 50))) * price_limit_down)
            df_ticks_10s.buy_volume = ((1 + (df_ticks_10s.buy_volume / (self.volume_lot_30s * 50))) * price_limit_down)
            df_ticks_10s.unknown_volume = ((1 + (df_ticks_10s.unknown_volume / (self.volume_lot_30s * 50))) * price_limit_down)
            ax.bar(df_ticks_10s.index, df_ticks_10s.sell_volume, color='darkblue', alpha=alpha, width=line_width)
            ax.bar(df_ticks_10s.index, df_ticks_10s.buy_volume, color='red', alpha=alpha, width=line_width)
            ax.bar(df_ticks_10s.index, df_ticks_10s.unknown_volume, color='yellow', alpha=alpha, width=line_width)
            ax.hlines((1 + (self.volume_burst / (self.volume_lot * 50))) * price_limit_down, 0, df_ticks_10s.shape[0], alpha=0.6, colors="red")
            ax.hlines(1.02 * price_limit_down, 0, df_ticks_10s.shape[0], alpha=0.6, colors="steelblue")
            ax.hlines(1.01 * price_limit_down, 0, df_ticks_10s.shape[0], linewidth=0.5, linestyles='dashed', colors="steelblue")
        plt.subplots_adjust(left=0.02, bottom=0.02, right=0.97, top=0.97, wspace=0.05, hspace=0.05)
        # plt.show()
        burst_count = self.mvp_index.loc[self.mvp_index['volume'] >= self.volume_burst_30s].shape[0]
        path = f'{folder}/{burst_count}-{symbol}-{date.replace("/", "-")}.png'
        plt.savefig(path)
        print(f'plot in {path}')
        fig.clf()
        plt.close('all')

        gc.collect()
        # print(self.mvp_index)
        # self.mvp_index['volume_ratio'] = (1 + (self.mvp_index['ratio']) / 100) * self.price_yesterday_close
        # fig = px.line(self.mvp_index, x='ts', y=['close', 'volume_ratio'], title=f'{date} {symbol}')
        # fig.show()


if __name__ == '__main__':
    import gzip
    import json
    from shioaji_ticks import shioaji_ticks
    from mypylib import timeIt

    ti: mvp = mvp(period_seconds=10,
                  volume_burst=1092,
                  volume_lot=747.9,
                  volume_moving=29061594,
                  yesterday_close=74)

    with timeIt('test TI'):
        with gzip.open('../data/2021-09-23_list6.txt.gz') as fp:
            for l in fp.readlines():
                ll = l.decode().split('\t')
                topic = ll[1]
                quote = ll[2]
                quote = json.loads(quote)

                tick = shioaji_ticks(quote)

                if topic[:3] == 'MKT' and topic[-4:] == '2368':
                    # print(topic, quote['Time'])
                    ti.push(tick)

        ti.draw('2368', '2021/09/23', '2368.png')
