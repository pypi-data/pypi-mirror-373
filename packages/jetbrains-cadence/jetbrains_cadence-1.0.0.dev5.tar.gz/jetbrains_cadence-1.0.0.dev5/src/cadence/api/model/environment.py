from typing import Optional

from pydantic import BaseModel, Field


class Pip(BaseModel):
    requirementsPath: str
    type: str = "PIP"


class Poetry(BaseModel):
    directory: str
    type: str = "POETRY"

DependencyManager = Pip | Poetry

class Python(BaseModel):
    version: Optional[str] = None
    dependencyManager: Optional[DependencyManager] = None


class Environment(BaseModel):
    dockerImage: Optional[str] = None
    pythonEnvironment: Optional[Python] = None
    variables: dict[str, str] = Field(default_factory=dict)
    secretVariables: dict[str, str] = Field(default_factory=dict)
