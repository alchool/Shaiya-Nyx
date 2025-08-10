from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    email: Optional[EmailStr]

class UserOut(BaseModel):
    UserNo: int
    UserID: str
    Email: Optional[str]
    Point: int

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class CharOut(BaseModel):
    CharID: int
    Name: str
    Level: int
    Exp: int
    kills: int

    class Config:
        orm_mode = True
