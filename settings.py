from envparse import Env

env = Env()

REAL_DATABASE_URL = env.str(
    "REAL_DATABASE_URL",
    default="postgresql+asyncpg://postgres:root@localhost:5432/firstFastApiProject",
)

TEST_DATABASE_URL = env.str(
    "TEST_DATABASE_URL",
    default="postgresql+asyncpg://postgres:root@localhost:5432/firstFastApiProject_test",
)

SECRET_KEY = env.str("SECRET_KEY", default="a_very_secret_key")
ALGORITHM = env.str("ALGORITHM", default="HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = env.int("ACCESS_TOKEN_EXPIRE_MINUTES", default=1440)
