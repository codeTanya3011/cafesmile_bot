from telegramBotCafe.handlers.start import start_router
from telegramBotCafe.handlers.info import router as info_router
from telegramBotCafe.handlers.catalog import router as catalog_router
from telegramBotCafe.handlers.cart import router as cart_router
from telegramBotCafe.handlers.order import router as order_router


routers = (start_router, info_router, catalog_router, cart_router, order_router)

