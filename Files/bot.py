import asyncio
import json
import os

from aiogram import F, Bot, types, Router, Dispatcher
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup, FSInputFile, Message
from aiogram.filters import Command, BaseFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from aiohttp import web

from request import (
    get_request_for_dots,
    post_request_media,
    post_request_location_and_description,
    get_request_urgent_message
)

from map import load_map


with open('../toc.json', 'r') as json_file:  # '/usr/src/app/Files/toc.json', 'r'
    config = json.load(json_file)
    TOKEN = config["token"]
    WEB_SERVER_HOST = config["server_host"]
    WEBHOOK_PATH = config["webhook_path"]
    WEBHOOK_URL = config["webhook_url"]

router = Router()

with open('../base/data_for_mess.json', 'r') as json_file:  # '/usr/src/app/base/data_for_mess.json', 'r'
    mes_data = json.load(json_file)

with open('../base/data_for_recognize.json', 'r') as json_file:  # '/usr/src/app/base/data_for_recognize.json', 'r'
    recognize_data = json.load(json_file)

all_type_actions = {
    "report_traffic_accident": "Дорожно-транспортные происшествия",
    "report_road_deficiencies": "Недостатки содержания дороги",
    "report_illegal_actions": "Противоправные действия 3-их лиц",
    "dangerous_situation": [
        "Куда звонить в экстренной ситуации?",
        "Угроза жизни и здоровья"],
    "recognize_meal": "Поесть",
    "recognize_gas_station": "Заправиться",
    "recognize_car_service": "Починить машину",
    "recognize_parking_lot": "Оставить машину",
    "recognize_attractions": "Интересные места"
}
callback_area = ['chelyabinsk', 'kurgan']
callback_route = [
    'route_chelyabinsk_1',
    'route_chelyabinsk_2',
    'route_chelyabinsk_3',
    'route_chelyabinsk_4',
    'route_kurgan_1',
    'route_kurgan_2',
    'route_kurgan_3',
    'route_kurgan_4'
]
callback_route_for_post = ['М-5', 'А-310', 'Р-254', 'Р-354']
callback_type_road_deficiencies = [
        "Проломы, ямы, выбоины",
        "Трещины",
        "Гололёд",
        "Проблемы с разметкой"
    ]
callback_continue_or_return = ['continue', 'return']

callback_map_for_meal = [f'location_meal_{i}' for i in range(10)]
callback_map_for_gas_station = [f'location_gas_station_{i}' for i in range(10)]
callback_map_for_car_service = [f'location_car_service_{i}' for i in range(10)]
callback_map_for_parking_lot = [f'location_parking_lot_{i}' for i in range(10)]
callback_map_for_attractions = [f'location_attractions_{i}' for i in range(10)]

callback_dangerous_situation = ['option_4', 'type_6']


class ProfileStatesGroup(StatesGroup):
    input_voice = State()
    go_to_road_deficiencies = State()

    input_description_for_illegal_actions = State()
    input_description_for_road_deficiencies = State()

    input_location_for_meal = State()
    input_location_for_gas_station = State()
    input_location_for_illegal_actions = State()
    input_location_for_road_deficiencies = State()
    input_location_for_car_service = State()
    input_location_for_parking_lot = State()
    input_location_for_attractions = State()

    input_photo_for_road_deficiencies = State()
    input_photo_for_illegal_actions = State()

    output_text_for_road_deficiencies = State()

    output_points_for_meal = State()
    output_points_for_gas_station = State()
    output_points_for_car_service = State()
    output_points_for_parking_lot = State()
    output_points_for_attractions = State()


class IsPhotoOrVideo(BaseFilter):
    def __init__(self) -> None:
        pass

    async def __call__(self, message: Message) -> bool:
        return message.photo is not None or message.video is not None


def get_route_mk(
        city: str,
        count: int
) -> InlineKeyboardBuilder:
    """
        Создаёт инлайн-клавиатуру по 1 кнопке в произвольном количестве рядов для конкретной области
        :city: область
        :count: количество рядов с кнопками
    """
    markup = InlineKeyboardBuilder()
    for i in range(count):
        btn = types.InlineKeyboardButton(
            text=mes_data[f'route_{city}'][i],
            callback_data=mes_data[f'route_callback_{city}'][i]
        )
        markup.row(btn)
    return markup


