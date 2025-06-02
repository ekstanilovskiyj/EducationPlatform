from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine

import settings

engine = create_async_engine(settings.REAL_DATABASE_URL, future=True, echo=True)

async_session = async_sessionmaker(engine, expire_on_commit=False)


async def get_db():
    async with async_session() as session:
        yield session
    # try:
    #     session = async_session()
    #     yield session
    # finally:
    #     await session.close()
