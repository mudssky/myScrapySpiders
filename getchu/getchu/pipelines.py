# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from datetime import datetime
from itemadapter import ItemAdapter
import pymongo
import scrapy.exceptions as scrapy_exceptions


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
