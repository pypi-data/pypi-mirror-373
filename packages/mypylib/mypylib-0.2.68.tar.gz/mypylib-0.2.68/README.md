
# This is William Chen's private library

# Interfaces
# \_\_init\_\_
* DefaultOrderedDict() 好像沒用
* my_addressable_IP() 抓對外IP
* \_\_LINE\_\_() 顯示哪一行
* get_all_stock_code_name_dict() 用 Shioaji 測試帳號抓所有股票代碼和名稱
* get_day_trade_candidates() 抓可以當沖標的
* get_top_future_trade_volume_list() 抓股票期貨交易量排行
* get_stock_future_snapshot() 抓所有股票期貨的更新資料，開高低收
* get_stock_future_data() 從交易所網站抓所有股票期貨的保證金、級距等等資料
* get_punishment_list() 抓處置股名單
* get_TSE_short_selling_list() 抓上市公司是否可以放空名單
* get_OTC_short_selling_list() 抓上櫃公司是否可以放空名單
* get_short_selling_list() 抓所有公司是否可以放空名單
* mypylib_unit_test() Unit test for 以上函數
* parse_date_time() 把 str_data, str_time 轉成 datetime
* timeIt() 計時
* Ticks 處理 Decimal 版本 
* get_current_price_tick_dec() 目前價格的 tick
* get_ticks_between_dec() 計算兩個價格間的 ticks 數
* price_ticks_offset_dec() ticks offset
* get_limit_up_and_down_price_dec() 平盤價的漲停與跌停
* price_stop_profit_and_lose_dec() 抓漲停與跌停
* date_range() 日期區間 (Iterator)
* short_selling_to_csv() 抓2019年以來能不能放空名單
* get_future_ex() 從日期抓期貨附加代號，例如 M2
* is_end_of_contract_day() 是否是結算日
* load_all_shioaji_ticks() 回傳所有 shioaji ticks的檔案名稱，接下來給 MP 去做事
* build_dealer_downloader() 下載自營商資料（買進、賣出、避險等等)
* get_trade_days() 用 finMind API 傳回哪些是交易日的資料

# finmind
* get_finMind_date_range() 底層 function 
* get_finMind_TX_ticks() 抓 TX tick
* get_finMind_TAIEX_day_KLine() 抓大盤 K 線

# MVP
* Carey的 MVP

# tLineNotify
* tLineNotify() Thread enabled LineNotify

# tplaysound
* tplaysound() Thread enabled playsound

# tredis
* tredis() Thread enabled redis

# warrant
* read_warrant_bible() 讀權證達人寶典的library

# binance_copy_bot
* Binance_position_monitor() 抓幣安 leader boards的部位

# chdbif
* select_targets() 用來從 clickhouse 選要回測資料

# libexcel 早期寫的東西整理在這邊
* parse_date_time() 重複
* date_range() 
* rename_column() 把一些敏感的字元拿掉
* str_to_float()
* trim_price() 這個東西應該用 Decimal ，不應該用 float
* get_day_trade_candidates()
* load_opendays() 抓有交易的日期
* find_last_number_day() 這個應該不能用了
* calculate_call_percentage() 計算做多%數
* convert_to_str()
* load_cell() 處理 excel 相關
* load_value() 處理 excel 相關
* set_cell()
* column_idx()
* conv()
* calculate_percentage()
* get_history()
* build_date_policy()
* build_stock_price()
* build_stock_info()
* build_1mk_from_shioaji()
* build_1mk_profit()
* build_1mk_chart1()
* build_1mk_chart()
* build_1mk_data()
* build_1mk()
* build_simulation()
* build_simulation_total_result()
* build_simulation_result()
* build_days() 
* build_ohlc()
* build_column_ranking_each_day()
* build_dealer_downloader()
* build_ticks_related_info()
* build_dealer_info()
* build_win_rate()
* get_current_price_tick()
* get_limit_up_and_down_price()
* list_fullhistory()

# Interfaces

# sjtools:
## class Quote(dict): Shioaji quote 轉成 class
## class Market(dict): Shioaji tick 轉成 class
#
# class SJ_wrapper:
## Shioaji warrper ，讓 login 比較方便，還需要擴充
#
# class SJ_downloader(SJ_wrapper):
## 專門用來 下載 shioaji ticks 的
#
#
# unit_test_SJ_downloader()
## Unit test for SJ_downloader 
#
#
# converter_SJ_ticks_to_MC()
## 把 SJ ticks 轉成 MultiCharts 可以吃的格式


