from aiogram import Router



from handlers.admin import router as admin_router

from handlers.booking import router as booking_router

from handlers.common import router as common_router

from handlers.my_bookings import router as my_bookings_router

from handlers.services import router as services_router





def setup_routers() -> Router:

    root_router = Router()

    root_router.include_router(common_router)

    root_router.include_router(services_router)

    root_router.include_router(booking_router)

    root_router.include_router(my_bookings_router)

    root_router.include_router(admin_router)

    return root_router

