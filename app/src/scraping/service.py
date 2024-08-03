from typing import Dict
from httpx import AsyncClient, Response

from scraping.constants import *
from scraping.exceptions import *


class ScrapydManager:

    def __init__(self):
        self.scrapyd_url = SCRAPYD_SERVER
        self.client = None


    async def __aenter__(self):
        self.client = AsyncClient()
        return self


    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()


    def _handle_response(self, response: Response):
        try:
            json = response.json()
        except ValueError:
            error = "Scrapyd returned an invalid JSON response: {0}".format(response.text)
            json = {"error": error, "url": response.url}
        return json


    async def deamon_status(self) -> Dict:
        response = await self.client.get(url=DAEMON_STATUS_ENDPOINT)
        return self._handle_response(response)


    async def schedule(self, url: str, project: str, spider: str, settings: Dict, render: bool) -> Dict:        
        setting_params = []
        for name, value in settings.items():
            setting_params.append(f"{name}={value}")
        data = {
            'url': url,
            'render': render if render else '',
            'project': project,
            'spider': spider,
            'setting': setting_params
        }
        response = await self.client.post(url=SCHEDULE_ENDPOINT, data=data)
        return self._handle_response(response)
    
    
    async def job_status(self, job_id: str, project: str) -> Dict:
        jobs = await self.list_jobs(project)
        if 'error' in jobs:
            return jobs
        for state in ["pending","running","finished"]:
            job_ids = [job['id'] for job in jobs[state]]
            if job_id in job_ids:
                return {"status": state}
        return {"status": "not found"}
    

    async def list_jobs(self, project: str) -> Dict:
        params = {
            "project": project
        }
        response = await self.client.get(url=LIST_JOBS_ENDPOINT, params=params)
        return self._handle_response(response)



async def get_scrapyd_manager():
    async with ScrapydManager() as manager:
        yield manager