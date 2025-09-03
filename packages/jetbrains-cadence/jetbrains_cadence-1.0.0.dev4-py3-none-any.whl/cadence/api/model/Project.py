from typing import Optional

from pydantic import BaseModel

from cadence.api.model.License import License


class Project(BaseModel):
    id: str
    name: str
    license: Optional[License]

class ProjectList(BaseModel):
    count: int
    projects: list[Project]