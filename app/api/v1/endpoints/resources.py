from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.core.deps import DbSession, EditorUser
from app.models.resource import Resource
from app.schemas.common import MessageResponse
from app.schemas.resource import ResourceCreate, ResourceRead, ResourceUpdate
from app.utils import apply_updates

router = APIRouter(prefix="/resources", tags=["resources"])


@router.get("", response_model=list[ResourceRead])
def list_resources(db: DbSession):
    return list(db.scalars(select(Resource).order_by(Resource.title)).all())


@router.post("", response_model=ResourceRead, status_code=status.HTTP_201_CREATED)
def create_resource(payload: ResourceCreate, db: DbSession, _: EditorUser):
    resource = Resource(**payload.model_dump())
    db.add(resource)
    db.commit()
    db.refresh(resource)
    return resource


@router.patch("/{resource_id}", response_model=ResourceRead)
def update_resource(resource_id: int, payload: ResourceUpdate, db: DbSession, _: EditorUser):
    resource = db.get(Resource, resource_id)
    if resource is None:
        raise HTTPException(status_code=404, detail="Resource not found")
    apply_updates(resource, payload.model_dump(exclude_unset=True))
    db.commit()
    db.refresh(resource)
    return resource


@router.delete("/{resource_id}", response_model=MessageResponse)
def delete_resource(resource_id: int, db: DbSession, _: EditorUser):
    resource = db.get(Resource, resource_id)
    if resource is None:
        raise HTTPException(status_code=404, detail="Resource not found")
    db.delete(resource)
    db.commit()
    return MessageResponse(message="Resource deleted")