def types_deficiencies(
) -> InlineKeyboardBuilder:
    """
        Создаёт инлайн-клавиатуру с 9 кнопками по 5-ти рядам
        :purpose: цель использования для образования колбэков
    """
    markup = InlineKeyboardBuilder()
    for i in range(4):
        btn = types.InlineKeyboardButton(
            text=mes_data['type_road_deficiencies'][i],
            callback_data=mes_data['type_road_deficiencies'][i]
        )
        markup.add(btn)
    markup.adjust(1, 2, 1)
    return markup


def btn_to_send_loc() -> ReplyKeyboardMarkup:
    """
        Создаёт реплай-клавиатуру с кнопкой в один ряд для отправления локации
    """
    kb = [[types.KeyboardButton(text="Отправить нынешнюю локацию", request_location=True)]]
    markup = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder='Отправьте геолокацию')
    return markup


def return_to_start():
    kb = [[types.KeyboardButton(text="/start")]]
    markup = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        one_time_keyboard=True)
    return markup


@router.message(Command('start'))
async def choice_of_area(message: types.Message):
    markup = InlineKeyboardBuilder()
    btn1 = types.InlineKeyboardButton(text='Челябинская область', callback_data='chelyabinsk')
    btn2 = types.InlineKeyboardButton(text='Курганская область', callback_data='kurgan')
    markup.add(btn1, btn2)

    # btn1 = types.InlineKeyboardButton(text='Челябинская область', callback_data='chelyabinsk')
    # btn2 = types.InlineKeyboardButton(text='Курганская область', callback_data='kurgan')
    # btn3 = types.InlineKeyboardButton(text='Отправить голосовое сообщение', callback_data='voice')
    # markup.add(btn1, btn2, btn3)
    # markup.adjust(2, 1)
    await message.answer(
        text=mes_data['choice_of_area'],
        reply_markup=markup.as_markup()
    )


@router.callback_query(F.data.in_(callback_area))
async def route_choice(callback: types.CallbackQuery):
    if callback.data == 'chelyabinsk':
        await callback.message.answer(text='Челябинская область')
        await callback.message.answer(
            text=mes_data['route_choice'],
            reply_markup=get_route_mk(count=3, city='chelyabinsk').as_markup()
        )
    else:
        await callback.message.answer(text='Курганская область')
        await callback.message.answer(
            text=mes_data['route_choice'],
            reply_markup=get_route_mk(count=2, city='kurgan').as_markup()
        )


@router.callback_query(F.data.in_(callback_route_for_post))
async def route_for_post(callback: types.CallbackQuery, state: FSMContext):
    # сохраняем переменные
    await state.update_data({"route": callback.data})

    # внезапное сообщение
    # answer = await get_request_urgent_message(road_name=callback.data)
    answer = {
        'advertisements': [
            {
                'title': "Для всех дорог",
                'description': "Все хорошо"
            }
        ]
    }
    if not answer['advertisements']:
        await callback.message.answer(text=mes_data['good_situation'])
    else:
        count = len(answer['advertisements'])
        text = ''
        for i in range(count):
            title = answer['advertisements'][i]['title']
            message = answer['advertisements'][i]['description']
            text += f'{i + 1}. {title}\n{message}\n\n'
        await callback.message.answer(text)

    markup = InlineKeyboardBuilder()
    btn1 = types.InlineKeyboardButton(text='Сообщить', callback_data='report')
    btn2 = types.InlineKeyboardButton(text='Узнать', callback_data='recognize')
    markup.row(btn1, btn2)
    await callback.message.answer(
        text=mes_data['choose_action'],
        reply_markup=markup.as_markup()
    )


