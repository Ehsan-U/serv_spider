import json
import os
from typing import AsyncGenerator
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCursor
import aiofiles

from config import DB_NAME, DB_SERVER


class Mongo:
    collection = "pages"

    def __init__(self):
        self.mongo_uri = DB_SERVER
        self.mongo_db = DB_NAME
        self.client: AsyncIOMotorClient = None


    async def __aenter__(self):
        self.client: AsyncIOMotorClient = AsyncIOMotorClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        return self


    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            self.client.close()


    async def results(self, job_id: str) -> AsyncGenerator:
        cursor: AsyncIOMotorCursor = self.db[self.collection].find({'job_id': job_id}, {'_id': 0, 'record_id': 0})
        async for document in cursor:
            yield document    


    async def export_to_json(self, job_id: str):
        os.makedirs("exports", exist_ok=True)
        filename = f"exports/{job_id}.jsonl"
        if os.path.exists(filename):
            os.remove(filename)

        document_count = 0

        async with aiofiles.open(filename, mode='w') as f:
            await f.write("[\n")
            async for document in self.results(job_id):
                if document_count > 0:
                    await f.write(",\n")
                json_line = json.dumps(document, ensure_ascii=False)
                await f.write(json_line)
                document_count += 1
            await f.write("\n]")

        if document_count == 0:
            os.unlink(filename)
            return None

        return filename


async def get_mongo():
    async with Mongo() as mongo:
        yield mongo
