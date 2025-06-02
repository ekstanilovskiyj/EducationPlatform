from db.dals import UserDAL
from api.models import ShowUser, UserCreate
from hashing import Hasher
from uuid import UUID
from api.models import UpdateUserRequest



async def _create_new_user(body: UserCreate, session) -> ShowUser:
    async with session.begin():
        user_dal = UserDAL(session)

        user = await user_dal.create_user(
            name=body.name,
            surname=body.surname,
            email=body.email,
            hashed_password=Hasher.get_password_hash(body.password),
        )

        return ShowUser(
            user_id=user.user_id,
            name=user.name,
            surname=user.surname,
            email=user.email,
            is_active=user.is_active,
        )


async def _delete_user(user_id: UUID, session) -> UUID | None:
    async with session.begin():
        user_dal = UserDAL(session)
        deleted_user = await user_dal.delete_user(user_id)
        return deleted_user


async def _get_user_by_id(user_id: UUID, session) -> ShowUser | None:
    async with session.begin():
        user_dal = UserDAL(session)
        user = await user_dal.get_user(user_id)
        if user:
            return ShowUser(
                user_id=user.user_id,
                name=user.name,
                surname=user.surname,
                email=user.email,
                is_active=user.is_active,
            )
        return None


async def _update_user(body: UpdateUserRequest, user_id, session) -> UUID | None:
    async with session.begin():
        user_dal = UserDAL(session)
        updated_user = await user_dal.update_user(
            user_id, **body.model_dump(exclude_none=True)
        )
        return updated_user