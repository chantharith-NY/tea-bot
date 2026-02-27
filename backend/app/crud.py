from sqlalchemy.orm import Session
from . import models
from .schemas import OrderCreate

def create_order(db: Session, order: OrderCreate):
    db_order = models.Order(**order.dict())
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

def get_pending_orders(db: Session):
    return db.query(models.Order).filter(models.Order.status == "pending").all()

def mark_all_bought(db: Session):
    db.query(models.Order).filter(models.Order.status == "pending").update({"status": "bought"})
    db.commit()