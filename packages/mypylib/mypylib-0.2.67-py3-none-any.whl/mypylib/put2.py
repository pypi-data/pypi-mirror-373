import traceback
import sys
import pandas as pd
import plotly.graph_objects as go
from docutils.nodes import target
from mypylib import get_ticks_between, get_ticks_between_dec, parse_date_time, price_ticks_offset_dec
from enum import Enum
import json
from datetime import datetime
from mypylib import get_ticks_between, price_ticks_offset, get_ticks_between_dec, parse_date_time
from datetime import timedelta
import os
import finlab
from finlab import data
from finlab.dataframe import FinlabDataFrame
from colorama import init
from dataclasses import dataclass
from loguru import logger


def has_recent_limit_up(close_prices, days=3):
    """檢查最近幾天（不包含當天）是否有漲停。"""
    limit_up = close_prices > close_prices.shift(1) * 1.095
    return limit_up.shift(0).rolling(days).max() == 1


def calculate_turnover_rate():
    """計算股票的週轉率。"""
    try:
        volume = data.get("price:成交股數")
        basic_info = data.get("company_basic_info")
        shares_outstanding = FinlabDataFrame(
            {
                date: basic_info.set_index("stock_id")["已發行普通股數或TDR原發行股數"]
                for date in volume.index
            }
        ).T
        return volume / shares_outstanding
    except Exception as e:
        logger.error(f"計算週轉率時發生錯誤: {e}")
        return None


def has_recent_limit_up(close_prices, days=3):
    """檢查最近幾天（不包含當天）是否有漲停。"""
    limit_up = close_prices > close_prices.shift(1) * 1.095
    return limit_up.shift(0).rolling(days).max() == 1


def calculate_turnover_rate():
    """計算股票的週轉率。"""
    try:
        volume = data.get("price:成交股數")
        basic_info = data.get("company_basic_info")
        shares_outstanding = FinlabDataFrame(
            {
                date: basic_info.set_index("stock_id")["已發行普通股數或TDR原發行股數"]
                for date in volume.index
            }
        ).T
        return volume / shares_outstanding
    except Exception as e:
        logger.error(f"計算週轉率時發生錯誤: {e}")
        return None


def get_dividend_day(close_prices):
    # 除權息不交易日 below
    dividend_announcement = data.get("dividend_announcement")
    df_all_one = pd.DataFrame(1, index=close_prices.index, columns=close_prices.columns)

    for _, row in (dividend_announcement.loc[:, ["stock_id", "除權交易日"]].dropna().iterrows()):
        stock_id = row["stock_id"]
        date = row["除權交易日"].strftime("%Y-%m-%d")

        if date in df_all_one.index and stock_id in df_all_one.columns:
            # print(date, stock_id)
            df_all_one.loc[date, stock_id] = 0

    for _, row in (dividend_announcement.loc[:, ["stock_id", "除息交易日"]].dropna().iterrows()):
        stock_id = row["stock_id"]
        date = row["除息交易日"].strftime("%Y-%m-%d")

        if date in df_all_one.index and stock_id in df_all_one.columns:
            df_all_one.loc[date, stock_id] = 0
    dividend_day_no_trade = df_all_one
    return dividend_day_no_trade
    # 除權息不交易日 above


