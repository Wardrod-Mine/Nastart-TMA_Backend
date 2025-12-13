from fastapi import APIRouter, Depends

from api.deps import get_user

router = APIRouter()


@router.post("/visit", dependencies=[Depends(get_user)])
async def visit():
    pass
