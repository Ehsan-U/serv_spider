# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from motor.motor_asyncio import AsyncIOMotorClient
from hashlib import md5


class MongoPipeline:
    collection_name = "pages"


    def __init__(self, mongo_uri: str, mongo_db: str) -> None:
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db


    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get("MONGO_URI"),
            mongo_db=crawler.settings.get("MONGO_DB"),
        )


    def open_spider(self, spider):
        self.client = AsyncIOMotorClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]


    def close_spider(self, spider):
        self.client.close()


    async def process_item(self, item, spider):
        item['record_id'] = md5(item['source'].encode("utf-8")).hexdigest()
        existing_item = await self.db[self.collection_name].find_one({'record_id': item['record_id']})
        if existing_item is None:
            item['job_id'] = spider.job_id
            await self.db[self.collection_name].insert_one(ItemAdapter(item).asdict())
        else:
            spider.logger.debug(f"Duplicate Record: {item['record_id']}")
        return item