def put2_select_targets_low_level(threshold_volume=1200 * 1000,
                                  threshold_amount=6500 * 10000,
                                  threshold_max_capital=145e9,
                                  threshold_amp=0.06,
                                  threshold_turn_over=0.003,
                                  threshold_yesterday_co_gt_rate=-0.025,
                                  bool_limit_up_targets=False,
                                  shift=0
                                  ):
    """
    put2 select everyday targets
    :param threshold_volume:
    :param threshold_amount:
    :param threshold_max_capital:
    :param threshold_amp:
    :param threshold_turn_over:
    :param threshold_yesterday_co_gt_rate: open to close rate = (close / open - 1)
    :param shift:
    :return:
    """

    finlab.login("RgK9Hzy5Pg66kc3lbv/mVUHcL6ciJ2QHA7wylySl4VdoUq/EPpXWeHFmu1kqmlC7#vip_m")
    with data.universe("TSE_OTC"):
        capital = data.get('financial_statement:股本')
        close_prices = data.get("price:收盤價")
        open_prices = data.get("price:開盤價")
        high_prices = data.get("price:最高價")
        low_prices = data.get("price:最低價")
        成交金額s = data.get('price:成交金額')
        成交股數s = data.get("price:成交股數")
        融資今日餘額s = data.get('margin_transactions:融資今日餘額')
        融券今日餘額s = data.get('margin_transactions:融券今日餘額')
        當沖s = data.get('intraday_trading:得先賣後買當沖')
        融券使用率s = data.get('margin_transactions:融券使用率')

    券資比s = 融券今日餘額s / 融資今日餘額s
    周轉量s = calculate_turnover_rate()
    # XQ 振幅計算公式 = (當期最高價 - 當期最低價) * 100 / 參考價%
    振幅s = (high_prices - low_prices) / close_prices.shift(1)
    Close_to_closes = round((close_prices / close_prices.shift(1)) - 1, 5)
    # 開盤趴數s = round((open_prices / close_prices.shift(1) - 1), 5)
    # 漲跌幅s = round((close_prices / close_prices.shift(1) - 1), 5)
    # 量比s = round((成交金額s / 成交金額s.shift(1)), 3).shift(1)
    最近漲停s = has_recent_limit_up(close_prices, 1)

    # ma5s = close_prices.average(5)
    # ma10s = close_prices.average(10)
    # ma20s = close_prices.average(20)

    # gt_ma5s = close_prices > ma5s
    # gt_ma10s = close_prices > ma5s
    # gt_ma20s = close_prices > ma5s
    # bool_close_highs = close_prices >= close_prices.shift(1)
    # bool_red_ks = close_prices > open_prices

    targets_volume = 成交股數s > threshold_volume
    targets_amount = 成交金額s > threshold_amount
    targets_amp = 振幅s > threshold_amp
    targets_oc_rate_yesterday = Close_to_closes > threshold_yesterday_co_gt_rate
    targets_turn_over = 周轉量s > threshold_turn_over
    targets_limit_up = 最近漲停s
    targets_day_trade = pd.isna(當沖s) == False
    targets_margin_trading = 融券使用率s > 0.01
    targets_red_k = close_prices > open_prices 

    targets_no_limit_up = 最近漲停s == False

    dividend_day_no_trade = get_dividend_day(close_prices)

    targets = (targets_volume &
               targets_amount &
               targets_turn_over &
               targets_day_trade &
               targets_amp &
               # targets_margin_trading &
               targets_oc_rate_yesterday &
               targets_red_k &
               dividend_day_no_trade
               )
    if not bool_limit_up_targets:
        targets = targets & targets_no_limit_up
        
    filtered_symbols = capital.columns[capital.iloc[-2, :] < threshold_max_capital / 1000]  # 股本在 160 億以下
    
    valid_symbols = filtered_symbols.intersection(targets.columns)
    targets_filtered = targets[valid_symbols]

    # These are the limit up stock of the day
    targets2 = targets_limit_up & targets_volume & targets_amount & targets_margin_trading & targets_day_trade

    targets_to_trade = targets_filtered # | targets2

    return targets_to_trade.shift(shift), close_prices


def _filter_targets(targets_filtered, str_start_date='', str_end_date=''):
    """
    Low level function to filter the data with start date and end date.
    Also convert the dataframe to a list
    :param targets_filtered:
    :param str_start_date:
    :param str_end_date:
    :return:
    """
    # Filter the DataFrame based on start and end dates
    if str_start_date != '':
        targets_filtered = targets_filtered[targets_filtered.index >= str_start_date]
    if str_end_date != '':
        targets_filtered = targets_filtered[targets_filtered.index <= str_end_date]

    # Convert the values with True to a list of [symbol, date]
    result = []
    for date, row in targets_filtered.iterrows():
        true_columns = row[row == True].index.tolist()
        for symbol in true_columns:
            result.append([symbol, date.strftime('%Y-%m-%d')])
    return result


