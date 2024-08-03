from pydantic import BaseModel


class Page(BaseModel):
    source: str
    content: str
    job_id: str