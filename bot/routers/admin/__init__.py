from aiogram import Router

from bot.middlewares import AdminMiddleware, DatabaseMiddleware

from .admin import router as admin_router
from .edit_product import router as edit_product_router
from .newproduct import router as newproduct_router
from .products import router as products_router

router = Router()
router.message.outer_middleware(AdminMiddleware())
router.message.middleware(DatabaseMiddleware())
router.callback_query.middleware(DatabaseMiddleware())

router.include_router(edit_product_router)
router.include_router(admin_router)
router.include_router(newproduct_router)
router.include_router(products_router)
