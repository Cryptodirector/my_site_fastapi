from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware

from app.front.routers import router as router_front
from app.users.routers import router as router_auth

app = FastAPI()

app.mount('/static', StaticFiles(directory='app/static'), name='static')

app.include_router(router_front)
app.include_router(router_auth)


origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)