def put2_select_targets_for_tomorrow(threshold_volume=1200 * 1000,
                                     threshold_amount=6500 * 10000,
                                     threshold_max_capital=145e9,
                                     threshold_amp=0.06,
                                     threshold_turn_over=0.003,
                                     threshold_yesterday_co_gt_rate=-0.025,
                                     bool_limit_up_targets=False,
                                     str_start_date='',
                                     str_end_date=''):
    """
    API to select target each day

    :param threshold_volume:
    :param threshold_amount:
    :param threshold_max_capital:
    :param threshold_amp:
    :param threshold_turn_over:
    :param threshold_yesterday_co_gt_rate: open to close rate = (close / open - 1)
    :param str_start_date:
    :param str_end_date:
    :return:
    """
    print(f'threshold_volume: {threshold_volume}')
    print(f'threshold_amount: {threshold_amount}')
    print(f'threshold_max_capital: {threshold_max_capital}')
    print(f'threshold_amp: {threshold_amp}')
    print(f'threshold_turn_over: {threshold_turn_over}')
    print(f'threshold_yesterday_co_gt_rate: {threshold_yesterday_co_gt_rate}')
    print(f'bool_limit_up_targets: {bool_limit_up_targets}')

    targets_to_trade, close_prices = put2_select_targets_low_level(threshold_volume=threshold_volume,
                                                                   threshold_amount=threshold_amount,
                                                                   threshold_max_capital=threshold_max_capital,
                                                                   threshold_amp=threshold_amp,
                                                                   threshold_turn_over=threshold_turn_over,
                                                                   threshold_yesterday_co_gt_rate=threshold_yesterday_co_gt_rate,
                                                                   bool_limit_up_targets=bool_limit_up_targets,
                                                                   shift=0
                                                                   )
    date_of_last_close = close_prices.index[-1].strftime('%Y-%m-%d')
    date_of_last_row = targets_to_trade.index[-1].strftime('%Y-%m-%d')
    if date_of_last_close != date_of_last_row:
        return []
    last_row = targets_to_trade.iloc[-1]
    true_columns = last_row[last_row == True].index.tolist()
    return true_columns


def put2_select_targets(threshold_volume=1200 * 1000,
                        threshold_amount=6500 * 10000,
                        threshold_max_capital=145e9,
                        threshold_amp=0.06,
                        threshold_turn_over=0.003,
                        threshold_yesterday_co_gt_rate=-0.025,
                        bool_limit_up_targets=False,
                        str_start_date='',
                        str_end_date=''):
    """
    API to select target each day

    :param threshold_volume:
    :param threshold_amount:
    :param threshold_max_capital:
    :param threshold_amp:
    :param threshold_turn_over:
    :param threshold_yesterday_co_gt_rate: open to close rate = (close / open - 1)
    :param str_start_date:
    :param str_end_date:
    :return:
    """
    targets_to_trade, close_prices = put2_select_targets_low_level(threshold_volume=threshold_volume,
                                                                   threshold_amount=threshold_amount,
                                                                   threshold_max_capital=threshold_max_capital,
                                                                   threshold_amp=threshold_amp,
                                                                   threshold_turn_over=threshold_turn_over,
                                                                   threshold_yesterday_co_gt_rate=threshold_yesterday_co_gt_rate,
                                                                   bool_limit_up_targets=bool_limit_up_targets,
                                                                   shift=1
                                                                   )
    list_result = _filter_targets(targets_to_trade, str_start_date, str_end_date)
    return list_result


