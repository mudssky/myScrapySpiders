import json

import scrapy
from scrapy.exceptions import CloseSpider
from .. import items as dlsite_item
from scrapy.utils.request import  fingerprint

class RjidSpider(scrapy.Spider):
    name = 'rjid'
    allowed_domains = ['www.dlsite.com']

    def __init__(self, start_id=1, end_id=None, *args, **kwargs):
        # 调用父类的构造函数
        super(RjidSpider, self).__init__(*args, **kwargs)

        self.start_id = int(start_id)
        if end_id is None:
            self.end_id = self.start_id + 1
        else:
            self.end_id = int(end_id)

        self.logger.debug(f'start_id: {start_id} ,end_id: {end_id}')
        self.validate_argument()
        # 分成两段，6位id时期和8位id时期。
        # RJ001016 RJ441531
        # RJ01000101 - ？

    def get_rjid_list(self):
        for num in range(self.start_id, self.end_id):
            if num >= 1 and num <= 441531:
                num_str = f'RJ{num:0>6}'
                yield num_str
            elif num >= 1000101:
                num_str = f'RJ{num:0>8}'
                yield num_str

    def validate_argument(self):
        if self.start_id == 1 and self.end_id == 1:
            raise CloseSpider('No start_id,end_id specified')

    def start_requests(self):
        for rjid in self.get_rjid_list():
            getchu_url = f'https://www.dlsite.com/maniax/work/=/product_id/{rjid}.html'
            metaDict = {"product_id": rjid}
            yield scrapy.Request(getchu_url, callback=self.parse, meta=metaDict)

    def parse(self, response):
        l = dlsite_item.ItemLoader(item=dlsite_item.DlsiteItem(), response=response)
        work_right = l.nest('//div[@id="work_right"]')
        work_right.add_xpath('on_sale','//work_outline')
        json.dumps()
        l.add_value('product_id',response.meta.get('product_id'))
        pass
