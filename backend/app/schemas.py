from pydantic import BaseModel
from datetime import datetime


# ===============================
# Create Order Schema
# ===============================
class OrderCreate(BaseModel):
    chat_id: int
    user_id: int
    product: str
    quantity: int
    buyer: str


# ===============================
# Order Response Schema
# ===============================
class OrderResponse(BaseModel):
    id: int
    chat_id: int
    user_id: int
    product: str
    quantity: int
    buyer: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True  # Important for SQLAlchemy