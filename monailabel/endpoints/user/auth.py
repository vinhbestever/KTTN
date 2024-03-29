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

import json
import os
from datetime import datetime, timedelta
from typing import List, Union, Literal

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, ValidationError
from sqlalchemy.orm import Session

from monailabel.config import settings
from monailabel.endpoints.user import models
from monailabel.schemas import CoreModel
from monailabel.database import get_session


logger = logging.getLogger(__name__)

# openssl rand -hex 32
SECRET_KEY = "c1d2508874b7774026272647cd1d2c0471a9e81d949a0f3a85abe413eb2a95a0"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

scopes = {
    "admin": "Who can run training and everything...",
    "reviewer": "Who can validate and modify saved annotations etc..",
    "annotator": "Who can annotate and submit labels",
    "user": "Annotator who cannot submit labels",
}

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
reusable_oauth2 = HTTPBearer(scheme_name='Authorization')


class Token(BaseModel):
    access_token: str
    token_type: str
    
class LoginResponse(CoreModel):
    data: Union[Token, object] = None


class TokenData(BaseModel):
    username: str = ""
    scopes: List[str] = []


class User(BaseModel):
    username: str
    email: Union[str, None] = None
    full_name: Union[str, None] = None
    disabled: Union[bool, None] = None
    scopes: List[str] = []


class UserInDB(User):
    hashed_password: str


class UserInfo(BaseModel):
    username: str
    email: Union[str, None] = None
    full_name: Union[str, None] = None
    disabled: Union[bool, None] = None
    scopes: Literal['admin', 'user']

class CreateUser(UserInfo):
    hashed_password: str

class UserWId(UserInfo):
    id: str

class Login(BaseModel):
    username: str
    password: str

class Register(Login):
    username: str
    password: str
    email: Union[str, None] = None
    full_name: Union[str, None] = None
    scopes: Literal['admin', 'user']

class RegisterResponse(CoreModel):
    data: Union[UserWId, object] = None
    
class UserListResponse(CoreModel):
    data: Union[List[UserWId], object] = None
    
class UserDetailResponse(CoreModel):
    data: Union[UserWId, object] = None


def validate_token(http_authorization_credentials = Depends(reusable_oauth2), session: Session = Depends(get_session)) -> str:
    """
    Decode JWT token to get username => return username
    """
    try:
        payload = jwt.decode(http_authorization_credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        
        user = session.query(models.User) \
            .filter(models.User.username == payload.get('username')) \
            .first()
            
        logger.info(f"User Token: {user.username}")
            
        if not user:
            raise HTTPException(status_code=403, detail="Token expired")

        if payload.get('exp') < int(datetime.now().timestamp()):
            raise HTTPException(status_code=403, detail="Token expired")
        return payload.get('exp')
    # except(jwt.PyJWTError, ValidationError):
    except Exception as e:
        logger.info(f"Token Error: {e}")
        raise HTTPException(
            status_code=403,
            detail=f"Could not validate credentials",
        )

def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    security_scopes: SecurityScopes, token: str = Depends(oauth2_scheme) if settings.MONAI_LABEL_AUTH_ENABLE else ""
):
    if not settings.MONAI_LABEL_AUTH_ENABLE:
        return User(username="admin")

    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(scopes=token_scopes, username=username)
    except (JWTError, ValidationError):
        raise credentials_exception

    user = get_user(token_data.username)
    if user is None:
        raise credentials_exception

    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
    return user


async def get_admin_user(current_user: User = Security(get_current_user, scopes=["admin"])):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_reviwer_user(current_user: User = Security(get_current_user, scopes=["reviewer"])):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_annotator_user(current_user: User = Security(get_current_user, scopes=["annotator"])):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_basic_user(current_user: User = Security(get_current_user, scopes=["user"])):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(username: str):
    f = settings.MONAI_LABEL_AUTH_DB
    if not f:
        f = os.path.join(os.path.dirname(os.path.realpath(__file__)), "users.json")

    db = {}
    if os.path.exists(f):
        with open(f) as fp:
            db = json.load(fp)

    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)
    return None


def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def authenticate_user_db(username, password, session):
    user = session.query(models.User).filter(models.User.username == username).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
