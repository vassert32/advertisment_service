from pydantic import BaseModel
from typing import Optional, List

class AdBase(BaseModel):
    title: str
    description: str
    budget: float
    target_audience: str

    class Config:
        orm_mode = True

class AdCreate(AdBase):
    pass

class Ad(AdBase):
    id: int
    generated_text: Optional[str] = None

    class Config:
        orm_mode = True

class AdData(BaseModel):
    prompt: str

class AdText(BaseModel):
    generated_text: str

# Добавим поле budget в данные пользователя для рекомендации
class UserDataInput(BaseModel):
    age: int
    interests: str
    budget: float
