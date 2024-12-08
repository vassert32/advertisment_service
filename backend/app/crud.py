from sqlalchemy.orm import Session
from . import models, schemas

def get_ad_by_title(db: Session, title: str):
    return db.query(models.Ad).filter(models.Ad.title == title).first()

def create_ad(db: Session, ad: schemas.AdCreate):
    db_ad = models.Ad(**ad.dict())
    db.add(db_ad)
    db.commit()
    db.refresh(db_ad)
    return db_ad

def get_ad(db: Session, ad_id: int):
    return db.query(models.Ad).filter(models.Ad.id == ad_id).first()

def update_generated_text(db: Session, ad: models.Ad, generated_text: str):
    ad.generated_text = generated_text
    db.commit()
    db.refresh(ad)
    return ad
