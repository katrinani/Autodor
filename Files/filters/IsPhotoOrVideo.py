from aiogram.filters import BaseFilter
from aiogram.types import Message


class IsPhotoOrVideo(BaseFilter):
    def __init__(self) -> None:
        pass

    async def __call__(self, message: Message) -> bool:
        return message.photo is not None or message.video is not None
