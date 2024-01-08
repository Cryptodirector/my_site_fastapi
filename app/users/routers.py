import os

from dotenv import load_dotenv
from fastapi import APIRouter, Response, Request, Form
from sqlalchemy import select, insert

from app.database.config import async_session_maker
from app.users.models import User
from app.users.security import Hasher, access_security
from fastapi import HTTPException
from jose import jwt

load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')
ALGO = os.getenv('ALGO')
KEY = os.getenv('KEY')

router = APIRouter(prefix='/auth', tags=['Пользователь'])


@router.post('/registration')
async def registration(
        username: str = Form(),
        password: str = Form(),
        email: str = Form(),
        apikey: str = Form(),
        apisecret: str = Form(),
):
    async with async_session_maker() as session:
        hashed_password = Hasher.get_password_hash(password)
        stmt = insert(User).values(
            username=username,
            hashed_password=hashed_password,
            email=email,
            api_key=apikey,
            api_secret=apisecret
        )
        await session.execute(stmt)
        await session.commit()


@router.post("/auth")
async def login_post(
        response: Response,
        email: str = Form(),
        password: str = Form()
):
    async with async_session_maker() as session:
        query = select(User).where(User.email == email)
        user = await session.execute(query)
        for users in user.scalars():

            if email == users.email and Hasher.verify_password(password, users.hashed_password) is True:
                subject = {'username': users.email, 'password': users.hashed_password}
                access_token = access_security.create_access_token(subject=subject)

                response.set_cookie(key=KEY,
                                    value=access_token,
                                    httponly=True,
                                    )
                return response


@router.post('/logout')
async def logout(response: Response):
    response.delete_cookie(key=KEY)


@router.get("/users/me")
async def read_current_user(request: Request):

    for value in request.cookies.values():
        payload = jwt.decode(value, SECRET_KEY, algorithms=[ALGO])
        return payload['subject']['username']


