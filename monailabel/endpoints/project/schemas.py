import logging

from enum import Enum
from typing import List, Union, Literal

from pydantic import BaseModel, Field
from monailabel.schemas import CoreModel

logger = logging.getLogger(__name__)

class ProjectStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    
class CreateProject(BaseModel):
    name: str
    description: Union[str, None] = None
    status: Literal['active', 'inactive']

class Project(BaseModel):
    name: str = Field(default=None)
    description: str = Field(default=None)
    status: str = Field(default="active")

class ProjectWId(Project):
    id: int = Field(default=1)
    
class ProjectListResponse(CoreModel):
    items: Union[List[ProjectWId], object] = None
    total: int = Field(default=0)
    
class ProjectDetailResponse(CoreModel):
    data: Union[ProjectWId, object] = None
