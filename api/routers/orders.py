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
