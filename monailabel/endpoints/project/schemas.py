import logging

from typing import List, Union, Literal

from pydantic import BaseModel
from monailabel.schemas import CoreModel

logger = logging.getLogger(__name__)

class CreateProject(BaseModel):
    name: str
    description: Union[str, None] = None
    workflow: Union[str, None] = None
    status: Literal['active', 'inactive']

class Project(BaseModel):
    name: str
    description: Union[str, None] = None
    workflow: Union[str, None] = None
    status: Union[str, None] = None

class ProjectWId(Project):
    id: str
    
class ProjectListResponse(CoreModel):
    data: Union[List[ProjectWId], object] = None
    
class ProjectDetailResponse(CoreModel):
    data: Union[ProjectWId, object] = None
