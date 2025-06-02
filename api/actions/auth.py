from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from db.dals import UserDAL
from db.models import User
import settings
from db.session import get_db
from hashing import Hasher


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/token")


async def _get_user_by_email_for_auth(email: str, db) -> User | None:
    async with db as session:
        async with session.begin():
            user_dal = UserDAL(session)
            return await user_dal.get_user_by_email(email)


async def authenticate_user(email: str, password: str, db) -> User | None:
    user = await _get_user_by_email_for_auth(email, db)
    if not user:
        return None
    if not Hasher.verify_password(password, user.hashed_password):
        return None
    return user


async def get_current_user_from_token(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password"
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email: str = payload.get("sub")
        print(email)
        if not email:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await _get_user_by_email_for_auth(email, db)
    if not user:
        raise credentials_exception
    return user