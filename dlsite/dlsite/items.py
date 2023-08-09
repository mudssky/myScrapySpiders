# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst
import re
from itemloaders.processors import TakeFirst, MapCompose, Identity, Join
from datetime import datetime


def get_maker_id(maker_url):
    if maker_url:
        result = re.match(r'.*maker_id/(?P<maker_id>.+?)\.html', maker_url)
        return result.group('maker_id')
    return None


def get_price(price_str: str):
    if price_str:
        clean_price = price_str.replace(',', '')
        return float(clean_price)
    return None


def get_cover_url(cover_url: str):
    if cover_url:
        if cover_url.startswith('//'):
            return cover_url[2:]
    return cover_url


def get_on_sale(on_sale_str):
    if on_sale_str:
        time_str = re.match(r'(\d+年\d+月\d+日).*', on_sale_str).group(1)
        if time_str:
            time_res = datetime.strptime(time_str, '%Y年%m月%d日')
            return time_res
    return None


def filter_blank_str(text):
    if text:
        if text.strip() != '':
            return text

    return None


class DlsiteItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # サークル名
    # circle_name=scrapy.Field()
    # cv_list=scrapy.Field()
    # 年齢指定
    # age_judge=scrapy.Field()
    # rjid
    product_id = scrapy.Field()
    # 作品名
    work_name = scrapy.Field()
    # 販売日
    on_sale = scrapy.Field()
    # 年齢指定
    age_judge = scrapy.Field()
    #    サークル名
    circle_name = scrapy.Field()
    # ブランド名
    # brand_name = scrapy.Field()
    maker_id = scrapy.Field()
    # 作品形式
    work_genre = scrapy.Field()

    # シナリオ
    scenario_list = scrapy.Field()
    # イラスト
    illustrator_list = scrapy.Field()
    # 声優
    cv_list = scrapy.Field()
    # ファイル形式	MP3/ wav同梱
    file_type = scrapy.Field()
    # ジャンル
    genre = scrapy.Field()

    # ファイル容量
    file_capcity = scrapy.Field()
    # イベント
    event = scrapy.Field()

    cover_url = scrapy.Field()
    price = scrapy.Field()
    price_without_tax = scrapy.Field()
    # 対応言語
    language_supports = scrapy.Field()
    intro = scrapy.Field()

    other_info = scrapy.Field()

    # 下面是作品相关实时性高的数据
    # 平均打分两位小数
    rate_average_2dp = scrapy.Field()
    # 打分数
    rate_count = scrapy.Field()
    dl_count = scrapy.Field()
    wishlist_count = scrapy.Field()

    updated_at = scrapy.Field()
    review_count = scrapy.Field()
    sample_img_list = scrapy.Field()
    intro_img_list = scrapy.Field()

    # 下面是漫画不一样的
    # 漫画存在作者
    author_list = scrapy.Field()
    page_count = scrapy.Field()

    # 游戏
    # シリーズ名
    series_name = scrapy.Field()

    # 针对翻译作品
    # 原作的id
    translation_id = scrapy.Field()


class DoujinItem(DlsiteItem):
    cv_list = scrapy.Field()


class DlsiteItemLoader(ItemLoader):
    default_output_processor = TakeFirst()
    # maker_id_in = MapCompose(get_maker_id)
    on_sale_in = MapCompose(get_on_sale)
    # creator_out = Identity()
    scenario_list_out = Identity()
    illustrator_list_out = Identity()
    cv_list_out = Identity()
    file_type_out = Identity()
    genre_out = Identity()
    work_genre_out = Identity()
    file_capcity_in = MapCompose(str.strip)
    # price_in = MapCompose(get_price)
    language_supports_out = Identity()
    intro_in = MapCompose(str.strip)
    # intro_in = MapCompose(filter_blank_str)
    intro_out = Join('\n')
    cover_url_in = MapCompose(get_cover_url)
    intro_img_list_in = MapCompose(get_cover_url)
    sample_img_list_in = MapCompose(get_cover_url)
    sample_img_list_out = Identity()
    intro_img_list_out = Identity()
    other_info_out = Identity()

    # 漫画
    author_list_out = Identity()
    page_count_in = MapCompose(str.strip)