def put1_select_targets_low_level(th_min_stock_price=6,
                                  th_min_amount_money_yesterday=2.5e8,
                                  th_foreign_sell=-29000,
                                  th_min_turnover_rate=0.015,
                                  th_max_capital=160e8, 
                                  condition_category=0
                                  ):
    # Initialize an empty dictionary to store the result
    true_dict = {}
    finlab.login("RgK9Hzy5Pg66kc3lbv/mVUHcL6ciJ2QHA7wylySl4VdoUq/EPpXWeHFmu1kqmlC7#vip_m")
    with data.universe('TSE_OTC'):
        df = FinlabDataFrame()
        price_close = data.get('price:收盤價')
        price_open = data.get('price:開盤價')
        amount_money = data.get('price:成交金額')
        foreign_sell = data.get('institutional_investors_trading_summary:外陸資買賣超股數(不含外資自營商)')
        turnover_rate = calculate_turnover_rate()
        intraday_trading = data.get("intraday_trading:得先賣後買當沖")
        intraday_trading.fillna(0, inplace=True)
        intraday_trading = intraday_trading.reindex(price_close.index)

        capital = data.get('financial_statement:股本')
        # print(f'capital: {capital}')
        filtered_symbols = capital.columns[capital.iloc[-2, :] < th_max_capital / 1000]  # 股本在 160 億以下

        cond1 = price_close.shift(0) > th_min_stock_price
        cond2 = amount_money.shift(0) > th_min_amount_money_yesterday
        cond3 = foreign_sell.shift(0) < th_foreign_sell
        cond4 = turnover_rate.shift(0) > th_min_turnover_rate
        cond5 = price_close.shift(0) >= price_open.shift(0)
        cond6 = intraday_trading > 0

        # dividend_day_no_trade = get_dividend_day(price_close)

        if condition_category == 0:
            targets = cond1 & cond2 & cond3 & cond4 & cond5 & cond6 
        elif condition_category == 1:
            targets = cond1 & cond5 & cond6
        elif condition_category == 2:
            targets = cond1 & cond6

        # print(f'股本160E 以下: {filtered_symbols}')
        valid_symbols = filtered_symbols.intersection(targets.columns)
        targets = targets[valid_symbols]

        # Iterate over the rows and columns of the DataFrame
        for index, row in targets.iterrows():
            # Find all columns (symbols) where the value is True
            true_symbols = [col for col in targets.columns if row[col]]

            # If there are any True values in this row, add them to the dictionary
            if true_symbols:
                true_dict[index.strftime('%Y-%m-%d')] = true_symbols
            else:
                true_dict[index.strftime('%Y-%m-%d')] = []

    last_items = list(true_dict.items())[-3:]
    print(f'true_dict: {last_items}')
    return true_dict


"""
return value:

('2024-12-06', ['1449', '2399', '2405', '2427', '2436', '2453', '2471', '3035', '3265', '3317', 
                '3443', '4510', '4931', '4953', '4991', '5202', '5274', '5284', '6112', '6138', 
                '6214', '6462', '6515', '6669', '6695', '6811', '8032', '8054', '8081', '8249', '8467'])
"""


def put1_select_targets_for_tomorrow(th_min_stock_price=6,
                                     th_min_amount_money_yesterday=2.5e8,
                                     th_foreign_sell=-2900,
                                     th_min_turnover_rate=0.015,
                                     th_max_capital=160e8,
                                     condition_category=0):
    true_dict = put1_select_targets_low_level(th_min_stock_price=th_min_stock_price,
                                              th_min_amount_money_yesterday=th_min_amount_money_yesterday,
                                              th_foreign_sell=th_foreign_sell,
                                              th_min_turnover_rate=th_min_turnover_rate,
                                              th_max_capital=th_max_capital,
                                              condition_category=condition_category)
    return next(reversed(true_dict.items()))


