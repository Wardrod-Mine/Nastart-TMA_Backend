from fastapi import APIRouter

from api.deps import SessionDep
from api.schemas import ItemResponse
from db.crud import get_all_items, get_item_by_id

router = APIRouter()


@router.get("", response_model=list[ItemResponse])
async def get_items(db: SessionDep):
    return get_all_items(db)


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(item_id: int, db: SessionDep):
    return get_item_by_id(db, item_id)
