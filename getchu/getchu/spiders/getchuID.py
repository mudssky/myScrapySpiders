# ruff: noqa: E741
import re
import scrapy
import getchu.items as getchu_item
from scrapy.exceptions import CloseSpider


class getchuIDSpider(scrapy.Spider):
    name = 'getchuID'
    allowed_domains = ['www.getchu.com']

    def __init__(self, start_id=1, end_id=None, *args, **kwargs):
        # 调用父类的构造函数
        super(getchuIDSpider, self).__init__(*args, **kwargs)

        self.startID = int(start_id)
        if end_id is None:
            self.endID = self.startID + 1
        else:
            self.endID = int(end_id)
        self.logger.debug(f'startID: {start_id} ,endID: {end_id}')
        self.validate_argument()

    def validate_argument(self):
        if self.startID == 1 and self.endID == 1:
            raise CloseSpider('No startID,EndID specified')

    def start_requests(self):
        for id in range(self.startID, self.endID):
            getchu_url = r'https://www.getchu.com/soft.phtml?id=' + str(id) + '&gc=gc'
            metaDict = {"getchu_id": id}
            yield scrapy.Request(getchu_url, callback=self.parse, meta=metaDict)

    def tabTypeParse(self, response):
        tab_link = response.css('.ui-headtabs li.current a::attr(href)').get()
        tab_type_dict = {
            '/pc/': 'game',
            '/anime/': 'anime',
            '/anime/adult.html': 'adult_anime',
            '/music/': 'music',
            '/goods': 'goods',
            '/goods/dakimakura.html': 'dakimakura',
            '/books/': 'books',
            '/doujin/': 'doujin',
            '/doujin/cosplay.html': 'cosplay',
            '/dvdpg/': 'dvdpg',
            '/dl/': 'dl',
            '/goods/adult.html': 'adult_goods',
        }

        # self.logger.debug(f'tab_link:{tab_link} ')
        # self.logger.debug(tab_link in tab_type_dict)
        return tab_type_dict.get(tab_link) or 'unknown'

    def extract_common(self, response, loader=None):
        common_dict = {}
        common_dict['getchu_id'] = response.meta['getchu_id']
        common_dict['title'] = response.css('h1#soft-title::text').get().strip()
        soft_table = response.xpath('//table[@id="soft_table"]')
        price = soft_table.xpath('//td[contains(text(),"定価")]/following-sibling::td/text()').get()
        common_dict['price'] = price
        common_dict['price_taxed'] = price
        common_dict['midea'] = soft_table.xpath('//td[contains(text(),"メディア")]/following-sibling::td/text()').get()
        common_dict['on_sale'] = soft_table.xpath('//td[contains(text(),"発売日")]/following-sibling::td/a/text()').get()
        common_dict['jan_code'] = soft_table.xpath('//td[contains(text(),"JANコード")]/following-sibling::td/text()').get()
        common_dict['is_r18'] = soft_table.xpath('//span[contains(@class,"redb") and contains(text(),"18歳未満の方は購入できません")] = true()').get()

        common_dict['cover_url'] = soft_table.xpath('//tr[1]//a[@class="highslide"]/img/@src').get()
        common_dict['cover_url_hd'] = soft_table.xpath('//tr[1]//a[@class="highslide"]/@href').get()
        common_dict['sample_img_list'] = response.xpath('//div[contains(@class,"tabletitle") and contains(text(),"サンプル画像")]/following-sibling::div[1]//a/@href').getall()

        common_dict['product_code'] = response.xpath('//td[contains(text(),"品番")]/following-sibling::td/text()').get()
        common_dict['tab_type'] = self.tabTypeParse(response)

        common_dict['genre'] = response.xpath('//td[re:test(text(),"^ジャンル")]/following-sibling::td/text()').get()
        common_dict['subgenre_list'] = response.xpath('//td[contains(text(),"サブジャンル")]/following-sibling::td/a/text()').getall()

        common_dict['intro'] = response.xpath('//div[contains(@class,"tabletitle") and contains(text(),"紹介")]/following-sibling::div[1]//text()').getall()
        brand_a = soft_table.xpath('//td[contains(text(),"ブランド")]/following-sibling::td/a')
        if len(brand_a) > 1:
            common_dict['brand'] = brand_a.xpath('./text()').get()
            common_dict['brand_site'] = soft_table.xpath('//td[contains(text(),"ブランド")]/following-sibling::td/a/@href').get()
        else:
            common_dict['brand'] = soft_table.xpath('//td[contains(text(),"ブランド")]/following-sibling::td/text()').get()
            common_dict['brand_site'] = None

        if loader:
            self.load_common_dict(loader=loader, common_dict=common_dict)
        return common_dict

    def load_common_dict(self, loader, common_dict):
        for key in common_dict.keys():
            loader.add_value(key, common_dict[key])

    def parse_name_text(self, nametext):
        res = {}

        name_pattern = r'(?P<name>[^（C]+)?(（(?P<yumi>[^）]+)）)?[^C]*(CV：(?P<cv>[\s\S]+))?'
        matched = re.match(name_pattern, nametext, re.S)
        # print(matched.groupdict())
        if not matched:
            print(nametext)
        res = {
            'yumi': matched.group('yumi'),
            'cv': matched.group('cv'),
            'name': matched.group('name'),
        }
        return res

    def parse_chara_list(self, response, loader=None):
        chara_list = []
        chara_sel_list = response.xpath('//div[contains(@class,"tabletitle") and contains(text(),"キャラクター")]/following-sibling::table[1]//tr[not(descendant::hr)]')
        for node in chara_sel_list:
            chara_dict = {}
            chara_dict['img'] = node.xpath('./td[1]/img/@src').get()
            name_text = node.xpath('./td[2]/dl/dt/h2[contains(@class,"chara-name")]/strong//text()').getall()
            chara_dict['name_text'] = getchu_item.join_and_strip(name_text)
            name_dict = self.parse_name_text(chara_dict['name_text'])
            chara_dict['yumi'] = name_dict['yumi']
            chara_dict['cv'] = name_dict['cv']
            chara_dict['name'] = name_dict['name']
            chara_dict['desp'] = getchu_item.join_and_strip(node.xpath('./td[2]/dl/dd//text()').getall())
            chara_dict['img_whole'] = node.xpath('./td[3]/a/@href').get()
            chara_list.append(chara_dict)
        if loader:
            loader.add_value('chara_list', chara_list)
        return chara_list

    def parse(self, response):
        tab_type = self.tabTypeParse(response)
        # self.logger.debug(f'tab_type:{tab_type} ')

        if tab_type == 'game' or tab_type == 'dvdpg' or tab_type == 'adult_goods':
            l = getchu_item.GameItemLoader(item=getchu_item.GameItem(), response=response)
            #  GetchuItem
            self.extract_common(response=response, loader=l)
            # l.add_value('tab_type', tab_type)
            # l.add_value('getchu_id', common_dict['getchu_id'])
            # l.add_value('title', common_dict['title'])
            # l.add_value('price', common_dict['price'])
            # l.add_value('price_taxed', common_dict['price_taxed'])
            # l.add_value('midea', common_dict['midea'])
            # l.add_value('on_sale', common_dict['on_sale'])
            # l.add_value('jan_code', common_dict['jan_code'])
            soft_table = l.nested_xpath('//table[@id="soft_table"]')
            # soft_table.add_xpath('genre','//td[contains(text(),"ジャンル")]/following-sibling::td/text()')
            # soft_table.add_xpath('subgenre_list','//td[contains(text(),"サブジャンル")]/following-sibling::td/a/text()')
            # soft_table.add_xpath('product_code','//td[contains(text(),"品番")]/following-sibling::td/text()')
            soft_table.add_xpath(
                'painter_list',
                '//td[contains(text(),"原画")]/following-sibling::td/a/text()',
            )
            soft_table.add_xpath(
                'scenario_list',
                '//td[contains(text(),"シナリオ")]/following-sibling::td/a/text()',
            )
            soft_table.add_xpath(
                'musician_list',
                '//td[contains(text(),"音楽")]/following-sibling::td/text()',
            )
            soft_table.add_xpath(
                'category_list',
                '//td[contains(text(),"カテゴリ")]/following-sibling::td/a/text()',
            )
            soft_table.add_xpath(
                'specials',
                '//td[contains(text(),"商品同梱特典")]/following-sibling::td/text()',
            )
            soft_table.add_xpath(
                'bikou',
                '//fieldset//legend[contains(text(),"備考")]/following-sibling::div//span/text()',
            )
            soft_table.add_xpath(
                'system_requirements',
                '//legend[contains(text(),"製品仕様")]/following-sibling::table//text()',
            )

            # soft_table.add_xpath('cover_url_hd','//tr[1]//a[@class="highslide"]/@href')
            # soft_table.add_xpath('cover_url','//tr[1]//a[@class="highslide"]/img/@src')
            l.add_xpath(
                'story',
                '//div[contains(@class,"tabletitle") and contains(text(),"ストーリー")]/following-sibling::div[1]//text()',
            )
            self.parse_chara_list(response=response, loader=l)
            # l.add_xpath("sample_img_list",'//div[contains(@class,"tabletitle") and contains(text(),"サンプル画像")]/following-sibling::div[1]//a/@href')
            return l.load_item()
        elif tab_type == 'anime' or tab_type == 'adult_anime':
            if tab_type == 'anime':
                l = getchu_item.AnimeItemLoader(item=getchu_item.AnimeItem(), response=response)
            else:
                l = getchu_item.AdultAnimeItemLoader(item=getchu_item.AdultAnimeItem(), response=response)
            self.extract_common(response=response, loader=l)
            soft_table = l.nested_xpath('//table[@id="soft_table"]')
            # soft_table.add_xpath('product_code','//td[contains(text(),"品番")]/following-sibling::td/text()')
            # l.add_xpath('intro','//div[contains(@class,"tabletitle") and contains(text(),"商品紹介")]/following-sibling::div[1]//text()')
            l.add_xpath(
                'staff',
                '//div[contains(@class,"tabletitle") and contains(text(),"スタッフ")]/following-sibling::div[1]//text()',
            )
            return l.load_item()
        elif tab_type == 'music' or tab_type == 'goods' or tab_type == 'dakimakura' or tab_type == 'books':
            if tab_type == 'music':
                l = getchu_item.MusicItemLoader(item=getchu_item.MusicItem(), response=response)
            elif tab_type == 'goods':
                l = getchu_item.GoodsItemLoader(item=getchu_item.GoodsItem(), response=response)
            elif tab_type == 'dakimakura':
                l = getchu_item.GoodsItemLoader(item=getchu_item.GoodsItem(), response=response)
            elif tab_type == 'books':
                l = getchu_item.BookItemLoader(item=getchu_item.BookItem(), response=response)
                l.add_xpath(
                    'ISBN_13',
                    '//td[contains(text(),"ISBN-13")]/following-sibling::td/text()',
                )
            self.extract_common(response=response, loader=l)
            return l.load_item()
        elif tab_type == 'doujin' or tab_type == 'cosplay':
            l = getchu_item.DoujinItemLoader(item=getchu_item.DoujinItem(), response=response)
            self.extract_common(response=response, loader=l)
            self.parse_chara_list(response=response, loader=l)
            soft_table = l.nested_xpath('//table[@id="soft_table"]')
            # soft_table.add_xpath('genre','//td[contains(text(),"ジャンル")]/following-sibling::td/text()')
            # soft_table.add_xpath('subgenre_list','//td[contains(text(),"サブジャンル")]/following-sibling::td/a/text()')
            # soft_table.add_xpath('product_code','//td[contains(text(),"品番")]/following-sibling::td/text()')
            soft_table.add_xpath(
                'painter_list',
                '//td[contains(text(),"原画")]/following-sibling::td/a/text()',
            )
            soft_table.add_xpath(
                'scenario_list',
                '//td[contains(text(),"シナリオ")]/following-sibling::td/a/text()',
            )
            soft_table.add_xpath(
                'musician_list',
                '//td[contains(text(),"音楽")]/following-sibling::td/text()',
            )
            soft_table.add_xpath(
                'category_list',
                '//td[contains(text(),"カテゴリ")]/following-sibling::td/a/text()',
            )
            soft_table.add_xpath(
                'bikou',
                '//fieldset//legend[contains(text(),"備考")]/following-sibling::div//span/text()',
            )
            soft_table.add_xpath(
                'system_requirements',
                '//legend[contains(text(),"製品仕様")]/following-sibling::table//text()',
            )
            l.add_xpath(
                'circle',
                '//td[contains(text(),"サークル")]/following-sibling::td[1]/text()',
            )
            return l.load_item()

        elif tab_type == 'unknown':
            l = getchu_item.GetchuItemLoader(item=getchu_item.GetchuItem(), response=response)
            l.add_value('tab_type', tab_type)
            l.add_value('getchu_id', response.meta['getchu_id'])
            return l.load_item()
