# backend/app/models.py

from sqlalchemy import Column, Integer, String, Float
from .database import Base

class Ad(Base):
    __tablename__ = "ads"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    budget = Column(Float)
    target_audience = Column(String)
    generated_text = Column(String, nullable=True)  # Новое поле для сгенерированного текста
