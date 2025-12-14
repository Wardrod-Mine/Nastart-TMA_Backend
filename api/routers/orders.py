# from fastapi import APIRouter, HTTPException, Header

# from api.deps import SessionDep, get_user
# from api.schemas import OrderResponseBase, OrderResponseItems
# from db.crud import get_order, get_user_orders

# router = APIRouter()


# # @router.get("/{order_id}", tags=["orders"],)
# @router.get("/{order_id}", tags=["orders"], response_model=OrderResponseItems)
# async def get_order_handler(order_id: int, db: SessionDep, user: UserDep):
#     order = get_order(db, order_id)
#     if not user:
#         raise HTTPException(status_code=401, detail="Unauthorized")
#     if not order or order.user_id != user.id:
#         raise HTTPException(status_code=404, detail="Order not found for that user")

#     return order


# @router.get("", response_model=list[OrderResponseBase])
# async def get_orders_handler(
#     db: SessionDep, authorization: str | None = Header(default=None)
# ):
#     # Заглушка: если нет авторизации — вернуть пустой список с 200
#     if not authorization:
#         return []

#     try:
#         user = await get_user(db=db, authorization=authorization)
#     except HTTPException:
#         return []

#     return get_user_orders(db, user.id)


# backend/api/routers/orders.py

from fastapi import APIRouter

from api.deps import SessionDep
from api import schemas

router = APIRouter()


@router.get("/", response_model=list[schemas.OrderRead])
def list_orders(db: SessionDep):
    """
    Временная заглушка: всегда отдаём пустой список заказов.
    Никаких зависимостей по пользователю, чтобы не ронять backend.
    """
    return []
