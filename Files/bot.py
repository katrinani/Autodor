import asyncio
from json import load
from os import environ, path, makedirs
from logging import basicConfig, INFO, FileHandler, StreamHandler
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from aiogram.types.input_file import InputFile, FSInputFile

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


with open(r'/usr/src/app/config.json', 'r') as json_file:
    config = load(json_file)
    # TOKEN = config["token"]
    TOKEN = environ.get('TOKEN')
    WEB_SERVER_HOST = config["server_host"]
    WEBHOOK_PATH = config["webhook_path"]
    # WEBHOOK_URL = config["webhook_url"]
    WEBHOOK_URL = environ.get('WEBHOOK_URL')

async def on_startup(bot: Bot) -> None:
    name_certificate = environ.get('CERTIFICATE_PATH')
    cert = FSInputFile(name_certificate)
    await bot.set_webhook(
        url=f"{WEBHOOK_URL}{WEBHOOK_PATH}",
        certificate=cert,
        allowed_updates=["message", "callback_query"]
    )


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

    log_path = '/usr/src/app/loging/bot.log'

    # Проверяем существует ли файл
    if not path.exists(log_path):
        makedirs(path.dirname(log_path), exist_ok=True)
        # Создаем файл
        with open(log_path, 'w') as f:
            # Можно записать что-то в файл
            f.write('Log started\n')

    # Настраиваем логирование
    basicConfig(level=INFO,
                format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
                handlers=[
                    FileHandler('/usr/src/app/loging/bot.log'),
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
