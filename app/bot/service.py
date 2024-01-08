import os

from dotenv import load_dotenv
from fastapi import APIRouter, Request
from jose import jwt
from sqlalchemy import select, update, insert

from app.database.config import async_session_maker
from app.users.models import User
from app.bot.bot import Trade

router = APIRouter()

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
ALGO = os.getenv('ALGO')


async def insert_balance(
        request: Request,
        balance: float,
):
    for value in request.cookies.values():
        payload = jwt.decode(value, SECRET_KEY, algorithms=[ALGO])

        async with async_session_maker() as session:
            user = select(User).where(User.email == payload['subject']['username'])
            result = await session.execute(user)
            for users in result.scalars():
                if users:
                    deposit = update(User).where(User.id == users.id).values(balance=balance)
                    await session.execute(deposit)
                    await session.commit()


async def run(request: Request):
    async with async_session_maker() as session:
        for value in request.cookies.values():
            payload = jwt.decode(value, SECRET_KEY, algorithms=[ALGO])
            user = select(User).where(User.email == payload['subject']['username'])
            users = await session.execute(user)

            for users_data in users.scalars():
                await Trade(
                    api_key=users_data.api_key,
                    api_secret=users_data.api_secret
                ).get_kline_1m(balance=users_data.balance)
