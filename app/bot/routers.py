import os

from dotenv import load_dotenv
from fastapi import APIRouter, Request
from app.bot.service import insert_balance, run

router = APIRouter(prefix='/app', tags=['Bot'])

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
ALGO = os.getenv('ALGO')


@router.post("/run")
async def app(
        request: Request,
        balance: float,
):
    await insert_balance(request, balance=balance)
    await run(request)
    return {'message': 'ok'}

