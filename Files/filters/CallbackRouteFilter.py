from aiogram.filters import BaseFilter
from support_function import make_callback_route
from aiogram import types


class CallbackRouteFilter(BaseFilter):
    def __init__(self):
        pass

    async def __call__(self, callback_query: types.CallbackQuery) -> bool:
        routes = await make_callback_route(None)
        return any(callback_query.data in item for item in routes)
