from aiogram.filters import BaseFilter
from Files.support_function import make_callback_route
from aiogram import types


class CallbackRouteFilter(BaseFilter):
    def __init__(self):
        pass

    async def __call__(self, callback_query: types.CallbackQuery) -> bool:
        routes = await make_callback_route(None)
        return callback_query.data in routes
