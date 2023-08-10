# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from datetime import datetime
from itemadapter import ItemAdapter
import pymongo
import scrapy.exceptions as scrapy_exceptions
from scrapy.pipelines.images import ImagesPipeline
import scrapy
from . import utils


class DlsitePipeline:
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
        if not itemAd.get('product_id'):
            raise scrapy_exceptions.CloseSpider('insert db error,no product_id provide')
        self.db[self.mongo_collection_name].update_one(
            {'product_id': itemAd.get('product_id')},
            {'$set': itemAd.asdict()},
            upsert=True,
        )
        # self.db[self.collection_name].insert_one(ItemAdapter(item).asdict(),)
        return item


class MyImagesPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        adapter = ItemAdapter(item)
        url_list = []
        # 只保存包含声优的日语项目的全部图片，其他项目只保存封面图
        if adapter.get('cv_list') and (not adapter.get('translation_id')):
            if adapter.get('sample_img_list'):
                url_list += adapter.get('sample_img_list')
            if adapter.get('intro_img_list'):
                url_list += adapter.get('intro_img_list')
        else:
            if adapter.get('cover_url'):
                url_list.append(adapter.get('cover_url'))
        for url in url_list:
            yield scrapy.Request(
                f'https://{url}',
                headers={
                    'referer': info.spider.get_detail_url(adapter.get('product_id')),
                },
                meta={
                    'dont_cache': True,
                },
            )

    def file_path(self, request, response=None, info=None, *, item=None):
        product_id = item['product_id']
        origin_filename = request.url.split('/')[-1]
        # 目录按照时间来分类
        on_sale = item['on_sale']
        # ext_name = request.url.split('.')[-1]
        #  按照年/月/id的文件夹形式归档
        datepath = on_sale.strftime(r'%Y/%m')
        return f'{datepath}/{product_id}/{origin_filename}'

    def item_completed(self, results, item, info):
        # image_paths = [x["path"] for ok, x in results if ok]
        # if not image_paths:
        #     raise scrapy_exceptions.DropItem("Item contains no images")
        return item
