from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI()

# Схемы для ранжирующего эндпоинта
class UserData(BaseModel):
    age: int
    interests: str
    budget: float

class AdItem(BaseModel):
    id: int
    title: str
    description: str
    target_audience: str
    generated_text: str
    budget: float

class RankRequest(BaseModel):
    user: UserData
    ads: List[AdItem]

class RankResponse(BaseModel):
    ranked_ads: List[int]

@app.post("/rank_ads/", response_model=RankResponse)
def rank_ads(rank_request: RankRequest):
    # Моковая логика ранжирования по бюджету
    # Сортируем объявления по модулю разницы между budget объявления и user.budget
    user_budget = rank_request.user.budget
    ads_sorted = sorted(rank_request.ads, key=lambda ad: abs(ad.budget - user_budget))
    ranked_ids = [ad.id for ad in ads_sorted]
    return {"ranked_ads": ranked_ids}

# Генерация текста (как было ранее)
from pydantic import BaseModel
from transformers import pipeline

generator = pipeline('text-generation', model='gpt2')

class TextGenerationRequest(BaseModel):
    prompt: str

class TextGenerationResponse(BaseModel):
    generated_text: str

@app.post("/generate_text/", response_model=TextGenerationResponse)
def generate_text(request: TextGenerationRequest):
    result = generator(
        request.prompt,
        max_length=150,
        num_return_sequences=1,
        temperature=0.7,
        top_p=0.9,
        do_sample=True
    )
    generated_text = result[0]['generated_text']
    return {"generated_text": generated_text}
