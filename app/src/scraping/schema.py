from typing import Dict, Optional
from pydantic import BaseModel, HttpUrl, Field


class JobScheduleRequest(BaseModel):
    url: HttpUrl
    project: str
    spider: str
    settings: Optional[Dict] = Field(default_factory=dict)
    render: Optional[bool] = Field(default=False)
