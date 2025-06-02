from uuid import UUID

from sqlalchemy import and_
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import User


class UserDAL:
    """Data access layer for users"""

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_user(
        self, name: str, surname: str, email: str, hashed_password: str
    ) -> User:
        new_user = User(
            name=name,
            surname=surname,
            email=email,
            hashed_password=hashed_password,
        )
        self.db_session.add(new_user)
        await self.db_session.flush()
        return new_user

    async def delete_user(self, user_id: UUID) -> UUID | None:
        query = (
            update(User)
            .where(and_(User.user_id == user_id, User.is_active == True))
            .values(is_active=False)
            .returning(User.user_id)
        )
        res = await self.db_session.execute(query)
        deleted_user = res.fetchone()
        if deleted_user:
            return deleted_user[0]
        return None

    async def get_user(self, user_id: UUID) -> User | None:
        query = select(User).where(User.user_id == user_id)
        res = await self.db_session.execute(query)
        received_user = res.scalars().one_or_none()
        if received_user:
            return received_user
        return None

    async def update_user(self, user_id, **kwargs) -> UUID | None:
        query = (
            update(User)
            .where(and_(User.user_id == user_id, User.is_active == True))
            .values(**kwargs)
            .returning(User.user_id)
        )
        res = await self.db_session.execute(query)
        updated_user_id = res.fetchone()
        if updated_user_id:
            return updated_user_id[0]
        return None

    async def get_user_by_email(self, email: str) -> User | None:
        query = select(User).where(User.email == email)
        res = await self.db_session.execute(query)
        received_user = res.scalars().one_or_none()
        if received_user:
            return received_user
        return None
