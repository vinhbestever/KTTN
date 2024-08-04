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
import os

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi.responses import FileResponse

from monailabel.endpoints.user.auth import User, get_basic_user
from monailabel.interfaces.app import MONAILabelApp
from monailabel.interfaces.utils.app import app_instance
from monailabel.utils.others.generic import file_ext, get_mime_type

from monailabel.endpoints.user.auth import validate_token

from sqlalchemy import String
from monailabel.orthanc_client.orthanc_client import DICOMWebAPI


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/orthanc",
    tags=["Orthanc"],
    responses={404: {"description": "Not found"}},
)


# @router.get("/upload", response_model=UserDetailResponse, dependencies=[Depends(validate_token)])
# async def my_profile(current_user: UserDetailResponse = Depends(get_current_user_db)):
@router.get("/studies")
async def studies():
    try:
        studies = DICOMWebAPI().search_for_studies()

        return {"success": True, "message": None, "data": studies}
    except Exception as e:
        return {"success": False, "message": e, "data": None}
    
@router.get("/instances")
async def instances():
    try:
        instances = DICOMWebAPI().search_for_instances()

        return {"success": True, "message": None, "data": instances}
    except Exception as e:
        return {"success": False, "message": e, "data": None}
    
@router.post("/upload")
async def upload(files: list[UploadFile]):
    try:        
        instances = await DICOMWebAPI().store_instances(files)

        return {"success": True, "message": None, "data": instances}
    except Exception as e:
        return {"success": False, "message": e, "data": None}
    
@router.get("/export")
async def export(study_id: str):
    try:
        metadata_datasets = DICOMWebAPI().retrieve_study_metadata(study_id)

        logger.info(f"Test export: {metadata_datasets}")

        return {"success": True, "message": None, "data": metadata_datasets}
    except Exception as e:
        return {"success": False, "message": e, "data": None}
    