# Not fnished since it's just for backtest
# 2024-11-30
def yang_tomorrow_select_target_low_level(th_times_of_yesterday_volume=4,
                                          th_price_lower_percentage=1.02,
                                          th_price_upper_percentage=1.08
                                          ):
    # Finlab login and data selection
    finlab.login("RgK9Hzy5Pg66kc3lbv/mVUHcL6ciJ2QHA7wylySl4VdoUq/EPpXWeHFmu1kqmlC7#vip_m")
    with data.universe("TSE_OTC"):
        股本s = data.get("financial_statement:股本")
        close_prices = data.get("price:收盤價")
        open_prices = data.get("price:開盤價")
        high_prices = data.get("price:最高價")
        low_prices = data.get("price:最低價")
        成交金額s = data.get("price:成交金額")
        成交股數s = data.get("price:成交股數")
        融資今日餘額s = data.get("margin_transactions:融資今日餘額")
        融券今日餘額s = data.get("margin_transactions:融券今日餘額")
        當沖s = data.get("intraday_trading:得先賣後買當沖")
        當日沖銷交易成交股數s = data.get("intraday_trading:當日沖銷交易成交股數")
        day_trade_amount_buy = data.get("intraday_trading:當日沖銷交易買進成交金額")
        day_trade_amount_sell = data.get("intraday_trading:當日沖銷交易賣出成交金額")
        dividend_announcement = data.get("dividend_announcement")

    ma5s = close_prices.average(5)
    ma10s = close_prices.average(10)
    ma20s = close_prices.average(20)
    ma60s = close_prices.average(60)

    bool_volume_gt_yesterday_2_times = (成交股數s > 成交股數s.shift(1) * th_times_of_yesterday_volume)
    bool_amount_gt_80M = 成交金額s > 8000 * 10000
    bool_above_ma5 = close_prices > ma5s
    bool_above_ma10 = close_prices > ma10s
    bool_above_ma20 = close_prices > ma20s
    bool_above_ma60 = close_prices > ma60s
    bool_price_2_to_8_percentage = ((close_prices > close_prices.shift(1) * th_price_lower_percentage) &
                                    (close_prices < close_prices.shift(1) * th_price_upper_percentage))

    # 除權息不交易日
    df_all_one = pd.DataFrame(1, index=close_prices.index, columns=close_prices.columns)

    for _, row in (dividend_announcement.loc[:, ["stock_id", "除權交易日"]].dropna().iterrows()):
        stock_id = row["stock_id"]
        date = row["除權交易日"].strftime("%Y-%m-%d")

        if date in df_all_one.index and stock_id in df_all_one.columns:
            # print(date, stock_id)
            df_all_one.loc[date, stock_id] = 0

    for _, row in (dividend_announcement.loc[:, ["stock_id", "除息交易日"]].dropna().iterrows()):
        stock_id = row["stock_id"]
        date = row["除息交易日"].strftime("%Y-%m-%d")

        if date in df_all_one.index and stock_id in df_all_one.columns:
            df_all_one.loc[date, stock_id] = 0
    dividend_day_no_trade = df_all_one
    dividend_day_no_trade = dividend_day_no_trade.shift(-1)
    # 除權息不交易日

    targets = (
            bool_volume_gt_yesterday_2_times
            & bool_amount_gt_80M
            & bool_above_ma5
            & bool_above_ma10
            & bool_above_ma20
            & bool_above_ma60
            & dividend_day_no_trade
            & bool_price_2_to_8_percentage
    )

    # Convert targets DataFrame to dictionary
    true_values_dict = {}
    for date, row in targets.iterrows():
        date_str = date.strftime("%Y-%m-%d")
        true_columns = row[row == True].index.tolist()
        if true_columns:
            true_values_dict[date_str] = true_columns

    return true_values_dict



def get_yesterday_closes_from_file(str_file_path, list_symbols):

    dict_ret = {}
    with open(str_file_path, 'r') as fp:
        for line in fp.readlines():
            rows = line.split()
            # print(f'{rows[0]} {rows[4]}')
            if rows[0] in list_symbols:
                dict_ret[rows[0]] = float(rows[4])
    return dict_ret



def get_yesterday_closes(str_date, list_symbols):
    """
    Get yesterday close prices of the symbols
    if the str_date is not a trading day, return the last trading day close prices.
    if the str_date is greater than the last date of the data, return the last date close prices.
    :param str_date:
    :param list_symbols:
    :return:
    """
    finlab.login("RgK9Hzy5Pg66kc3lbv/mVUHcL6ciJ2QHA7wylySl4VdoUq/EPpXWeHFmu1kqmlC7#vip_m")
    with data.universe("TSE_OTC"):
        close_prices = data.get("price:收盤價")
    if str_date in close_prices.index:
        return close_prices.shift(1).loc[str_date, list_symbols].to_dict()
    else:
        last_date = close_prices.index[-1]
        print(last_date)
        print(close_prices.loc[last_date])
        print(list_symbols)
        print(close_prices.loc[last_date, list_symbols])
        return close_prices.loc[last_date, list_symbols].to_dict()


def get_stock_market_TSE_or_OTC_from_file(str_file_path, list_symbols):
    dict_ret = {}
    with open(str_file_path, 'r') as fp:
        for line in fp.readlines():
            rows = line.split()
            if rows[0] in list_symbols:
                dict_ret[rows[0]] = rows[6][0]
    return dict_ret