@router.callback_query(F.data == 'report')
async def choose_report(callback: types.CallbackQuery):
    markup = InlineKeyboardBuilder()
    for i in range(4):
        btn = types.InlineKeyboardButton(
            text=mes_data['choose_report'][i],
            callback_data=f'option_{i + 1}'
        )
        markup.row(btn)
    await callback.message.answer(
        text=mes_data['text_report'],
        reply_markup=markup.as_markup()
    )


# ветка с гс -----------------------------------------------
# @router.callback_query(F.data == 'voice')
# async def voice_requirements(callback: types.CallbackQuery, state: FSMContext):
#     await callback.message.answer(text=mes_data['voice_requirements'])
#     await state.set_state(ProfileStatesGroup.input_voice)
#
#
# @router.message(F.voice, ProfileStatesGroup.input_voice)
# async def voice_processing(message: types.Message, state: FSMContext, bot: Bot):
#     await bot.download(message.voice,  destination=f'{message.voice.file_id}.ogg')
#     # запрос для отправки гс на ии
#     skip_information = ['М-5', 'Дорожно-транспортные происшествия']  # полученный ответ
#     if skip_information[1] == all_type_actions['report_traffic_accident']:
#         await traffic_accident(message)
#     elif skip_information[1] == all_type_actions['report_road_deficiencies']:
#         await road_deficiencies()
#     elif skip_information[1] == all_type_actions['report_illegal_actions']:
#         await illegal_actions()
#     elif skip_information[1] == all_type_actions['dangerous_situation']:
#         await dangerous_situation()
#     elif skip_information[1] == all_type_actions['recognize_meal']:
#         await meal()
#     elif skip_information[1] == all_type_actions['recognize_gas_station']:
#         await gas_station()
#     elif skip_information[1] == all_type_actions['recognize_car_service']:
#         await car_service()
#     elif skip_information[1] == all_type_actions['recognize_parking_lot']:
#         await parking_lot()
#     elif skip_information[1] == all_type_actions['recognize_attractions']:
#         await attractions()
#     else:
#         await message.answer(text=mes_data['bad_situation'])
#         await state.set_state(ProfileStatesGroup.input_photo_for_illegal_actions)
#     os.remove(f'{message.voice.file_id}.ogg')


# -----------------------------------------------------------
@router.callback_query(F.data == 'option_1')
async def traffic_accident(message: types.Message):
    await message.answer(text=mes_data['traffic_accident'])
    await message.answer(
        text='Для повторного выбора нажмите /start',
        reply_markup=return_to_start()
    )


