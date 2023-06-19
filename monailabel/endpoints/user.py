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
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from monailabel.endpoints.user.auth import ACCESS_TOKEN_EXPIRE_MINUTES, Token, UserListResponse, UserDetailResponse, Register, \
    authenticate_user, create_access_token, authenticate_user_db, get_password_hash, validate_token
from monailabel.database import Base, engine, get_session
from monailabel.endpoints.user import models

# Create the database
Base.metadata.create_all(engine)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="",
    tags=["User"],
    responses={404: {"description": "Not found"}},
)

@router.get("/users", response_model=UserListResponse, dependencies=[Depends(validate_token)])
async def user_list(session: Session = Depends(get_session)):
    try:
        users = session.query(models.User).all()
    except Exception as e:
        return {"success": False, "message": e, "data": None}

    return {"success": True, "message": None, "data": users}

@router.post("/users", response_model=UserListResponse, dependencies=[Depends(validate_token)])
async def create_user(user: Register, session: Session = Depends(get_session)):
    try:
        user = models.User(
            username = user.username, 
            email = user.email, 
            hashed_password = get_password_hash(user.password),
            full_name = user.full_name,
            disabled = False,
            scopes = user.scopes
        )

        # add it to the session and commit it
        session.add(user)
        session.commit()
        session.refresh(user)
    except Exception as e:
        return {"success": False, "message": e, "data": None}

    return {"success": True, "message": None, "data": None}

@router.get("/users/{user_id}", response_model=UserDetailResponse, dependencies=[Depends(validate_token)])
async def user_detail(user_id: str, session: Session = Depends(get_session)):
    try:
        user = session.query(models.User).filter(models.User.id == user_id).first()
    except Exception as e:
        return {"success": False, "message": e, "data": None}

    return {"success": True, "message": None, "data": user}

@router.put("/users/{user_id}", response_model=UserDetailResponse, dependencies=[Depends(validate_token)])
async def update_user(user_id: str, user: Register, session: Session = Depends(get_session)):
    try:
        db_user = session.get(models.User, user_id)
        if not db_user:
            return {"success": False, "message": 'Not found', "data": None}

        user_data = user.dict(exclude_unset=True)
        for key, value in user_data.items():
            setattr(db_user, key, value)
            
        # add it to the session and commit it
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
    except Exception as e:
        return {"success": False, "message": e, "data": None}

    return {"success": True, "message": None, "data": db_user}

@router.delete("/users/{user_id}", response_model=UserDetailResponse, dependencies=[Depends(validate_token)])
async def delete_user(user_id: str, session: Session = Depends(get_session)):
    try:
        user = session.query(models.User).filter_by(id=car_id).delete()
        if num_rows == 0:
             return {"success": False, "message": 'Not found', "data": None}
        session.commit()
    except Exception as e:
        return {"success": False, "message": e, "data": None}

    return {"success": True, "message": None, "data": None}