def get_stock_market_TSE_or_OTC(list_symbols):
    finlab.login("RgK9Hzy5Pg66kc3lbv/mVUHcL6ciJ2QHA7wylySl4VdoUq/EPpXWeHFmu1kqmlC7#vip_m")
    with data.universe("TSE_OTC"):
        # Filter the dataframe to include only the relevant stock_ids
        df = data.get('company_basic_info')
        filtered_df = df[df['stock_id'].isin(list_symbols)]
        # Convert to dictionary mapping stock_id to '市場別'
        stock_market_dict = filtered_df.set_index('stock_id')['市場別'].to_dict()
        return stock_market_dict


def all_stocks_close_on_date(str_date, shift=1, token='RgK9Hzy5Pg66kc3lbv/mVUHcL6ciJ2QHA7wylySl4VdoUq/EPpXWeHFmu1kqmlC7#vip_m'):
    finlab.login(token)
    with data.universe("TSE_OTC"):
        close_prices = data.get("price:收盤價").shift(shift)
    # Extract the row corresponding to 'str_date' as a Series
    row_series = close_prices.loc[str_date]
    
    # Convert that Series to a dictionary
    # If you want to exclude NaN values, you can do `row_series.dropna().to_dict()`
    return row_series.to_dict()


def get_TaiwanStockPrice(path_dest='latest_stock_data.csv'):
    import finlab
    from finlab import data
    from finlab.dataframe import FinlabDataFrame
    import pandas as pd

    # Login to finlab (use your provided API key)
    finlab.login("RgK9Hzy5Pg66kc3lbv/mVUHcL6ciJ2QHA7wylySl4VdoUq/EPpXWeHFmu1kqmlC7#vip_m")

    # Set the universe to TSE_OTC and fetch the data
    with data.universe("TSE_OTC"):
        close_prices = data.get("price:收盤價")
        open_prices = data.get("price:開盤價")
        high_prices = data.get("price:最高價")
        low_prices = data.get("price:最低價")
        amount_tradeds = data.get("price:成交股數")  # This is volume in shares
        volume_tradeds = data.get("price:成交金額")  # This is amount in currency

    # Get the latest date (last index in the DataFrames)
    latest_date = close_prices.index[-1].strftime('%Y-%m-%d')

    # Get the list of stock symbols (common columns across DataFrames)
    symbols = close_prices.columns.intersection(open_prices.columns).intersection(high_prices.columns).intersection(low_prices.columns).intersection(amount_tradeds.columns).intersection(volume_tradeds.columns)

    # Collect rows for CSV
    rows = ["date,stock_id,open,close,high,low,volume,amount"]
    for symbol in symbols:
        try:
            open_price = open_prices.loc[latest_date, symbol] if pd.notna(open_prices.loc[latest_date, symbol]) else ""
            high_price = high_prices.loc[latest_date, symbol] if pd.notna(high_prices.loc[latest_date, symbol]) else ""
            low_price = low_prices.loc[latest_date, symbol] if pd.notna(low_prices.loc[latest_date, symbol]) else ""
            close_price = close_prices.loc[latest_date, symbol] if pd.notna(close_prices.loc[latest_date, symbol]) else ""
            volume = amount_tradeds.loc[latest_date, symbol] if pd.notna(amount_tradeds.loc[latest_date, symbol]) else ""  # Shares
            amount = volume_tradeds.loc[latest_date, symbol] if pd.notna(volume_tradeds.loc[latest_date, symbol]) else ""  # Currency
            rows.append(f"{latest_date},{symbol},{open_price},{close_price},{high_price},{low_price},{volume},{amount}")
        except KeyError:
            # Skip if symbol or date not found in all DataFrames
            continue

    # Write to CSV file
    with open(path_dest, "w") as f:
        f.write("\n".join(rows))

    print(f"CSV file '{path_dest}' has been created successfully.")


