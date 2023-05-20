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
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from monailabel.endpoints.user.auth import ACCESS_TOKEN_EXPIRE_MINUTES, Token, Register, RegisterResponse, \
    authenticate_user, create_access_token, authenticate_user_db, get_password_hash
from monailabel.database import Base, engine, get_session
from monailabel.endpoints.user import models

# Create the database
Base.metadata.create_all(engine)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="",
    tags=["AppService"],
    responses={404: {"description": "Not found"}},
)

@router.post("/login")
async def login_for_access_token(session: Session = Depends(get_session)):
    # user = authenticate_user_db(form_data.username, form_data.password, session)
    # if not user:
    #     raise HTTPException(status_code=400, detail="Incorrect username or password")

    # logger.info(f"User: {user.username}; Scopes: {user.scopes}")

    # access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # access_token = create_access_token(
    #     data={
    #         "sub": user.username,
    #         "scopes": user.scopes,
    #     },
    #     expires_delta=access_token_expires,
    # )

    user = session.query(models.User).all()

    # close the session
    session.close()

    return {"access_token": user, "token_type": "bearer"}
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=RegisterResponse)
async def register(user: Register, session: Session = Depends(get_session)):
    try:
        user = models.User(
            username = user.username, 
            email = user.email, 
            hashed_password = get_password_hash(user.password),
            full_name = user.full_name,
            disabled = False
        )

        # add it to the session and commit it
        session.add(user)
        session.commit()
        session.refresh(user)
    except Exception as e:
        return {"success": False, "message": e, "data": None}

    return {"success": True, "message": None, "data": user}


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    logger.info(f"User: {user.username}; Scopes: {user.scopes}")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user.username,
            "scopes": user.scopes,
        },
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}
