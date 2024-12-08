from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, schemas, crud, database
import os
import requests
from .initial_ads import initial_ads

app = FastAPI()


@app.on_event("startup")
def startup_event():
    models.Base.metadata.create_all(bind=database.engine)
    db = next(database.get_db())
    ml_service_url = os.getenv("ML_SERVICE_URL", "http://ml:8001/generate_text/")

    # Проверяем и добавляем недостающие объявления из initial_ads
    for ad_data in initial_ads:
        existing_ad = crud.get_ad_by_title(db, ad_data["title"])
        if not existing_ad:
            ad_obj = crud.create_ad(db=db, ad=schemas.AdCreate(**ad_data))
            # Генерируем текст
            prompt = (
                f"Создай привлекательный рекламный текст для продукта:\n"
                f"Название: {ad_obj.title}\n"
                f"Описание: {ad_obj.description}\n"
                f"Бюджет: {ad_obj.budget}\n"
                f"Целевая аудитория: {ad_obj.target_audience}\n"
                f"Текст должен быть цепляющим и призывать к действию."
            )
            try:
                response = requests.post(ml_service_url, json={"prompt": prompt})
                response.raise_for_status()
                generated_text = response.json().get("generated_text")
                if generated_text:
                    crud.update_generated_text(db=db, ad=ad_obj, generated_text=generated_text)
            except:
                pass


@app.post("/ads/", response_model=schemas.Ad)
def create_ad(ad: schemas.AdCreate, db: Session = Depends(database.get_db)):
    db_ad = crud.create_ad(db=db, ad=ad)

    ml_service_url = os.getenv("ML_SERVICE_URL", "http://ml:8001/generate_text/")
    prompt = (
        f"Создай привлекательный рекламный текст для продукта:\n"
        f"Название: {db_ad.title}\n"
        f"Описание: {db_ad.description}\n"
        f"Бюджет: {db_ad.budget}\n"
        f"Целевая аудитория: {db_ad.target_audience}\n"
        f"Текст должен быть цепляющим и призывать к действию."
    )
    try:
        response = requests.post(ml_service_url, json={"prompt": prompt})
        response.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при обращении к ML-сервису: {e}")

    generated_text = response.json().get("generated_text")
    if not generated_text:
        raise HTTPException(status_code=500, detail="ML-сервис не вернул сгенерированный текст.")

    db_ad = crud.update_generated_text(db=db, ad=db_ad, generated_text=generated_text)
    return db_ad


@app.get("/ads/{ad_id}", response_model=schemas.Ad)
def read_ad(ad_id: int, db: Session = Depends(database.get_db)):
    db_ad = crud.get_ad(db, ad_id=ad_id)
    if db_ad is None:
        raise HTTPException(status_code=404, detail="Ad not found")
    return db_ad


@app.post("/generate_ad_text/", response_model=schemas.AdText)
def generate_ad_text(ad_data: schemas.AdData):
    ml_service_url = os.getenv("ML_SERVICE_URL", "http://ml:8001/generate_text/")
    prompt = ad_data.prompt
    try:
        response = requests.post(ml_service_url, json={"prompt": prompt})
        response.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при обращении к ML-сервису: {e}")

    generated_text = response.json().get("generated_text")
    if not generated_text:
        raise HTTPException(status_code=500, detail="ML-сервис не вернул сгенерированный текст.")

    return {"generated_text": generated_text}


@app.post("/recommend_ads/")
def recommend_ads(user_data: schemas.UserDataInput, db: Session = Depends(database.get_db)):
    # Получаем все объявления
    ads = db.query(models.Ad).all()
    if not ads:
        return []

    ads_for_rank = []
    for ad in ads:
        ads_for_rank.append({
            "id": ad.id,
            "title": ad.title,
            "description": ad.description,
            "target_audience": ad.target_audience,
            "generated_text": ad.generated_text if ad.generated_text else "",
            "budget": ad.budget
        })

    # Теперь вызываем ML-сервис, который выполнит моковую логику ранжирования
    ml_rank_url = os.getenv("ML_RANK_URL", "http://ml:8001/rank_ads/")
    try:
        response = requests.post(ml_rank_url, json={"user": {"age": user_data.age, "interests": user_data.interests, "budget": user_data.budget}, "ads": ads_for_rank})
        response.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при обращении к ранжирующему ML-сервису: {e}")

    ranked_ids = response.json().get("ranked_ads", [])
    id_to_ad = {ad.id: ad for ad in ads}
    ranked_ads = [id_to_ad[ad_id] for ad_id in ranked_ids if ad_id in id_to_ad]

    # Ограничим до 10 штук
    ranked_ads = ranked_ads[:10]
    return ranked_ads


@app.delete("/ads/{ad_id}")
def delete_ad(ad_id: int, db: Session = Depends(database.get_db)):
    db_ad = crud.get_ad(db, ad_id=ad_id)
    if db_ad is None:
        raise HTTPException(status_code=404, detail="Ad not found")

    db.delete(db_ad)
    db.commit()
    return {"detail": "Ad deleted successfully"}
