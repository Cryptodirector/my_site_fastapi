from pydantic import BaseModel


class CUser(BaseModel):
    username: str
    email: str
    password: str


