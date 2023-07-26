import scrapy
from getchu.items import GameItem, GameItemLoader, GetchuItem
from itemloaders import ItemLoader
from scrapy.exceptions import CloseSpider


class getchuIDSpider(scrapy.Spider):
    name='getchuID'
    allowed_domains = ['www.getchu.com']
    def __init__(self,startID=1,endID=None, *args, **kwargs):
        # 调用父类的构造函数
        super(getchuIDSpider, self).__init__(*args, **kwargs)

        self.startID = int(startID)
        if endID is None:
            self.endID =self.startID+1
        else:
            self.endID= int(endID)
        self.logger.debug(f'startID: {startID} ,endID: {endID}')
        self.validate_argument()

    def validate_argument(self):
        if self.startID==1 and self.endID == 1:
            raise CloseSpider('No startID,EndID specified')

    def start_requests(self):
        for id in range(self.startID,self.endID):
            getchu_url=r'http://www.getchu.com/soft.phtml?id=' + str(id) + '&gc=gc'
            metaDict={
                "getchu_id":id
            }
            yield scrapy.Request(getchu_url,callback=self.parse,meta=metaDict)

    def tabTypeParse(self,response):
        tab_link= response.css('.ui-headtabs li.current a::attr(href)').get()
        tab_type_dict={
            '/pc/':'game',
            '/anime/':'anime',
            '/anime/adult.html':'adult_anime',
            '/music/':'music',
            '/goods':'goods',
            '/goods/dakimakura.html':'dakimakura',
            '/books/':'books',
            '/doujin':'doujin',
            '/doujin/cosplay.html':'cosplay',
            '/dvdpg/':'dvdpg',
            '/dl/':'dl',
            '/goods/adult.html':'adult_goods'
        }

        self.logger.debug(f'tab_link:{tab_link} ')
        self.logger.debug(tab_link in tab_type_dict)
        return tab_type_dict.get(tab_link) or 'unknown'
    def parse(self,response):
        tab_type = self.tabTypeParse(response)
        self.logger.debug(f'tab_type:{tab_type} ')
        if tab_type=='game':
            l=GameItemLoader(item=GameItem(),response=response)
            l.add_value('tab_type',tab_type)
            l.add_value('getchu_id',response.meta['getchu_id'])
            l.add_css('title','h1#soft-title::text')
            return l.load_item()
        elif tab_type == 'unknown':
            l=ItemLoader(item=GetchuItem(),response=response)
            l.add_value('tab_type',tab_type)
            l.add_value('getchu_id',response.meta['getchu_id'])
            return l.load_item()




