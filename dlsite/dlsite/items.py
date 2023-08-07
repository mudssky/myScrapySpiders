# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst


class DlsiteItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # サークル名
    # circle_name=scrapy.Field()
    # cv_list=scrapy.Field()
    # 年齢指定
    # age_judge=scrapy.Field()
    # rjid
    product_id=scrapy.Field()
    # 販売日
    on_sale = scrapy.Field()
    # 年齢指定
    age_judge = scrapy.Field()
    #    サークル名
    circle_name = scrapy.Field()
    # ブランド名
    brand_name = scrapy.Field()
    maker_id = scrapy.Field()
    # 作品形式
    work_genre = scrapy.Field()

    # ファイル形式	MP3/ wav同梱
    file_type = scrapy.Field()
    # ジャンル
    genre = scrapy.Field()
    # ファイル容量
    file_capcity = scrapy.Field()

    cover_url = scrapy.Field()
    pass


class DoujinItem(DlsiteItem):
    cv_list = scrapy.Field()


class DlsiteItemLoader(ItemLoader):
    # default_output_processor = TakeFirst()
    pass