# ------------------------------------------------------
@router.callback_query(F.data == 'option_2')
async def road_deficiencies(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(text=mes_data['road_deficiencies'])
    await callback.message.answer(text=mes_data['locate_road_deficiencies'], reply_markup=btn_to_send_loc())
    await state.set_state(ProfileStatesGroup.input_location_for_road_deficiencies)  # вешаем статус ожидания геолокации


@router.message(
    F.location,
    ProfileStatesGroup.input_location_for_road_deficiencies
)
async def location_road_deficiencies(message: types.Message, state: FSMContext):
    longitude = message.location.longitude
    latitude = message.location.latitude
    # сохраняем переменные
    await state.update_data({"longitude": longitude})
    await state.update_data({"latitude": latitude})

    markup = types_deficiencies()
    await message.answer(
        text=mes_data['text_for_type_road_deficiencies'],
        reply_markup=markup.as_markup()
    )
    await state.set_state(ProfileStatesGroup.output_text_for_road_deficiencies)


@router.callback_query(
    F.data.in_(callback_type_road_deficiencies),
    ProfileStatesGroup.output_text_for_road_deficiencies
)
async def photo_road_deficiencies(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    route = data["route"]  # получение дороги
    longitude = data["longitude"]
    latitude = data["latitude"]

    # post запрос
    # list_road_deficiencies = await post_request_location_and_description(
    #     road_name=route,
    #     longitude=longitude,
    #     latitude=latitude,
    #     type_road='RoadDisadvantages',
    #     description=callback.message.text
    # )
    list_road_deficiencies = {"pointId": '349849547040'}
    # сохраняем id точки
    point_id_for_road_deficiencies = list_road_deficiencies['pointId']
    await state.update_data({"id_for_road_deficiencies": point_id_for_road_deficiencies})

    await callback.message.answer(text=mes_data['photo_road_deficiencies'])
    await state.set_state(ProfileStatesGroup.input_photo_for_road_deficiencies)  # вешаем cтатус ожидания фото


@router.message(
    F.photo,
    ProfileStatesGroup.input_photo_for_road_deficiencies
)
async def photo_road_deficiencies(
        message: types.Message,
        state: FSMContext,
        bot: Bot
):
    # получение id точки
    data = await state.get_data()
    point_id_for_road_deficiencies = data['id_for_road_deficiencies']

    await bot.download(message.photo[-1], destination=f'{message.photo[-1].file_id}.jpg')
    # post запрос
    # status = await post_request_media(
    #     file_id=message.photo[-1].file_id,
    #     point_id=point_id_for_road_deficiencies,
    #     type_media='jpg'
    # )
    status = True

    if status:
        await message.answer(
            mes_data['end_road_deficiencies'],
            reply_markup=return_to_start()
        )
        await state.clear()

    else:
        await message.answer(text=mes_data['bad_situation'])
        await state.set_state(ProfileStatesGroup.input_photo_for_road_deficiencies)
    os.remove(f'{message.photo[-1].file_id}.jpg')


# --------------------------------------------------------------------------------------------
@router.callback_query(F.data == 'option_3')
async def illegal_actions(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(text=mes_data['instructions_for_contact'])
    await callback.message.answer(text=mes_data['locate_road_deficiencies'], reply_markup=btn_to_send_loc())
    await state.set_state(ProfileStatesGroup.input_location_for_illegal_actions)


@router.message(
    F.location,
    ProfileStatesGroup.input_location_for_illegal_actions
)
async def input_description(message: types.Message, state: FSMContext):
    locate = [message.location.longitude, message.location.latitude]
    # сохранение id сообщения
    await state.update_data(locate=locate)

    await message.answer(text=mes_data['action_description'])
    await state.set_state(ProfileStatesGroup.input_description_for_illegal_actions)


@router.message(
    F.text,
    ProfileStatesGroup.input_description_for_illegal_actions
)
async def input_photo_or_video(message: types.Message, state: FSMContext):
    # получение дороги
    data = await state.get_data()
    route = data["route"]

    # получение id сообщения
    data = await state.get_data()
    locate = data["locate"]

    description = message.text
    longitude = locate[0]
    latitude = locate[1]
    # post запрос
    # post_result = await post_request_location_and_description(
    #     road_name=route,
    #     longitude=longitude,
    #     latitude=latitude,
    #     description=description,
    #     type_road='ThirdPartyIllegalActions'
    # )
    post_result = {"pointId": '3456u654'}

    point_id_for_illegal_actions = post_result['pointId']
    # сохранение id точки
    await state.update_data({"id_for_illegal_actions": point_id_for_illegal_actions})

    await message.answer(text=mes_data['media_of_illegal_actions'])
    await state.set_state(ProfileStatesGroup.input_photo_for_illegal_actions)


@router.message(
    IsPhotoOrVideo(),
    ProfileStatesGroup.input_photo_for_illegal_actions
)
async def input_photo_or_video(
        message: types.Message,
        state: FSMContext,
        bot: Bot
):
    # получение id сообщения
    data = await state.get_data()
    point_id_for_illegal_actions = data["id_for_illegal_actions"]

    if message.photo:
        await bot.download(message.photo[-1], destination=f'{message.photo[-1].file_id}.jpg')
        # обработка фото
        # status = await post_request_media(
        #     file_id=message.photo[-1].file_id,
        #     point_id=point_id_for_illegal_actions,
        #     type_media='jpg'
        # )
        status = True
        if status:
            await message.answer(
                mes_data['end_road_deficiencies'],
                reply_markup=return_to_start()
            )
            await state.clear()
        else:
            await message.answer(text=mes_data['bad_situation'])
            await state.set_state(ProfileStatesGroup.input_photo_for_illegal_actions)
        os.remove(f'{message.photo[-1].file_id}.jpg')

    elif message.video:
        await bot.download(message.video, destination=f'{message.video.file_id}.mp4')
        # обработка видео
        # status = await post_request_media(
        #     file_id=message.video.file_id,
        #     point_id=point_id_for_illegal_actions,
        #     type_media='mp4'
        # )
        status = True
        if status:
            await message.answer(
                mes_data['end_road_deficiencies'],
                reply_markup=return_to_start()
            )
            await state.clear()
        else:
            await message.answer(text=mes_data['bad_situation'])
            await state.set_state(ProfileStatesGroup.input_photo_for_illegal_actions)
        os.remove(f'{message.video.file_id}.mp4')

    await state.clear()


# ---------------------------------------------------------------------------------------------
@router.callback_query(F.data == 'recognize')
async def choose_que(callback: types.CallbackQuery):
    markup = InlineKeyboardBuilder()
    for i in range(6):
        btn = types.InlineKeyboardButton(
            text=recognize_data['questions_for_recognize'][i],
            callback_data=f'type_{i + 1}'
        )
        markup.row(btn)
    await callback.message.answer(
        text=recognize_data['recognize'],
        reply_markup=markup.as_markup()
    )


# Точки с едой (meal) -----------------------------------------------------------------
@router.callback_query(F.data == 'type_1')
async def meal(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(text=recognize_data['start_and_send_location'], reply_markup=btn_to_send_loc())
    await state.set_state(ProfileStatesGroup.input_location_for_meal)  # вешаем статус ожидания геолокации


@router.message(
    F.location,
    ProfileStatesGroup.input_location_for_meal
)
async def choose_meal(message: types.Message, state: FSMContext):
    longitude = message.location.longitude
    latitude = message.location.latitude

    # получение дороги
    data = await state.get_data()
    route = data["route"]

    # запрос геолокаци мест с едой
    # list_meal = await get_request_for_dots(
    #     road_name=route,
    #     longitude=longitude,
    #     latitude=latitude,
    #     point_type='Cafe'
    # )
    list_meal = {
        'points': [
            {
                'name': 'Точка 1',
                'coordinates': {
                    'longitude': 61.389596,
                    'latitude': 55.179907
                }
            },
            {
                'name': 'Точка 2',
                'coordinates': {
                    'longitude': 61.295911,
                    'latitude': 55.219387
                }
            },
        ],
        'distancesFromUser': [
            13,
            12
        ]
    }

    count = len(list_meal['points'])  # сколько пришло точек

    text = ''
    for i in range(count):
        name_meal = list_meal['points'][i]['name']
        distance_meal = round(list_meal['distancesFromUser'][i], 2)
        text += f"{i + 1}. {name_meal} : {distance_meal}км. от вас\n"
    await message.answer(text=text)

    # вывод карты
    if not list_meal:
        await message.answer('К сожалению ближайших к вам точек нет')
    else:
        load_map(longitude=longitude, latitude=latitude, list_dots=list_meal, color='rd')
        file = FSInputFile('map.png')
        await message.answer_photo(file)
        os.remove('map.png')

    await message.answer(
        text='Для просмотра других точек нажмите /start',
        reply_markup=return_to_start()
    )
    await state.clear()


# АЗС (type_2) -------------------------------------------------------------------------------------------
@router.callback_query(F.data == 'type_2')
async def gas_station(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(text=recognize_data['start_and_send_location'], reply_markup=btn_to_send_loc())
    await state.set_state(ProfileStatesGroup.input_location_for_gas_station)  # вешаем статус ожидания геолокации


@router.message(
    F.location,
    ProfileStatesGroup.input_location_for_gas_station
)
async def choose_gas_station(message: types.Message, state: FSMContext):
    # запрос геолокаци заправок
    longitude = message.location.longitude
    latitude = message.location.latitude

    # получение дороги
    data = await state.get_data()
    route = data["route"]

    # list_gas_station = await get_request_for_dots(
    #     road_name=route,
    #     longitude=longitude,
    #     latitude=latitude,
    #     point_type='GasStation'
    # )
    list_gas_station = {
        'points': [
            {
                'name': 'Точка 1',
                'coordinates': {
                    'longitude': 61.389596,
                    'latitude': 55.179907
                }
            },
            {
                'name': 'Точка 2',
                'coordinates': {
                    'longitude': 61.295911,
                    'latitude': 55.219387
                }
            },
        ],
        'distancesFromUser': [
            13,
            12
        ]
    }

    count = len(list_gas_station['points'])  # сколько пришло точек

    text = ''
    for i in range(count):
        name_gas_station = list_gas_station['points'][i]['name']
        distance_gas_station = round(list_gas_station['distancesFromUser'][i], 2)
        text += f"{i + 1}. {name_gas_station} : {distance_gas_station}км. от вас\n"
    await message.answer(text=text)

    # вывод карты
    if not list_gas_station:
        await message.answer('К сожалению ближайших к вам точек нет')
    else:
        load_map(longitude=longitude, latitude=latitude, list_dots=list_gas_station, color='nt')
        file = FSInputFile('map.png')
        await message.answer_photo(file)
        os.remove('map.png')

    await message.answer(
        text='Для просмотра других точек нажмите /start',
        reply_markup=return_to_start()
    )
    await state.clear()


# Точки с автосервисами (type_3) ---------------------------------------------------------
@router.callback_query(F.data == 'type_3')
async def car_service(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(text=recognize_data['start_and_send_location'], reply_markup=btn_to_send_loc())
    await state.set_state(ProfileStatesGroup.input_location_for_car_service)  # вешаем статус ожидания геолокации


@router.message(
    F.location,
    ProfileStatesGroup.input_location_for_car_service
)
async def choose_car_service(message: types.Message, state: FSMContext):
    longitude = message.location.longitude
    latitude = message.location.latitude

    # получение дороги
    data = await state.get_data()
    route = data["route"]

    # запрос геолокаци мест с автосервисов
    # list_car_service = await get_request_for_dots(
    #     road_name=route,
    #     longitude=longitude,
    #     latitude=latitude,
    #     point_type='CarService'
    # )
    list_car_service = {
        'points': [
            {
                'name': 'Точка 1',
                'coordinates': {
                    'longitude': 61.389596,
                    'latitude': 55.179907
                }
            },
            {
                'name': 'Точка 2',
                'coordinates': {
                    'longitude': 61.295911,
                    'latitude': 55.219387
                }
            },
        ],
        'distancesFromUser': [
            13,
            12
        ]
    }

    count = len(list_car_service['points'])  # сколько пришло точек

    text = ''
    for i in range(count):
        name_car_service = list_car_service['points'][i]['name']
        distance_car_service = round(list_car_service['distancesFromUser'][i], 2)
        text += f"{i + 1}. {name_car_service} : {distance_car_service}км. от вас\n"
    await message.answer(text=text)

    # вывод карты
    if not list_car_service:
        await message.answer('К сожалению ближайших к вам точек нет')
    else:
        load_map(longitude=longitude, latitude=latitude, list_dots=list_car_service, color='dg')
        file = FSInputFile('map.png')
        await message.answer_photo(file)
        os.remove('map.png')

    await message.answer(
        text='Для просмотра других точек нажмите /start',
        reply_markup=return_to_start()
    )
    await state.clear()


# Точки с временной парковкой (type_4) ----------------------------------------------------------------
@router.callback_query(F.data == 'type_4')
async def parking_lot(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(text=recognize_data['start_and_send_location'], reply_markup=btn_to_send_loc())
    await state.set_state(ProfileStatesGroup.input_location_for_parking_lot)  # вешаем статус ожидания геолокации


@router.message(F.location, ProfileStatesGroup.input_location_for_parking_lot)
async def choose_parking_lot(message: types.Message, state: FSMContext):
    longitude = message.location.longitude
    latitude = message.location.latitude

    # получение дороги
    data = await state.get_data()
    route = data["route"]

    # запрос геолокаци мест с парковкой
    # list_parking_lot = await get_request_for_dots(
    #     road_name=route,
    #     longitude=longitude,
    #     latitude=latitude,
    #     point_type='RestPlace'
    # )
    list_parking_lot = {
        'points': [
            {
                'name': 'Точка 1',
                'coordinates': {
                    'longitude': 61.389596,
                    'latitude': 55.179907
                }
            },
            {
                'name': 'Точка 2',
                'coordinates': {
                    'longitude': 61.295911,
                    'latitude': 55.219387
                }
            },
        ],
        'distancesFromUser': [
            13,
            12
        ]
    }

    count = len(list_parking_lot['points'])  # сколько пришло точек

    text = ''
    for i in range(count):
        name_parking_lot = list_parking_lot['points'][i]['name']
        distance_parking_lot = round(list_parking_lot['distancesFromUser'][i], 2)
        text += f"{i + 1}. {name_parking_lot} : {distance_parking_lot}км. от вас\n"
    await message.answer(text=text)

    # вывод карты
    if not list_parking_lot:
        await message.answer('К сожалению ближайших к вам точек нет')
    else:
        load_map(longitude=longitude, latitude=latitude, list_dots=list_parking_lot, color='vv')
        file = FSInputFile('map.png')
        await message.answer_photo(file)
        os.remove('map.png')

    await message.answer(
        text='Для просмотра других точек нажмите /start',
        reply_markup=return_to_start()
    )
    await state.clear()


# Точки с достопримечательностями (type_5) ------------------------------------------------------------
@router.callback_query(F.data == 'type_5')
async def attractions(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(text=recognize_data['start_and_send_location'], reply_markup=btn_to_send_loc())
    await state.set_state(ProfileStatesGroup.input_location_for_attractions)  # вешаем статус ожидания геолокации


@router.message(F.location, ProfileStatesGroup.input_location_for_attractions)
async def choose_attractions(message: types.Message, state: FSMContext):
    longitude = message.location.longitude
    latitude = message.location.latitude

    # получение дороги
    data = await state.get_data()
    route = data["route"]

    # запрос геолокаци мест с достопримечательностями
    # list_attractions = await get_request_for_dots(
    #     road_name=route,
    #     longitude=longitude,
    #     latitude=latitude,
    #     point_type='InterestingPlace'
    # )
    list_attractions = {
        'points': [
            {
                'name': 'Точка 1',
                'coordinates': {
                    'longitude': 61.389596,
                    'latitude': 55.179907
                }
            },
            {
                'name': 'Точка 2',
                'coordinates': {
                    'longitude': 61.295911,
                    'latitude': 55.219387
                }
            },
        ],
        'distancesFromUser': [
            13,
            12
        ]
    }

    count = len(list_attractions['points'])  # сколько пришло точек

    text = ''
    for i in range(count):
        name_attractions = list_attractions['points'][i]['name']
        distance_attractions = round(list_attractions['distancesFromUser'][i], 2)
        text += f"{i + 1}. {name_attractions} : {distance_attractions}км. от вас\n"
    await message.answer(text=text)
    # вывод карты
    if not list_attractions:
        await message.answer('К сожалению ближайших к вам точек нет')
    else:
        load_map(longitude=longitude, latitude=latitude, list_dots=list_attractions, color='or')
        file = FSInputFile('map.png')
        await message.answer_photo(file)
        os.remove('map.png')

    await message.answer(
        text='Для просмотра других точек нажмите /start',
        reply_markup=return_to_start()
    )
    await state.clear()


# Экстренная ситуация(type_6 / option_4) ------------------------------------------------------------------
@router.callback_query(F.data.in_(callback_dangerous_situation))
async def dangerous_situation(callback: types.CallbackQuery):
    await callback.message.answer(
        text=mes_data['dangerous_situation'],
        reply_markup=return_to_start()
    )


# ------------------------------------------------------------------------------------------------------
async def on_startup(bot: Bot) -> None:
    await bot.set_webhook(f"{WEBHOOK_URL}{WEBHOOK_PATH}")


async def main() -> None:
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    dp.include_router(router)

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
