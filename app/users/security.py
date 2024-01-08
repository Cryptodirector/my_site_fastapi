import os
from datetime import timedelta

from dotenv import load_dotenv
from fastapi_jwt import JwtAccessBearerCookie
from passlib.context import CryptContext

load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
access_security = JwtAccessBearerCookie(
    secret_key=SECRET_KEY,
    auto_error=True,
    access_expires_delta=timedelta(hours=1),  # custom access token valid timedelta
    refresh_expires_delta=timedelta(days=1),  # custom access token valid timedelta
)


class Hasher:
    @staticmethod
    def verify_password(plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password):
        return pwd_context.hash(password)