if __name__ == '__main__':

    if False:
        list_targets_to_trade = ['2330', '2317', '2337']
        print('\n\n\nget_yesterday_closes_from_file')
        dict_closes = get_yesterday_closes_from_file(f'/home/william/daily_stock_data/all_stocks.txt', list_targets_to_trade)
        print(dict_closes)


    if False:
        str_start_date = '2024-01-01'
        str_end_date = ''
        files_list = put2_select_targets(threshold_volume=3000 * 1000,
                                    threshold_amount=10000 * 10000,
                                    threshold_max_capital=145e8,  # Dummy nod
                                    threshold_amp=0.03,
                                    threshold_turn_over=0.05,
                                    threshold_yesterday_co_gt_rate=0.025,
                                    bool_limit_up_targets=False,
                                    str_start_date=str_start_date,
                                    str_end_date=str_end_date)
        for symbol, str_date in files_list:
            print(f'{str_date} {symbol}')

        total = len(files_list)
        print(f'總共 {total} 標地')

    if False:
        print(f'\033[1;33mThis is to get yesterday close of 2330, 2317, 2337 in 2024-11-12\033[0m')
        dict_closes = get_yesterday_closes('2024-11-12', ['2330', '2317', '2337'])
        print(f'\n\n\nYesterday close of 2024-11-12: {dict_closes}')

        print(f'\033[1;33mThis is to get yesterday close of 2330, 2317, 2337 in 2024-11-17\033[0m')
        dict_closes = get_yesterday_closes('2024-11-17', ['2330', '2317', '2337'])
        print(f'\n\n\nYesterday close of 2024-11-17: {dict_closes}')

        ### list_targets_to_trade = put2_select_targets_for_tomorrow(threshold_volume=1200 * 1000,
        ###                                                          threshold_amount=6500 * 10000,
        ###                                                          threshold_max_capital=145e8,
        ###                                                          threshold_amp=0.06,
        ###                                                          threshold_turn_over=0.003,
        ###                                                          threshold_yesterday_co_gt_rate=-0.025,
        ###                                                          str_start_date='2024-01-01',
        ###                                                          str_end_date='')

        print(f'\033[1;33m]This is to test put2_select_targets_for_tomorrow()\033[0m')
        list_targets_to_trade = put2_select_targets_for_tomorrow(
                                                                 threshold_volume=1200 * 1000,
                                                                 threshold_amount=6500 * 10000,
                                                                 threshold_max_capital=145e9,
                                                                 threshold_amp=0.03,
                                                                 threshold_turn_over=0.05,
                                                                 threshold_yesterday_co_gt_rate=0.025,
                                                                 bool_limit_up_targets=False
                                                                    )
        print('\n\n\nPUT2 targets')
        print(list_targets_to_trade)

        print('\n\n\nget_yesterday_closes')
        dict_closes = get_yesterday_closes(datetime.today().strftime('%Y-%m-%d'), list_targets_to_trade)
        print(dict_closes)
        with open(f'/home/william/daily_stock_data/put2_targets-{str(datetime.today().date())}.txt', 'w') as fp:
            fp.write(' '.join(list_targets_to_trade))
        with open('/home/william/daily_stock_data/put2_targets.txt', 'w') as fp:
            fp.write(' '.join(list_targets_to_trade))

        print('\n\n\nget_yesterday_closes_from_file')
        dict_closes = get_yesterday_closes_from_file(f'/home/william/daily_stock_data/all_stocks.txt', list_targets_to_trade)
        print(dict_closes)



    if False:
        print(f'\033[1;33mThis is to test put1_select_targets_for_tomorrow()\033[0m')
        tuple_date_list_symbols = put1_select_targets_for_tomorrow(th_min_stock_price=6,
                                                                   th_min_amount_money_yesterday=2.5e8,
                                                                   th_foreign_sell=-2900,
                                                                   th_min_turnover_rate=0.015,
                                                                   th_max_capital=160e8,
                                                                   condition_category=0)
        # print('\n\n\nPUT1 targets')
        # list_symbols = tuple_date_list_symbols[1]
        # dict_closes = get_yesterday_closes(None, list_symbols)
        # print(dict_closes)

    # ret = yang_tomorrow_select_target_low_level()
    # print('Yang tomorrow')
    # print(ret)

    if True:
        get_TaiwanStockPrice()