# Copyright (c) MONAI Consortium
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging

from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from monailabel.endpoints.user.auth import UserListResponse, UserDetailResponse, Register, \
    get_password_hash, validate_token, get_current_user_db
from monailabel.database import Base, engine, get_session
from monailabel.endpoints.user import models

# Create the database
Base.metadata.create_all(engine)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="",
    tags=["Auth"],
    responses={404: {"description": "Not found"}},
)

@router.get("/auth/my-profile", response_model=UserDetailResponse, dependencies=[Depends(validate_token)])
async def my_profile(current_user: UserDetailResponse = Depends(get_current_user_db)):
    try:
        if not current_user:
            return {"success": False, "message": None, "data": None}
    except Exception as e:
        return {"success": False, "message": e, "data": None}

    return {"success": True, "message": None, "data": current_user}