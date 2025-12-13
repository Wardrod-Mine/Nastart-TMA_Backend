from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.payments import configure_yookassa
from api.routers.addresses import router as addresses_router
from api.routers.checkout import router as checkout_router
from api.routers.items import router as items_router
from api.routers.metrics import router as metrics_router
from api.routers.orders import router as orders_router
from api.webhook import router as webhook_router
from config import settings

configure_yookassa()

app = FastAPI(
    docs_url=None if settings.DEBUG else "/docs",
    redoc_url=None if settings.DEBUG else "/redoc",
)
app.include_router(items_router, prefix="/items", tags=["items"])
app.include_router(checkout_router, prefix="/checkout", tags=["checkout"])
app.include_router(webhook_router, prefix="/webhook", tags=["webhook"])
app.include_router(orders_router, prefix="/orders", tags=["orders"])
app.include_router(metrics_router, prefix="/metrics", tags=["metrics"])
app.include_router(addresses_router, prefix="/addresses", tags=["addresses"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
