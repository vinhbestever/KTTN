import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from monailabel.endpoints.project.schemas import CreateProject, ProjectListResponse, ProjectDetailResponse
from monailabel.endpoints.user.auth import validate_token
from monailabel.database import Base, engine, get_session
from monailabel.endpoints.project import models

# Create the database
Base.metadata.create_all(engine)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="",
    tags=["Project"],
    responses={404: {"description": "Not found"}},
)

@router.get("/projects", response_model=ProjectListResponse, dependencies=[Depends(validate_token)])
async def project_list(session: Session = Depends(get_session)):
    try:
        projects = session.query(models.Project).all()
    except Exception as e:
        return {"success": False, "message": e, "data": None}

    return {"success": True, "message": None, "data": projects}

@router.post("/projects", response_model=ProjectListResponse, dependencies=[Depends(validate_token)])
async def create_project(project: CreateProject, session: Session = Depends(get_session)):
    try:
        project = models.Project(
            name = project.name, 
            description = project.description, 
            status = project.status
        )

        # add it to the session and commit it
        session.add(project)
        session.commit()
        session.refresh(project)
    except Exception as e:
        return {"success": False, "message": e, "data": None}

    return {"success": True, "message": None, "data": None}

@router.get("/projects/{project_id}", response_model=ProjectDetailResponse, dependencies=[Depends(validate_token)])
async def project_detail(project_id: str, session: Session = Depends(get_session)):
    try:
        project = session.query(models.Project).filter(models.Project.id == project_id).first()
    except Exception as e:
        return {"success": False, "message": e, "data": None}

    return {"success": True, "message": None, "data": project}

@router.put("/projects/{project_id}", response_model=ProjectDetailResponse, dependencies=[Depends(validate_token)])
async def update_project(project_id: str, project: CreateProject, session: Session = Depends(get_session)):
    try:
        db_project = session.get(models.Project, project_id)
        if not db_project:
            return {"success": False, "message": 'Not found', "data": None}

        project_data = project.dict(exclude_unset=True)
        for key, value in project_data.items():
            setattr(db_project, key, value)
            
        # add it to the session and commit it
        session.add(db_project)
        session.commit()
        session.refresh(db_project)
    except Exception as e:
        return {"success": False, "message": e, "data": None}

    return {"success": True, "message": None, "data": db_project}

@router.delete("/projects/{project_id}", response_model=ProjectDetailResponse, dependencies=[Depends(validate_token)])
async def delete_project(project_id: str, session: Session = Depends(get_session)):
    try:
        project = session.query(models.Project).filter_by(id=project_id).delete()
        if project == 0:
             return {"success": False, "message": 'Not found', "data": None}
        session.commit()
    except Exception as e:
        return {"success": False, "message": e, "data": None}

    return {"success": True, "message": None, "data": None}