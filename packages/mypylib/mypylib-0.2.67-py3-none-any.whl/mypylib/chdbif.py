


def select_targets(query_string,
                   path_tmp_dir='/tmp',
                   filename_filtered_targets='filtered.csv',
                   date_after=None,
                   server='127.0.0.1',
                   user='default',
                   password='111111',
                   database='STOCK',
                   table='STOCK',
                   selected_items_str=None) -> int:
    from clickhouse_driver import Client

    client = Client(server,
                    user=user,
                    password=password,
                    database=database)

    if date_after is not None and date_after != '':
        query_string += f" and date > '{date_after}' "

    sql_str = f'SELECT count(*) FROM {database}.{table} where {query_string}'
    print(sql_str)
    df = client.query_dataframe(sql_str)

    num_items = df.iloc[0, 0]
    print(f'There are {num_items} items')

    if selected_items_str is None:
        selected_items_str = '`date`, `tick_date`, `stock_id`, ' \
                             '`tick漲停價`, `tick跌停價`, `close`, `open`, ' \
                             '`volume_2percent_30s`, `volume_5percent_30s`, ' \
                             '`volume_2percent`, `volume_5percent`, `mav3`, ' \
                             '`交易日tick_up`, `五日量比`, `ma5`, `三日振幅`, `volume`, ' \
                             '`發行股數`, `tick開`, `空秒數20`, `空22tick數`, `空秒數24`, `空秒數22`, ' \
                             '`交易日漲停價`, `交易日跌停價`, `價1000`, ' \
                             '`價1015`, `價1030`, `價1045`, `價1100`, `價1115`, `價1130`, `價1145`, ' \
                             '`價1200`, `價1215`, `價1230`, `價1245`, `價1300`, `價1315`, `價1330`, `價1345`,' \
                             '`first_tick_ask_price`, `first_tick_bid_price`, `first_tick_ask_volume`, ' \
                             '`first_tick_bid_volume`, `first_tick_close`, `first_tick_volume` '

    """
`date`, `tick_date`, `stock_id`, `tick漲停價`, `tick跌停價`, `close`, `open`, 
`volume_2percent_30s`, `volume_5percent_30s`, `volume_2percent`, `volume_5percent`, 
`mav3`, `交易日tick_up`, `五日量比`, `ma5`, `三日振幅`, `volume`, `發行股數`, `tick開`, 
`空秒數30`, `空22tick數`, `空秒數24`, `空秒數22`, `交易日漲停價`, `交易日跌停價` 
`day_trade_Rank`, `day_trade_Rank`, `day_trade_Rank_negative`, `day_trade_Rank_negative`, 
`tick_up`, `close`, `紅K`, `每筆平均金額`, `五日振幅`, `十日內曾經漲停`, `ma5`, `五日量比`, `open`
    """

    query_string = f'SELECT {selected_items_str} FROM {database}.{table} where {query_string} order by `date`'

    print(query_string)

    df = client.query_dataframe(query_string)

    df.to_csv(f'{path_tmp_dir}/{filename_filtered_targets}')

    return num_items



if __name__ == '__main__':
    query_string = f"""
        ((day_trade_Rank > 0 and day_trade_Rank <= 100) or (day_trade_Rank_negative > 0 and day_trade_Rank_negative <= 50)) and
        tick_up / close < 0.003 and `紅K` = 1 and 
        `每筆平均金額` > 100000 and (`五日振幅` > 15 or `十日內曾經漲停` = 1) and 
        ma5 / close < 0.95 and ma5 / close > 0.85 and 
        `五日量比` < 270 and close > open * 1.01  and volume/1000 > 1000 
        """

    num_items = select_targets(query_string=query_string)

