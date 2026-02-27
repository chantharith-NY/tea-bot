from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from .database import Base

class Order(Base):
    __tablename__ = "tea_orders"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer)
    user_id = Column(Integer)
    product = Column(String)
    quantity = Column(Integer)
    buyer = Column(String)
    status = Column(String, default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())