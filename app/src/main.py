from typing import List
import aiofiles
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from starlette.middleware.gzip import GZipMiddleware

from scraping.router import router as scraping_router
from database import get_mongo, Mongo
from schema import Page


app = FastAPI()

app.add_middleware(GZipMiddleware, minimum_size=1000)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(router=scraping_router, prefix="/scrapyd")


@app.get("/pages/{job_id}", response_model=List[Page])
async def get_pages(
    job_id: str,
    mongo: Mongo = Depends(get_mongo)
):
    filename = await mongo.export_to_json(job_id)
    if not filename:
        raise HTTPException(status_code=404, detail="No data found for this job ID")

    async def iterfile():
        async with aiofiles.open(filename, mode="rb") as file_like:
            while chunk := await file_like.read(8192):  # 8KB chunks
                yield chunk

    return StreamingResponse(
        iterfile(), 
        media_type="application/x-jsonlines",
        headers={
            "Content-Disposition": f"attachment; filename={job_id}.jsonl"
        }
    )
