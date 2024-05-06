from aiogram.filters import BaseFilter
from Files.support_function import make_callback_regions
from aiogram import types


class CallbackRegionFilter(BaseFilter):
    def __init__(self):
        pass

    async def __call__(self, callback_query: types.CallbackQuery) -> bool:
        regions = await make_callback_regions()
        return callback_query.data in regions
