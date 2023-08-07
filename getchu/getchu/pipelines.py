# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from datetime import datetime
from itemadapter import ItemAdapter
import pymongo
import scrapy.exceptions as scrapy_exceptions
import scrapy
from scrapy.pipelines.images import ImagesPipeline
from urllib.parse import urljoin


class GetchuPipeline:
    def process_item(self, item, spider):
        return item


class MongoUpsertPipeline:
    mongo_collection_name = "items"

    def __init__(self, mongo_uri, mongo_db, mongo_collection_name):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.mongo_collection_name = mongo_collection_name

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get("MONGO_URI"),
            mongo_db=crawler.settings.get("MONGO_DATABASE"),
            mongo_collection_name=crawler.settings.get("MONGO_COLLECTION_NAME"),
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        itemAd = ItemAdapter(item)
        itemAd['updated_at'] = datetime.now()
        if not itemAd.get('getchu_id'):
            raise scrapy_exceptions.CloseSpider('insert db error,not getchu_id provide')
        self.db[self.mongo_collection_name].update_one(
            {'getchu_id': itemAd.get('getchu_id')},
            {'$set': itemAd.asdict()},
            upsert=True,
        )
        # self.db[self.collection_name].insert_one(ItemAdapter(item).asdict(),)
        return item


class MyImagesPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        # print('enter image pipeline')
        adapter = ItemAdapter(item)
        # 只下载game分类
        if adapter.get('tab_type') == 'game':
            url_list = []
            cover_url = adapter.get('cover_url')
            if cover_url:
                url_list.append(cover_url)
            cover_url_hd = adapter.get('cover_url_hd')
            if cover_url_hd:
                url_list.append(cover_url_hd)
            # 样品图片
            sample_img_list = adapter.get('sample_img_list')
            if sample_img_list:
                url_list += sample_img_list
            # 角色图片
            chara_list = adapter.get('chara_list')
            if chara_list:
                for chara in chara_list:
                    img = chara['img']
                    img_whole = chara['img_whole']
                    if img:
                        url_list += [img]
                    if img_whole:
                        url_list += [img_whole]
            # print(f'urllist:{url_list}')
            for url in url_list:
                yield scrapy.Request(
                    urljoin('https://www.getchu.com', url),
                    headers={
                        'referer': f'https://www.getchu.com/soft.phtml?id={adapter.get("getchu_id")}'
                    },
                    meta={'cache_ignore': True},
                )

    def file_path(self, request, response=None, info=None, *, item=None):
        getchu_id = item['getchu_id']
        origin_filename = request.url.split('/')[-1]
        return f'{getchu_id}/{origin_filename}'

    def item_completed(self, results, item, info):
        image_paths = [x["path"] for ok, x in results if ok]
        if not image_paths:
            raise scrapy_exceptions.DropItem("Item contains no images")
        return item
