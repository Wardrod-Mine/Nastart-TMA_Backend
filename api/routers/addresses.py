import aiohttp
from fastapi import APIRouter

from api.deps import SessionDep
from api.services.addresses import calculate_delivery_price
from config import settings

router = APIRouter()


@router.get("/delivery-price")
async def get_delivery_price(address: str, db: SessionDep):
    return {"price": await calculate_delivery_price(address)}


@router.get("/suggest")
async def get_checkout(address_input: str, db: SessionDep):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://suggest-maps.yandex.ru/v1/suggest?apikey={settings.SUGGEST_API_TOKEN}&text={address_input}&ll=30.308343,59.957189&print_address=1&types=house&attrs=uri"
        ) as response:
            data = await response.json()
            return data["results"]
