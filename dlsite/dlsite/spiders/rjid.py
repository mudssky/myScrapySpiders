import json

import scrapy
from scrapy.exceptions import CloseSpider
from .. import items as dlsite_item
import re


class RjidSpider(scrapy.Spider):
    name = 'rjid'
    allowed_domains = ['www.dlsite.com']

    def __init__(self, start_id=1, end_id=None, *args, **kwargs):
        # 调用父类的构造函数
        super(RjidSpider, self).__init__(*args, **kwargs)

        self.start_id = self.extract_rjid_num(start_id)
        if end_id is None:
            self.end_id = self.start_id + 1
        else:
            self.end_id = self.extract_rjid_num(end_id)

        self.logger.info(f'start_id: {start_id} ,end_id: {end_id}')
        self.validate_argument()
        # 分成两段，6位id时期和8位id时期。
        # RJ001016 RJ441531
        # RJ01000101 - ？

    @staticmethod
    def extract_rjid_num(rjid_str):
        res = re.match(r'(RJ)?(0+)?(?P<rjid_num>\d+)', rjid_str)
        return int(res.group('rjid_num'))

    def get_rjid_str(self, rjid_num: int):
        if rjid_num >= 1 and rjid_num <= 441531:
            return f'RJ{rjid_num:0>6}'
        elif rjid_num >= 1000101:
            return f'RJ{rjid_num:0>8}'
        else:
            return None

    def get_rjid_list(self):
        for num in range(self.start_id, self.end_id):
            rjid_str = self.get_rjid_str(num)
            if rjid_str:
                yield rjid_str

    @staticmethod
    def get_detail_url(rjid_str: str):
        return f'https://www.dlsite.com/maniax/work/=/product_id/{rjid_str}.html/?locale=ja_JP'

    def validate_argument(self):
        if self.start_id == 1 and self.end_id == 1:
            raise CloseSpider('No start_id,end_id specified')

    def start_requests(self):
        for rjid in self.get_rjid_list():
            getchu_url = self.get_detail_url(rjid_str=rjid)
            metaDict = {"product_id": rjid}
            yield scrapy.Request(getchu_url, callback=self.parse, meta=metaDict)

    def parse(self, response):
        l = dlsite_item.DlsiteItemLoader(
            item=dlsite_item.DlsiteItem(), response=response
        )
        # work_right = l.nest('//div[@id="work_right"]')
        # work_right.add_xpath('on_sale','//work_outline')
        l.add_xpath('work_name', '//h1[@id="work_name"]/text()')
        work_right = l.nested_xpath('//div[@id="work_right"]')
        work_right.add_xpath(
            'circle_name', '//span[contains(@class,"maker_name")]/a/text()'
        )
        work_right.add_xpath(
            'maker_id', '//span[contains(@class,"maker_name")]/a/@href'
        )
        # 表格
        work_outline = work_right.nested_xpath('//table[@id="work_outline"]')
        work_outline.add_xpath(
            'on_sale', '//th[contains(text(),"販売日")]/following-sibling::td/a/text()'
        )
        work_outline.add_xpath(
            'scenario_list',
            '//th[contains(text(),"シナリオ")]/following-sibling::td//a/text()',
        )
        work_outline.add_xpath(
            'illustrator_list',
            '//th[contains(text(),"イラスト")]/following-sibling::td//a/text()',
        )
        work_outline.add_xpath(
            'cv_list',
            '//th[contains(text(),"声優")]/following-sibling::td//a/text()',
        )
        work_outline.add_xpath(
            'age_judge',
            '//th[contains(text(),"年齢指定")]/following-sibling::td//a/span/text()',
        )
        work_outline.add_xpath(
            'work_genre',
            '//th[contains(text(),"作品形式")]/following-sibling::td//a/span/text()',
        )
        work_outline.add_xpath(
            'file_type',
            '//th[contains(text(),"ファイル形式")]/following-sibling::td//a/span/text()',
        )
        work_outline.add_xpath(
            'event',
            '//th[contains(text(),"イベント")]/following-sibling::td//a/text()',
        )
        work_outline.add_xpath(
            'genre',
            '//th[contains(text(),"ジャンル")]/following-sibling::td//a/text()',
        )
        work_outline.add_xpath(
            'file_capcity',
            '//th[contains(text(),"ファイル容量")]/following-sibling::td//div/text()',
        )
        work_outline.add_xpath(
            'language_supports',
            '//th[contains(text(),"対応言語")]/following-sibling::td//a/span/text()',
        )
        work_outline.add_xpath(
            'other_info',
            '//th[contains(text(),"その他")]/following-sibling::td//span/text()',
        )

        # 漫画作者
        work_outline.add_xpath(
            'author_list',
            '//th[contains(text(),"作者")]/following-sibling::td//a/text()',
        )
        work_outline.add_xpath(
            'page_count',
            '//th[contains(text(),"ページ数")]/following-sibling::td/text()',
        )
        # 游戏
        work_outline.add_xpath(
            'series_name',
            '//th[contains(text(),"シリーズ名")]/following-sibling::td/a/text()',
        )
        # right = l.nested_xpath('//div[@id="right"]')
        # right.add_xpath(
        #     'price',
        #     '//div[contains(text(),"価格") and contains(@class , "work_buy_label")]/following-sibling::div//span/text()',
        # )

        l.add_xpath(
            'intro',
            '//div[contains(@class,"work_parts_container")]//text()|//div[contains(@class,"work_parts_container")]//img/@src',
        )
        l.add_xpath(
            'cover_url',
            '//div[contains(@class,"work_slider_container")]//li//source/@srcset',
        )
        l.add_value('product_id', response.meta.get('product_id'))
        l.add_xpath(
            'sample_img_list',
            '//div[contains(@class, "product-slider-data")]//div/@data-src',
        )
        l.add_xpath(
            'intro_img_list',
            '//div[contains(@class,"work_parts_container")]//img/@src',
        )
        # return l.load_item()
        meta_data = response.meta.copy()
        meta_data['loader'] = l

        rjid_str = response.meta.get("product_id")
        # 判断是否是翻译页面
        matched = re.match(r'.*(?P<rjid_str>RJ\d+)\.html.*translation.*', response.url)
        if matched:
            self.logger.debug(f'is translation :{response.url}')
            rjid_str = matched.group('rjid_str')
            l.add_value('translation_id', rjid_str)
        yield scrapy.Request(
            f'https://www.dlsite.com/maniax/product/info/ajax?product_id={ rjid_str}&cdn_cache_min=1',
            callback=self.parse_info_json,
            meta=meta_data,
        )

    def parse_info_json(self, response):
        # self.logger.debug("Visited %s", response.url)
        res = response.json().get(response.meta.get('product_id'))
        # print(res, response.meta.get('product_id'), response.meta)
        l = response.meta.get('loader')
        if res:
            l.add_value('price', res.get('price'))
            l.add_value('price_without_tax', res.get('price_without_tax'))
            l.add_value('rate_average_2dp', res.get('rate_average_2dp'))
            l.add_value('rate_count', res.get('rate_count'))
            l.add_value('maker_id', res.get('maker_id'))
            l.add_value('dl_count', res.get('dl_count'))
            l.add_value('wishlist_count', res.get('wishlist_count'))
            l.add_value('review_count', res.get('review_count'))
        return l.load_item()
