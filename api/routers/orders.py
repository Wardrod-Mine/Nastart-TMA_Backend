from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class OrderIn(BaseModel):
    items: list
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    deliveryPrice: Optional[float] = 0
    externalDelivery: Optional[bool] = False


class OrderOut(OrderIn):
    id: str
    created_at: datetime


_ORDERS: List[OrderOut] = []


@router.get("", response_model=list[OrderOut])
def list_orders():
    return _ORDERS


@router.post("", response_model=OrderOut)
def create_order(order: OrderIn):
    o = OrderOut(**order.model_dump(), id=str(uuid4()), created_at=datetime.utcnow())
    _ORDERS.append(o)
    return o


@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: str):
    for o in _ORDERS:
        if o.id == order_id:
            return o
    raise HTTPException(status_code=404, detail="Not Found")
