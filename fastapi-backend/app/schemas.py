from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        from_attributes = True

class PredictionCreate(BaseModel):
    prediction: str


class DateRangeRequest(BaseModel):
    start_date: datetime
    end_date: datetime
