from logging import getLogger
from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from api.actions.auth import get_current_user_from_token
from api.actions.user import _create_new_user
from api.actions.user import _delete_user
from api.actions.user import _get_user_by_id
from api.actions.user import _update_user
from api.models import DeleteUserResponse
from api.models import ShowUser
from api.models import UpdateUserRequest
from api.models import UpdateUserResponse
from api.models import UserCreate
from db.models import User
from db.session import get_db

logger = getLogger(__name__)

user_router = APIRouter()


@user_router.post("/", response_model=ShowUser)
async def create_user(body: UserCreate, db: AsyncSession = Depends(get_db)) -> ShowUser:
    try:
        return await _create_new_user(body, db)
    except IntegrityError as e:
        logger.error(e)
        raise HTTPException(status_code=503, detail=f"Database error: {e}")


@user_router.delete("/", response_model=DeleteUserResponse)
async def delete_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token),
):
    deleted_user = await _delete_user(user_id, db)
    if not deleted_user:
        raise HTTPException(
            status_code=404, detail=f"User with id {user_id} not found."
        )
    return DeleteUserResponse(deleted_user_id=deleted_user)


@user_router.get("/", response_model=ShowUser)
async def get_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token),
):
    user = await _get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(
            status_code=404, detail=f"User with id {user_id} not found."
        )
    return user


@user_router.patch("/", response_model=UpdateUserResponse)
async def update_user_by_id(
    user_id: UUID,
    body: UpdateUserRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token),
):
    if body.model_dump(exclude_none=True) == {}:
        raise HTTPException(
            status_code=422,
            detail="At least one parameter for user update info should be provided",
        )
    user = await _get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(
            status_code=404, detail=f"User with id {user_id} not found."
        )
    try:
        updated_user_id = await _update_user(body, user_id, db)
    except IntegrityError as e:
        logger.error(e)
        raise HTTPException(status_code=503, detail=f"Database error: {e}")
    return UpdateUserResponse(updated_user_id=updated_user_id)
