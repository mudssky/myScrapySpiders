# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose, Identity, Join
import re


price_pattern = r'￥([\d,]+)[^\d]*\(税込￥([\d,]+)\)'


# '￥9,800 (税込￥10,780)'
def get_price(price_text):
    res = re.match(price_pattern, price_text)
    if res:
        return float(res.group(1).replace(',', ''))
    return None


def get_price_taxed(price_text):
    res = re.match(price_pattern, price_text)
    if res:
        return float(res.group(2).replace(',', ''))
    return None


def filter_subgenre_list(input_list):
    res = list(filter(lambda x: '一覧' not in x, input_list))
    return res


def debug_processor(input):
    print('input', input)
    return input


def join_and_strip(input_list):
    # print('input',input_list)
    return ''.join(input_list).strip()


def is_true(input):
    return input == '1'


class GetchuItem(scrapy.Item):
    getchu_id = scrapy.Field()
    title = scrapy.Field()
    tab_type = scrapy.Field()
    # 因为都是商品，都有价格和含税价格
    price = scrapy.Field()
    price_taxed = scrapy.Field()

    # ===== 下面这些不是每种类别都有，对应的类别继承时设置为None就可以了
    brand = scrapy.Field()
    brand_site = scrapy.Field()
    # メディア 媒体介质，比如dvd，只有非实物类的才有
    midea = scrapy.Field()

    # 発売日 发售日
    on_sale = scrapy.Field()
    # JANコード 商品码
    jan_code = scrapy.Field()

    # 封面url
    cover_url = scrapy.Field()
    cover_url_hd = scrapy.Field()
    # 根据r18的提示判断是否r18作品
    is_r18 = scrapy.Field()

    # 示例图片列表
    sample_img_list = scrapy.Field()

    # 品番： 比如HTL-2301
    product_code = scrapy.Field()

    # 商品紹介
    intro = scrapy.Field()

    # ジャンル  一句话的类别,和category的区别是比较粗的分类、
    genre = scrapy.Field()
    # サブジャンル 子类别
    subgenre_list = scrapy.Field()
    updated_at = scrapy.Field()


class GetchuItemLoader(ItemLoader):
    default_output_processor = TakeFirst()
    price_in = MapCompose(get_price)
    price_taxed_in = MapCompose(get_price_taxed)
    is_r18_in = MapCompose(is_true)
    sample_img_list_out = Identity()
    intro_in = join_and_strip
    # genre_in = debug_processor
    subgenre_list_out = filter_subgenre_list
    brand_in = MapCompose(str.strip)


class GameItem(GetchuItem):
    # 原画
    painter_list = scrapy.Field()
    # シナリオ
    scenario_list = scrapy.Field()
    # 音楽
    musician_list = scrapy.Field()
    # カテゴリ, 也就是标签
    category_list = scrapy.Field()
    # 商品同梱特典
    specials = scrapy.Field()

    # 製品仕様／動作環境
    system_requirements = scrapy.Field()
    # 備考
    bikou = scrapy.Field()

    # ストーリー
    story = scrapy.Field()
    # 角色列表，包含角色名，读音，cv， 角色描述，角色图片，全身图
    # 还包括角色参数，3维，身高，罩杯
    # 其中name_text是未处理的文本。
    # {'name': chara_name,
    #  'yumi': chara_yumi,
    #  'cv': chara_cv,
    #  'name_text': chara_name_text,
    #  'desp': chara_desp,
    #  'img': chara_img,
    #  }

    # img_whole

    chara_list = scrapy.Field()

    # 'duration':duration,
    # 'goods_introduction':goods_introduction,
    # 'content_list':content_list,
    # 'staff_cast':staff_cast,
    # 'ISBN13':ISBN13,
    # 'painter_writer_list':painter_writer_list


class GameItemLoader(GetchuItemLoader):
    painter_list_out = Identity()
    scenario_list_out = Identity()
    category_list_out = filter_subgenre_list
    system_requirements_in = join_and_strip
    story_in = join_and_strip
    # story_in=debug_processor
    # strory_out=Identity()
    musician_list_out = Identity()
    chara_list_out = Identity()


class AnimeItem(GetchuItem):
    # 根据r18的提示判断是否r18作品
    # is_r18=scrapy.Field()
    # intro=scrapy.Field()
    # 品番： 比如HTL-2301
    # product_code=scrapy.Field()
    staff = scrapy.Field()


class AnimeItemLoader(GetchuItemLoader):
    # intro_in=join_and_strip
    staff_in = join_and_strip


class AdultAnimeItem(AnimeItem):
    pass


class AdultAnimeItemLoader(AnimeItemLoader):
    pass


class MusicItem(GetchuItem):
    pass


class MusicItemLoader(GameItemLoader):
    pass


class GoodsItem(GetchuItem):
    pass


class GoodsItemLoader(GetchuItemLoader):
    pass


class BookItem(GetchuItem):
    ISBN_13 = scrapy.Field()


class BookItemLoader(GetchuItemLoader):
    pass


# class DoujinItem(GetchuItem):
#     chara_list=scrapy.Field()
#     circle=scrapy.Field()
#     painter_list=scrapy.Field()
#     scenario_list=scrapy.Field()
#     category_list=scrapy.Field()
#     musician_list=scrapy.Field()
#     bikou=scrapy.Field()
#     system_requirements=scrapy.Field()


class DoujinItem(GameItem):
    circle = scrapy.Field()


class DoujinItemLoader(GameItemLoader):
    circle_in = MapCompose(str.strip)
    # chara_list_out=Identity()
    # painter_list_out=Identity()
    # scenario_list_out=Identity()
    # category_list_out=filter_subgenre_list
    # musician_list_out=Identity()


class CosplayItem(DoujinItem):
    pass


class CosplayItemLoader(DoujinItemLoader):
    pass


class PgItem(GameItem):
    pass


class PgItemLoader(GameItemLoader):
    pass
