import asyncio
import os

from dotenv import load_dotenv
from fastapi import APIRouter, Request, Form, Depends, Response, HTTPException
from sqlalchemy import select

from starlette.templating import Jinja2Templates

from app.bot.service import insert_balance, run
from app.database.config import async_session_maker
from app.users.models import User
from app.users.routers import registration as back_registration
from fastapi.responses import RedirectResponse
from app.users.security import Hasher, access_security

router = APIRouter(prefix='/front', tags=['FRONTEND'])
templates = Jinja2Templates(directory='app/templates')

load_dotenv()
KEY = os.getenv('KEY')


@router.get('/main')
async def main(request: Request):
    cookie = request.cookies
    return templates.TemplateResponse('main.html', {'request': request, 'cookie': cookie})


@router.post('/app')
async def app(
        request: Request,
        balance: float = Form(),
):
    await insert_balance(request, balance=balance)
    await run(request)


@router.get('/app')
async def app(request: Request):
    cookie = request.cookies
    return templates.TemplateResponse('app.html', {'request': request, 'cookie': cookie})


class Authentication:

    @staticmethod
    @router.get('/registration')
    async def registration(request: Request):
        return templates.TemplateResponse('registration.html', {'request': request})

    @staticmethod
    @router.post('/registration')
    async def registration_post(
            request: Request,
            reg=Depends(back_registration),
    ):
        redirect_url = request.url_for('login')
        response = RedirectResponse(redirect_url, status_code=302)
        return response

    @staticmethod
    @router.get('/login')
    async def login(request: Request):
        return templates.TemplateResponse('login.html', {'request': request})

    @staticmethod
    @router.post('/login')
    async def login_post(
            request: Request,
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
                    redirect_url = request.url_for('main')
                    response = RedirectResponse(redirect_url, status_code=302)

                    response.set_cookie(key=KEY,
                                        value=access_token,
                                        httponly=True,
                                        )
                    return response

    @staticmethod
    @router.get('/logout')
    async def logout(request: Request):

        redirect_url = request.url_for('login')
        redirect = RedirectResponse(redirect_url)
        redirect.delete_cookie(key=KEY, httponly=True)
        return redirect
