from typing import Optional

from pydantic import BaseModel


class ProjectView(BaseModel):
    id: str
    ownerId: Optional[int]
    displayName: str

class ProjectViewList(BaseModel):
    count: int
    projectViews: list[ProjectView]