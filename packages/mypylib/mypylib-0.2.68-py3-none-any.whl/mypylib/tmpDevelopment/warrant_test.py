#
# 從元富的 UDP -> warrant 的 tick 當中針對某個 標的 將股票與權證資料都轉出來
#

import sys
sys.path.append('/Users/chenwei-ting/PycharmProjects/mypylib/mypylib')

import orjson

from mypylib import timeIt
from warrant import read_warrant_bible

str_target = '2368'

dict_warrant_to_info, dict_stock_to_warrant = read_warrant_bible('權證達人寶典_NEWVOL_2022-07-15.xls')

print(dict_stock_to_warrant[str_target])


with timeIt(f'reading {str_target}'):
    with open('code.txt', 'w+') as cfp:
        with open(f'{str_target}.txt', 'w+') as wfp:
            with open('../../stocks/warrant-2022-07-15.txt') as fp:
                for line in fp.readlines():
                    line = line.rstrip()
                    data = orjson.loads(line)
                    code: str = data['code']
                    code = code.rstrip()
                    cfp.write(f'{data["Time"]}\t{code}\n')
                    if code == str_target or code in dict_stock_to_warrant[str_target]:
                        wfp.write(f'{data["Time"]}\t{line}\n')


