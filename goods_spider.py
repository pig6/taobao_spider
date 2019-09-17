import os
import re
import json
import time
import random

import requests
import pandas as pd
from retrying import retry

from taobao_login import TaoBaoLogin

"""
获取详细教程、获取代码帮助、提出意见建议
关注微信公众号「裸睡的猪」与猪哥联系

@Author  :   猪哥,
"""

# 关闭警告
requests.packages.urllib3.disable_warnings()
# 登录与爬取需使用同一个Session对象
req_session = requests.Session()
# 淘宝商品excel文件保存路径
GOODS_EXCEL_PATH = 'taobao_goods.xlsx'


class GoodsSpider:

    def __init__(self, q):
        self.q = q
        # 超时
        self.timeout = 15
        self.goods_list = []
        # 淘宝登录
        tbl = TaoBaoLogin(req_session)
        tbl.login()

    @retry(stop_max_attempt_number=3)
    def spider_goods(self, page):
        """

        :param page: 淘宝分页参数
        :return:
        """
        s = page * 44
        # 搜索链接，q参数表示搜索关键字，s=page*44 数据开始索引
        search_url = f'https://s.taobao.com/search?initiative_id=tbindexz_20170306&ie=utf8&spm=a21bo.2017.201856-taobao-item.2&sourceId=tb.index&search_type=item&ssid=s5-e&commend=all&imgfile=&q={self.q}&suggest=history_1&_input_charset=utf-8&wq=biyunt&suggest_query=biyunt&source=suggest&bcoffset=4&p4ppushleft=%2C48&s={s}&data-key=s&data-value={s + 44}'

        # 代理ip，网上搜一个，猪哥使用的是 站大爷：http://ip.zdaye.com/dayProxy.html
        # 尽量使用最新的，可能某些ip不能使用，多试几个。后期可以考虑做一个ip池
        # 爬取淘宝ip要求很高，西刺代理免费ip基本都不能用，如果不能爬取就更换代理ip
        proxies = {'http': '118.24.172.149:1080',
                   'https': '60.205.202.3:3128'
                   }
        # 请求头
        headers = {
            'referer': 'https://www.taobao.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }
        response = req_session.get(search_url, headers=headers, proxies=proxies,
                                   verify=False, timeout=self.timeout)
        # print(response.text)
        goods_match = re.search(r'g_page_config = (.*?)}};', response.text)
        # 没有匹配到数据
        if not goods_match:
            print('提取页面中的数据失败！')
            print(response.text)
            raise RuntimeError
        goods_str = goods_match.group(1) + '}}'
        goods_list = self._get_goods_info(goods_str)
        self._save_excel(goods_list)
        # print(goods_str)

    def _get_goods_info(self, goods_str):
        """
        解析json数据，并提取标题、价格、商家地址、销量、评价地址
        :param goods_str: string格式数据
        :return:
        """
        goods_json = json.loads(goods_str)
        goods_items = goods_json['mods']['itemlist']['data']['auctions']
        goods_list = []
        for goods_item in goods_items:
            goods = {'title': goods_item['raw_title'],
                     'price': goods_item['view_price'],
                     'location': goods_item['item_loc'],
                     'sales': goods_item['view_sales'],
                     'comment_url': goods_item['comment_url']}
            goods_list.append(goods)
        return goods_list

    def _save_excel(self, goods_list):
        """
        将json数据生成excel文件
        :param goods_list: 商品数据
        :param startrow: 数据写入开始行
        :return:
        """
        # pandas没有对excel没有追加模式，只能先读后写
        if os.path.exists(GOODS_EXCEL_PATH):
            df = pd.read_excel(GOODS_EXCEL_PATH)
            df = df.append(goods_list)
        else:
            df = pd.DataFrame(goods_list)

        writer = pd.ExcelWriter(GOODS_EXCEL_PATH)
        # columns参数用于指定生成的excel中列的顺序
        df.to_excel(excel_writer=writer, columns=['title', 'price', 'location', 'sales', 'comment_url'], index=False,
                    encoding='utf-8', sheet_name='Sheet')
        writer.save()
        writer.close()

    def patch_spider_goods(self):
        """
        批量爬取淘宝商品
        如果爬取20多页不能爬，可以分段爬取
        :return:
        """
        # 写入数据前先清空之前的数据
        if os.path.exists(GOODS_EXCEL_PATH):
            os.remove(GOODS_EXCEL_PATH)
        # 批量爬取，自己尝试时建议先爬取3页试试
        for i in range(0, 100):
            print('第%d页' % (i + 1))
            self.spider_goods(i)
            # 设置一个时间间隔
            time.sleep(random.randint(10, 15))


if __name__ == '__main__':
    gs = GoodsSpider('避孕套')
    gs.patch_spider_goods()
