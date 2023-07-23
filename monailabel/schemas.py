from pydantic import BaseModel
from typing import Union

class CoreModel(BaseModel):
    success: bool
    message: Union[str, object] = None
