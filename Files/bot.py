import asyncio
from json import load
from logging import basicConfig, INFO, FileHandler, StreamHandler
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from handlers.recognize import (
    attractions_5,
    car_service_3,
    dangerous_situation_7,
    traffic_situation_6,
    gas_station_2,
    meal_1,
    parking_lot_4,
    start_recognize
)
from handlers.report import (
    illegal_actions_3,
    road_block_4,
    road_deficiencies_2,
    start_report,
    traffic_accident_1
)
from handlers.voice import voice
from handlers import start

# TODO: сменить .. -> /usr/src/app/ и изменить в конфиге порты

with open(r'../config.json', 'r') as json_file:
    config = load(json_file)
    TOKEN = config["token"]
    WEB_SERVER_HOST = config["server_host"]
    WEBHOOK_PATH = config["webhook_path"]
    WEBHOOK_URL = config["webhook_url"]


async def on_startup(bot: Bot) -> None:
    await bot.set_webhook(f"{WEBHOOK_URL}{WEBHOOK_PATH}")


async def main() -> None:
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    dp.include_router(start.router)
    dp.include_router(attractions_5.router)
    dp.include_router(car_service_3.router)
    dp.include_router(dangerous_situation_7.router)
    dp.include_router(traffic_situation_6.router)
    dp.include_router(gas_station_2.router)
    dp.include_router(meal_1.router)
    dp.include_router(parking_lot_4.router)
    dp.include_router(start_recognize.router)

    dp.include_router(illegal_actions_3.router)
    dp.include_router(road_block_4.router)
    dp.include_router(road_deficiencies_2.router)
    dp.include_router(start_report.router)
    dp.include_router(traffic_accident_1.router)

    dp.include_router(voice.router)

    # Настраиваем логирование
    basicConfig(level=INFO,
                format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
                handlers=[
                    FileHandler('../loging/bot.log'),
                    StreamHandler()
                ])

    dp.startup.register(on_startup)
    app = web.Application()
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    )
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)
    await web._run_app(app, host=WEB_SERVER_HOST)


if __name__ == "__main__":
    asyncio.run(main())
