from fastapi import APIRouter, Depends

from scraping.service import ScrapydManager, get_scrapyd_manager
from scraping.schema import JobScheduleRequest


router = APIRouter()


@router.get("/status")
async def get_scrapyd_status(
    manager: ScrapydManager = Depends(get_scrapyd_manager)
):
    response = await manager.deamon_status()
    return response


@router.post("/schedule")
async def schedule_scraping_job(
    request: JobScheduleRequest, 
    manager: ScrapydManager = Depends(get_scrapyd_manager)
):
    response = await manager.schedule(
        request.url, 
        project=request.project,
        spider=request.spider,
        settings=request.settings,
        render=request.render
    )    
    return response


@router.get("/jobs/{project}/{job_id}")
async def get_job_status(
    project: str,
    job_id: str,
    manager: ScrapydManager = Depends(get_scrapyd_manager)
):
    response = await manager.job_status(job_id, project)
    return response