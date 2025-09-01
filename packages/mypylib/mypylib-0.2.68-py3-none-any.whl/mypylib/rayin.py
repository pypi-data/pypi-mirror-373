
from enum import Enum

class ExCode(Enum):
    整股 = 1
    盤後 = 2
    零股 = 3
    興櫃 = 4
    盤中零股 = 5


# 買賣別
class Side(Enum):
    Buy = 'B'
    Sell = 'S'


# 委託類別
class OrdType(Enum):
    現股 = '0'
    代辦融資 = '1'
    代辦融券 = '2'
    融資 = '3'
    融券 = '4'
    一般借券 = '5'
    避險借券 = '6'
    現股當沖賣出 = 'A'


# 價格旗標
class PriceFlag(Enum):
    限價 = 0
    平盤 = 1
    跌停 = 2
    漲停 = 3
    市價 = 4


# 委託條件
class TimeInForce(Enum):
    FOK = 'F'
    IOC = 'I'
    ROD = 'R'



class w_rayin:
    data_type = 'data_type'
    new_order = 'new_order'
    cancel_order = 'cancel_order'
    cancel_order_by_symbol = 'cancel_order_by_symbol'
    cancel_order_by_symbol_and_user_data = 'cancel_order_by_symbol_and_user_data'
    stock_no = 'stock_no'
    ExCode = 'ExCode'
    Side = 'Side'
    TimeInForce = 'TimeInForce'
    price = 'price'
    qty = 'qty'
    OrdType = 'OrdType'
    PriceFlag = 'PriceFlag'
    UserData = 'UserData'
    order_id = 'order_id'
    order_times = 'order_times'
