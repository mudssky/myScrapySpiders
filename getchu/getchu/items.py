# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst

class GetchuItem(scrapy.Item):
    getchu_id=scrapy.Field()
    title=scrapy.Field()
    tab_type=scrapy.Field()
    # 因为都是商品，都有价格和含税价格
    price=scrapy.Field()
    price_taxed=scrapy.Field()

    # ===== 下面这些不是每种类别都有，对应的类别继承时设置为None就可以了
    brand=scrapy.Field()
    brand_site=scrapy.Field()
    # メディア 媒体介质，比如dvd，只有非实物类的才有
    midea=scrapy.Field()

    # 発売日 发售日
    on_sale = scrapy.Field()
    # JANコード 商品码
    jan_code=scrapy.Field()

class GetchuItemLoader(ItemLoader):
    default_output_processor = TakeFirst()




class GameItem(GetchuItem):

    # ジャンル  一句话的类别,和category的区别是比较粗的分类、
    genre=scrapy.Field()
    # サブジャンル 子类别
    subgenre_list=scrapy.Field()

    # 品番： 比如HTL-2301
    product_code=scrapy.Field()
    # 原画
    painter_list=scrapy.Field()
    # シナリオ
    scenario_list=scrapy.Field()
    # カテゴリ, 也就是标签
    category_list=scrapy.Field()
    # 商品同梱特典
    specials=scrapy.Field()
    # 封面url
    cover_url=scrapy.Field()
    # 製品仕様／動作環境
    system_requirements=scrapy.Field()
    # 備考
    bikou=scrapy.Field()
    # 根据r18的提示判断是否r18作品
    is_r18=scrapy.Field()
    # ストーリー
    stroy=scrapy.Field()
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

    # 3サイズ
    # height,cup_size,BWH，img_whole

    chara_list=scrapy.Field()
    # 示例图片列表
    sampleimg_list=scrapy.Field()

    # 'duration':duration,
    # 'goods_introduction':goods_introduction,
    # 'content_list':content_list,
    # 'staff_cast':staff_cast,
    # 'ISBN13':ISBN13,
    # 'painter_writer_list':painter_writer_list


class GameItemLoader(GetchuItemLoader):
    pass
class AnimeItem(GetchuItem):
    pass