from time import sleep

import loguru
from loguru import logger
# HTTP Method: GET(), POST()
import requests as rq
# 導入 BeautifulSoup module: 解析 HTML 語法工具
from bs4 import BeautifulSoup as BS
import requests
import time
import json
import datetime
from lxml import etree
import csv
import urllib3
from loguru import logger

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18362',
}



"""
{'isOutsource': 0,
    'content': '&lt;p&gt;佳世達 (2352-TW) 今 (5) 日公告 6 月營收 189 億元，月增 10%、年減 20%；第二季營收 521 億元，季增 3%、年減 17%；上半年營收 1026 億元，年減 17%。&lt;/p&gt;\n\n&lt;p&gt;佳世達說明，在各項事業表現方面，第二季各項事業幾乎都較第一季增長，其中高附加價值事業的醫療、智慧解決方案也較去年同期成長，醫院營運表現健康。&lt;/p&gt;\n\n&lt;p&gt;展望下半年，佳世達認為，雖然資訊產品不確性仍高，但庫存已回到正常，網通短期則受到庫存去化影響，不過，醫療、智慧解決方案成長動能仍佳，下半年可望優於上半年。&lt;/p&gt;\n\n&lt;p&gt;此外，佳世達集團上月參加的台北國際電腦展 COMPUTEX 業績持續發酵，基三豐旗下華鋒科技看準寵物高齡化趨勢，也將在 7 日登場的台北寵物用品展推出寵物居家照護產品。&lt;/p&gt;\n',
    'hasCoverPhoto': 1,
    'isCategoryHeadline': 1,
    'isIndex': 1,
    'newsId': 5240218,
    'otherProduct': ['TWS:2352:STOCK:COMMON'],
    'payment': 0,
    'source': '',
    'stock': ['2352'],
    'summary': '佳世達 6 月營收 189 億元月增 1 成 Q2 同步回溫',
    'title': '佳世達6月營收189億元月增1成 Q2同步回溫',
    'video': '',
    'publishAt': 1688562762,
    'coverSrc': {'xs': {'src': 'https://cimg.cnyes.cool/prod/news/5240218/xs/7ff96266c21f5fc916eb9e424be0858e.jpg',
      'width': 100,
      'height': 56},
     's': {'src': 'https://cimg.cnyes.cool/prod/news/5240218/s/7ff96266c21f5fc916eb9e424be0858e.jpg',
      'width': 180,
      'height': 101},
     'm': {'src': 'https://cimg.cnyes.cool/prod/news/5240218/m/7ff96266c21f5fc916eb9e424be0858e.jpg',
      'width': 380,
      'height': 214},
     'l': {'src': 'https://cimg.cnyes.cool/prod/news/5240218/l/7ff96266c21f5fc916eb9e424be0858e.jpg',
      'width': 640,
      'height': 360},
     'xl': {'src': 'https://cimg.cnyes.cool/prod/news/5240218/xl/7ff96266c21f5fc916eb9e424be0858e.jpg',
      'width': 960,
      'height': 540},
     'xxl': {'src': 'https://cimg.cnyes.cool/prod/news/5240218/xl/7ff96266c21f5fc916eb9e424be0858e.jpg',
      'width': 960,
      'height': 540}},
    'abTesting': None,
    'categoryId': 827,
    'columnists': None,
    'magazine': None,
    'fundCategoryAbbr': [],
    'fbShare': 0,
    'fbComment': 0,
    'fbCommentPluginCount': 0,
    'market': [{'code': '2352', 'name': '佳世達', 'symbol': 'TWS:2352:STOCK'}],
    'categoryName': '台股新聞'}
"""

class crawler_cnyes:

    list_source = [
        {
            'base_url': 'https://api.cnyes.com',
            'next_page_url': '/media/api/v1/newslist/category/tw_stock?page=1'
        },
        {
            'base_url': 'https://api.cnyes.com',
            'next_page_url': '/media/api/v1/newslist/category/tw_stock_news?page=1'
        },
        {
            'base_url': 'https://news.cnyes.com',
            'next_page_url': '/api/v3/news/category/tw_stock?page=1'
        }

    ]

    def __init__(self, version=1):
        self.list_news = set()
        self.version = version


    @logger.catch
    def fetch(self,
              datetime_start: datetime.datetime = datetime.datetime.today().replace(hour=0, minute=0, second=0),
              datetime_end: datetime.datetime = datetime.datetime.today() + datetime.timedelta(days=1)):

        startAt = int(datetime_start.timestamp())
        endday = int(datetime_end.timestamp())

        list_news = set()

        for source in crawler_cnyes.list_source:
            base_url = source['base_url']
            next_page_url = source['next_page_url']

            while True:
                url = f'{base_url}{next_page_url}&startAt={startAt}&endAt={endday}'
                # print(url)
                res = requests.get(url, headers=headers)
                dict_res = json.loads(res.text)
                last_page = dict_res['items']['last_page']
                next_page_url = dict_res['items']['next_page_url']
                # print(f'總共 {last_page} 頁, Total: {dict_res["items"]["total"]}, from {dict_res["items"]["from"]} - {dict_res["items"]["to"]}')
                for x in dict_res['items']['data']:
                    # print(x)
                    # for key in x:
                    #     print(key)
                    # logger.info(x)
                    title = x['title']
                    # print(title)
                    str_dt = datetime.datetime.fromtimestamp(x['publishAt'])
                    categoryName = x.get('categoryName', '')
                    if categoryName != '台股新聞':
                        continue
                    stock = ' '.join(x.get('stock', ''))

                    # logger.info(f'{str_dt} {title}')
                    list_news.add(f'{str_dt} {title} [{categoryName}] {stock}')

                if next_page_url is None:
                    break

        return list_news


    def fetch_new(self):

        ret: list = self.fetch()

        list_news_new = []

        for x in ret:
            if x not in self.list_news:
                self.list_news.add(x)
                list_news_new.append(x)

        return list_news_new


if __name__ == '__main__':
    from time import sleep

    cynes1 = crawler_cnyes()
    while True:
        news = cynes1.fetch_new()
        if news:
            for x in news:
                print(x)

        sleep(20)

