# общие импорты
import asyncio
import json
import os
import logging

# импорты из библиотеки aiogram
from aiogram import F, Bot, types, Router, Dispatcher
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import FSInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

# импорты из библиотеки aiohttp
from aiohttp import web

# импорты из библиотеки pydub
from pydub import AudioSegment

# импорты из файла request.py
from request import (
    get_road_and_region,
    get_request_for_dots,
    post_request_media,
    post_request_location_and_description,
    get_request_urgent_message,
    get_advertisements_for_region
)

# импорты из файла support_function.py
from support_function import (
    return_to_start,
    btn_to_send_loc,
    concate_files
)

# импорты из файла map.py
from map import load_map
from filters.IsPhotoOrVideo import IsPhotoOrVideo
from filters.States import ProfileStatesGroup
# ngrok config add-authtoken 2eARc5NIQJFH6vmqpMvM56DyFya_3JP6riD9tNJ3WWs7R2suH
# ngrok http --domain=hookworm-picked-needlessly.ngrok-free.app 8080

router = Router()
# .. -> /usr/src/app/
with open(r'/usr/src/app/config.json', 'r') as json_file:
    config = json.load(json_file)
    TOKEN = config["token"]
    WEB_SERVER_HOST = config["server_host"]
    WEBHOOK_PATH = config["webhook_path"]
    WEBHOOK_URL = config["webhook_url"]

with open(r'/usr/src/app/recurses/text_for_message/data_for_mess.json',
          'r') as data_for_mess:
    mes_data = json.load(data_for_mess)

with open(r'/usr/src/app/recurses/text_for_message/data_for_recognize.json',
          'r') as data_for_recognize:
    recognize_data = json.load(data_for_recognize)

with open(r'/usr/src/app/recurses/text_for_message/callback_data.json',
          'r') as callback_mes_data:
    callback_data = json.load(callback_mes_data)


@router.message(Command('start'))
async def start(message: types.Message, state: FSMContext):
    await message.answer(text=mes_data['start_talk'], reply_markup=btn_to_send_loc())
    await state.set_state(ProfileStatesGroup.input_location)


@router.message(
        F.location,
        ProfileStatesGroup.input_location
    )
async def location_confirmation(message: types.Message, state: FSMContext):
    if message.reply_to_message is None:
        print('Самостоятельно отправленная локация')
        await state.update_data({"reliability_level": 2})
    else:
        print('Локация через кнопку')
        await state.update_data({"reliability_level": 1})
    longitude = message.location.longitude
    latitude = message.location.latitude
    # сохраняем локацию
    await state.update_data({"longitude": longitude})
    await state.update_data({"latitude": latitude})

    # запрос на бэк для получения области и дороги
    answer = await get_road_and_region(
        longitude=longitude,
        latitude=latitude
    )
    print(answer)
    if not answer['roadName'] and not answer['regionName']:
        await message.answer('Вы слишком далеко от киллометрового столба. Попробуйте еще раз позже')
        await state.set_state(ProfileStatesGroup.input_location)
        return
    # сохраняем место
    await state.update_data({"road": answer['roadName']})
    await state.update_data({"region": answer['regionName']})

    # кнопки да/нет
    markup = InlineKeyboardBuilder()
    btn_1 = types.InlineKeyboardButton(text='Да', callback_data='yes')
    btn_2 = types.InlineKeyboardButton(text='Нет', callback_data='no')
    markup.add(btn_1, btn_2)
    markup.adjust(2)

    text = f"Вы находитесь на дороге {answer['roadName']} в {answer['regionName']}. Верно?"
    await message.answer(text=text, reply_markup=markup.as_markup())
    await state.set_state(ProfileStatesGroup.text_or_voice)


@router.callback_query(
    F.data == 'no',
    ProfileStatesGroup.text_or_voice
)
async def retry_send_location(callback: types.CallbackQuery, state: FSMContext):
    print(callback)
    await callback.message.answer(
        text='Попробуйте еще раз отправить локацию',
        reply_markup=btn_to_send_loc()
    )
    await state.set_state(ProfileStatesGroup.input_location)


@router.callback_query(
    F.data == 'yes',
    ProfileStatesGroup.text_or_voice
)
async def text_or_voice(callback: types.CallbackQuery, state: FSMContext):
    markup = InlineKeyboardBuilder()
    btn_1 = types.InlineKeyboardButton(text='Продолжить в текстовом формате', callback_data='text')
    btn_2 = types.InlineKeyboardButton(text='Отправить голосовое сообщение', callback_data='voice')
    markup.add(btn_1, btn_2)
    markup.adjust(1, 1)
    await callback.message.answer(
        text=mes_data['text_or_voice'],
        reply_markup=markup.as_markup()
    )
    await state.set_state(ProfileStatesGroup.advertisements)


@router.callback_query(
    F.data == 'text',
    ProfileStatesGroup.advertisements
)
async def regional_advertisements(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    route = data["road"]
    region = data["region"]

    # запрос на обьяления по области
    request_advertisements = await get_advertisements_for_region(region_name=region)
    if len(request_advertisements['advertisements']) == 0:
        await callback.message.answer(text=mes_data['good_situation'])
    else:
        print(request_advertisements)
        count = len(request_advertisements['advertisements'])
        text = ''
        for i in range(count):
            title = request_advertisements['advertisements'][i]['title']
            message = request_advertisements['advertisements'][i]['description']
            text += f'{i + 1}. {title}\n{message}\n\n'
        await callback.message.answer(text)
        # озвучка
        audio = AudioSegment.empty()
        flag = False
        flag, audio = await concate_files(
            count, request_advertisements, callback.from_user.id, flag, audio
        )

        if flag:
            res_path = f"res-{callback.from_user.id}.ogg"
            audio.export(res_path, format="ogg")
            audio = FSInputFile(path=res_path)
            await callback.message.answer_audio(
                audio=audio,
                caption="⚡️⚡️⚡️ Новости ⚡️⚡️⚡️",
            )
            os.remove(res_path)

    # обьявление для дороги
    answer = await get_request_urgent_message(road_name=route)
    if len(answer['advertisements']) == 0:
        await callback.message.answer(text=mes_data['good_situation'])
    else:
        print(answer)
        count = len(answer['advertisements'])
        text = ''
        for i in range(count):
            title = answer['advertisements'][i]['title']
            message = answer['advertisements'][i]['description']
            text += f'{i + 1}. {title}\n{message}\n\n'
        await callback.message.answer(text)
        # озвучка
        audio = AudioSegment.empty()
        flag, audio = await concate_files(
            count, answer, callback.from_user.id, False, audio
        )

        if flag:
            res_path = f"res-{callback.from_user.id}.ogg"
            audio.export(res_path, format="ogg")
            audio = FSInputFile(path=res_path)
            await callback.message.answer_audio(
                audio=audio,
                caption="⚡️⚡️⚡️ Новости⚡️⚡️⚡️",
            )
            os.remove(res_path)

    markup = InlineKeyboardBuilder()
    btn1 = types.InlineKeyboardButton(text='Сообщить', callback_data='report')
    btn2 = types.InlineKeyboardButton(text='Узнать', callback_data='recognize')
    markup.row(btn1, btn2)
    await callback.message.answer(
        text=mes_data['choose_action'],
        reply_markup=markup.as_markup()
    )
    await state.set_state(ProfileStatesGroup.report_or_recognize)


@router.callback_query(
    F.data == 'report',
    ProfileStatesGroup.report_or_recognize
)
async def choose_report(callback: types.CallbackQuery, state: FSMContext):
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
    await state.set_state(ProfileStatesGroup.report)


# ветка с гс -----------------------------------------------
@router.callback_query(F.data == 'voice', ProfileStatesGroup.advertisements)
async def voice_requirements(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(text=mes_data['voice_requirements'])
    await state.set_state(ProfileStatesGroup.input_voice)


@router.message(F.voice, ProfileStatesGroup.input_voice)
async def voice_processing(message: types.Message, state: FSMContext, bot: Bot):
    await bot.download(message.voice, destination=f'{message.voice.file_id}.ogg')
    await state.update_data({"file_name": f'{message.voice.file_id}.ogg'})

    # запрос для отправки гс на ии
    skip_information = ['АЗС']  # полученный ответ
    await state.update_data({"to_do": skip_information[0]})

    text = f'Вы хотите перейти к действию под названием: {skip_information[0]}. Верно?'
    markup = InlineKeyboardBuilder()
    btn_1 = types.InlineKeyboardButton(text='Да', callback_data='voice_good')
    btn_2 = types.InlineKeyboardButton(text='Нет', callback_data='voice_bad')
    markup.add(btn_1, btn_2)
    markup.adjust(2)

    await message.answer(text=text, reply_markup=markup.as_markup())
    await state.set_state(ProfileStatesGroup.voice_right_or_not)


@router.callback_query(F.data == 'voice_bad', ProfileStatesGroup.voice_right_or_not)
async def voice_bad(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer('Попробуйте отправить голосовое сообщение еще раз')
    await state.set_state(ProfileStatesGroup.input_voice)


@router.callback_query(F.data == 'voice_good', ProfileStatesGroup.voice_right_or_not)
async def voice_good(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    to_do = data['to_do']
    file_name = data['file_name']

    if to_do == callback_data['all_type_actions']['report_traffic_accident']:
        await traffic_accident(
            callback=callback,
            state=state
        )
        await state.set_state(ProfileStatesGroup.input_description_for_traffic_accident)
    elif to_do == callback_data['all_type_actions']['report_road_deficiencies']:
        await road_deficiencies(
            callback=callback,
            state=state
        )
        await state.set_state(ProfileStatesGroup.output_text_for_road_deficiencies)

    elif to_do == callback_data['all_type_actions']['report_illegal_actions']:
        await illegal_actions(
            callback=callback,
            state=state
        )
        await state.set_state(ProfileStatesGroup.input_description_for_illegal_actions)
    elif to_do == callback_data['all_type_actions']['report_road_block']:
        await road_block(
            callback=callback,
            state=state
        )
        await state.set_state(ProfileStatesGroup.input_description_for_road_block)
    elif to_do == callback_data['all_type_actions']['recognize_meal']:
        await meal(
            callback=callback,
            state=state
        )
        await state.set_state(ProfileStatesGroup.recognize)
    elif to_do == callback_data['all_type_actions']['recognize_gas_station']:
        await gas_station(
            callback=callback,
            state=state
        )
        await state.set_state(ProfileStatesGroup.recognize)
    elif to_do == callback_data['all_type_actions']['recognize_car_service']:
        await car_service(
            callback=callback,
            state=state
        )
        await state.set_state(ProfileStatesGroup.recognize)
    elif to_do == callback_data['all_type_actions']['recognize_parking_lot']:
        await parking_lot(
            callback=callback,
            state=state
        )
        await state.set_state(ProfileStatesGroup.recognize)
    elif to_do == callback_data['all_type_actions']['recognize_attractions']:
        await attractions(
            callback=callback,
            state=state
        )
        await state.set_state(ProfileStatesGroup.recognize)
    elif to_do == callback_data['all_type_actions']['recognize_dangerous_situation']:
        await dangerous_situation(callback)
        await state.set_state(ProfileStatesGroup.report)
    else:
        await callback.message.answer(text=mes_data['bad_situation'])
        await state.set_state(ProfileStatesGroup.input_voice)
    os.remove(file_name)
    print(f"voice_good: Current state: {await state.get_state()}")


# -----------------------------------------------------------
@router.callback_query(F.data == 'option_1', ProfileStatesGroup.report)
async def traffic_accident(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(text=mes_data['traffic_accident'])
    await state.set_state(ProfileStatesGroup.input_description_for_traffic_accident)


@router.message(
    F.text,
    ProfileStatesGroup.input_description_for_traffic_accident
)
async def description_for_traffic_accident(message: types.Message, state: FSMContext):
    data = await state.get_data()
    route = data["road"]  # получение дороги
    longitude = data["longitude"]
    latitude = data["latitude"]
    level = data["reliability_level"]

    request = await post_request_location_and_description(
        road_name=route,
        longitude=longitude,
        latitude=latitude,
        type_road=0,  # RoadAccident = 0
        description=message.text,
        level=level
    )

    if request:
        await message.answer(mes_data['end_road_deficiencies'])
        await message.answer(
            text='Для повторного выбора нажмите /start',
            reply_markup=return_to_start()
        )
        await state.clear()
    else:
        await message.answer(mes_data['bad_situation'])
        await state.clear()


# ------------------------------------------------------
@router.callback_query(F.data == 'option_2', ProfileStatesGroup.report)
async def road_deficiencies(
        callback: types.CallbackQuery,
        state: FSMContext
):
    await callback.message.answer(text=mes_data['road_deficiencies'])

    markup = InlineKeyboardBuilder()
    for i in range(4):
        btn = types.InlineKeyboardButton(
            text=mes_data['type_road_deficiencies'][i],
            callback_data=mes_data['type_road_deficiencies'][i]
        )
        markup.add(btn)
        print(mes_data['type_road_deficiencies'][i])
    markup.adjust(1, 2, 1)

    await callback.message.answer(
        text=mes_data['text_for_type_road_deficiencies'],
        reply_markup=markup.as_markup()
    )
    await state.set_state(ProfileStatesGroup.output_text_for_road_deficiencies)
    print(f"road_deficiencies: Current state: {await state.get_state()}")


@router.callback_query(
    F.data.in_(callback_data['callback_type_road_deficiencies']),
    ProfileStatesGroup.output_text_for_road_deficiencies
)
async def photo_road_deficiencies(callback: types.CallbackQuery, state: FSMContext):
    print(f"photo_road_deficiencies: Current state: {await state.get_state()}")
    print(f"photo_road_deficiencies: Callback data: {callback.data}")

    data = await state.get_data()
    route = data["road"]  # получение дороги
    longitude = data["longitude"]
    latitude = data["latitude"]
    level = data["reliability_level"]

    # post запрос
    list_road_deficiencies = await post_request_location_and_description(
        road_name=route,
        longitude=longitude,
        latitude=latitude,
        type_road=1,
        description=callback.data,
        level=level
    )
    print(list_road_deficiencies)
    # сохраняем id точки
    point_id_for_road_deficiencies = list_road_deficiencies['pointId']
    await state.update_data({"id_for_road_deficiencies": point_id_for_road_deficiencies})

    await callback.message.answer(text=mes_data['photo_road_deficiencies'])
    await state.set_state(ProfileStatesGroup.input_photo_for_road_deficiencies)


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
    status = await post_request_media(
        file_id=message.photo[-1].file_id,
        point_id=point_id_for_road_deficiencies,
        type_media='jpg'
    )

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
@router.callback_query(F.data == 'option_3', ProfileStatesGroup.report)
async def illegal_actions(
        callback: types.CallbackQuery,
        state: FSMContext
):
    await callback.message.answer(text=mes_data['instructions_for_contact'])

    await callback.message.answer(text=mes_data['action_description'])
    await state.set_state(ProfileStatesGroup.input_description_for_illegal_actions)


@router.message(
    F.text,
    ProfileStatesGroup.input_description_for_illegal_actions
)
async def input_photo_or_video(message: types.Message, state: FSMContext):
    # получение иформации
    data = await state.get_data()

    route = data["road"]
    description = message.text
    longitude = data["longitude"]
    latitude = data["latitude"]
    level = data["reliability_level"]

    # post запрос
    post_result = await post_request_location_and_description(
        road_name=route,
        longitude=longitude,
        latitude=latitude,
        description=description,
        type_road=3,
        level=level
    )
    print(post_result)
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
        status = await post_request_media(
            file_id=message.photo[-1].file_id,
            point_id=point_id_for_illegal_actions,
            type_media='jpg'
        )
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
        status = await post_request_media(
            file_id=message.video.file_id,
            point_id=point_id_for_illegal_actions,
            type_media='mp4'
        )
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


# -------------------------------------------------------------------------------------

@router.callback_query(F.data == 'option_4', ProfileStatesGroup.report)
async def road_block(
        callback: types.CallbackQuery,
        state: FSMContext
):
    await callback.message.answer(text=mes_data['traffic_accident'])
    await state.set_state(ProfileStatesGroup.input_description_for_road_block)


@router.message(
    F.text,
    ProfileStatesGroup.input_description_for_road_block
)
async def description_for_traffic_accident(message: types.Message, state: FSMContext):
    data = await state.get_data()
    route = data["road"]  # получение дороги
    longitude = data["longitude"]
    latitude = data["latitude"]
    level = data["reliability_level"]

    request = await post_request_location_and_description(
        road_name=route,
        longitude=longitude,
        latitude=latitude,
        type_road=2,  # RoadBlock = 2
        description=message.text,
        level=level
    )

    if request:
        await message.answer(mes_data['end_road_deficiencies'])
        await message.answer(
            text='Для повторного выбора нажмите /start',
            reply_markup=return_to_start()
        )
        await state.clear()
    else:
        await message.answer(mes_data['bad_situation'])
        await state.clear()


# ---------------------------------------------------------------------------------------------
@router.callback_query(
    F.data == 'recognize',
    ProfileStatesGroup.report_or_recognize
)
async def choose_que(callback: types.CallbackQuery, state: FSMContext):
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
    await state.set_state(ProfileStatesGroup.recognize)


# Точки с едой (meal) -----------------------------------------------------------------
@router.callback_query(
    F.data == 'type_1',
    ProfileStatesGroup.recognize
)
async def meal(
        callback: types.CallbackQuery,
        state: FSMContext
):
    # получение дороги
    data = await state.get_data()
    route = data["road"]
    longitude = data["longitude"]
    latitude = data["latitude"]

    # запрос геолокаци мест с едой
    list_meal = await get_request_for_dots(
        road_name=route,
        longitude=longitude,
        latitude=latitude,
        point_type='Cafe'
    )

    count = len(list_meal['points'])  # сколько пришло точек
    if count == 0:
        await callback.message.answer('К сожалению ближайших к вам точек нет')
        return

    text = ''
    for i in range(count):
        name_meal = list_meal['points'][i]['name']
        distance_meal = round(list_meal['points'][i]['distanceFromUser'], 2)
        text += f"{i + 1}. {name_meal} : {distance_meal}км. от вас\n"
    await callback.message.answer(text=text)

    # вывод карты
    load_map(longitude=longitude, latitude=latitude, list_dots=list_meal, color='rd')
    file = FSInputFile('map.png')
    await callback.message.answer_photo(file)
    os.remove('map.png')

    await callback.message.answer(
        text='Для просмотра других точек нажмите /start',
        reply_markup=return_to_start()
    )
    await state.clear()


# АЗС (type_2) -------------------------------------------------------------------------------------------
@router.callback_query(
    F.data == 'type_2',
    ProfileStatesGroup.recognize
    )
async def gas_station(
        callback: types.CallbackQuery,
        state: FSMContext
):
    # получение дороги
    data = await state.get_data()
    route = data["road"]
    longitude = data["longitude"]
    latitude = data["latitude"]

    list_gas_station = await get_request_for_dots(
        road_name=route,
        longitude=longitude,
        latitude=latitude,
        point_type='GasStation'
    )

    count = len(list_gas_station['points'])  # сколько пришло точек
    if count == 0:
        await callback.message.answer('К сожалению ближайших к вам точек нет')
        return

    text = ''
    for i in range(count):
        name_gas_station = list_gas_station['points'][i]['name']
        distance_gas_station = round(list_gas_station['points'][i]['distanceFromUser'], 2)
        text += f"{i + 1}. {name_gas_station} : {distance_gas_station}км. от вас\n"
    await callback.message.answer(text=text)

    # вывод карты
    load_map(longitude=longitude, latitude=latitude, list_dots=list_gas_station, color='nt')
    file = FSInputFile('map.png')
    await callback.message.answer_photo(file)
    os.remove('map.png')

    await callback.message.answer(
        text='Для просмотра других точек нажмите /start',
        reply_markup=return_to_start()
    )
    await state.clear()


# Точки с автосервисами (type_3) ---------------------------------------------------------
@router.callback_query(
    F.data == 'type_3',
    ProfileStatesGroup.recognize
)
async def car_service(
        callback: types.CallbackQuery,
        state: FSMContext
):
    # получение дороги
    data = await state.get_data()
    route = data["road"]
    longitude = data["longitude"]
    latitude = data["latitude"]

    # запрос геолокаци мест с автосервисов
    list_car_service = await get_request_for_dots(
        road_name=route,
        longitude=longitude,
        latitude=latitude,
        point_type='CarService'
    )

    count = len(list_car_service['points'])  # сколько пришло точек
    if count == 0:
        await callback.message.answer('К сожалению ближайших к вам точек нет')
        return

    text = ''
    for i in range(count):
        name_car_service = list_car_service['points'][i]['name']
        distance_car_service = round(list_car_service['points'][i]['distanceFromUser'], 2)
        text += f"{i + 1}. {name_car_service} : {distance_car_service}км. от вас\n"
    await callback.message.answer(text=text)

    # вывод карты
    load_map(longitude=longitude, latitude=latitude, list_dots=list_car_service, color='dg')
    file = FSInputFile('map.png')
    await callback.message.answer_photo(file)
    os.remove('map.png')

    await callback.message.answer(
        text='Для просмотра других точек нажмите /start',
        reply_markup=return_to_start()
    )
    await state.clear()


# Точки с временной парковкой (type_4) ----------------------------------------------------------------
@router.callback_query(
    F.data == 'type_4',
    ProfileStatesGroup.recognize
)
async def parking_lot(
        callback: types.CallbackQuery,
        state: FSMContext
):
    # получение дороги
    data = await state.get_data()
    route = data["road"]
    longitude = data["longitude"]
    latitude = data["latitude"]

    # запрос геолокаци мест с парковкой
    list_parking_lot = await get_request_for_dots(
        road_name=route,
        longitude=longitude,
        latitude=latitude,
        point_type='Hotel'
    )

    count = len(list_parking_lot['points'])  # сколько пришло точек
    if count == 0:
        await callback.message.answer('К сожалению ближайших к вам точек нет')
        return

    text = ''
    for i in range(count):
        name_parking_lot = list_parking_lot['points'][i]['name']
        distance_parking_lot = round(list_parking_lot['points'][i]['distanceFromUser'], 2)
        text += f"{i + 1}. {name_parking_lot} : {distance_parking_lot}км. от вас\n"
    await callback.message.answer(text=text)

    # вывод карты
    load_map(longitude=longitude, latitude=latitude, list_dots=list_parking_lot, color='vv')
    file = FSInputFile('map.png')
    await callback.message.answer_photo(file)
    os.remove('map.png')

    await callback.message.answer(
        text='Для просмотра других точек нажмите /start',
        reply_markup=return_to_start()
    )
    await state.clear()


# Точки с достопримечательностями (type_5) ------------------------------------------------------------
@router.callback_query(
    F.data == 'type_5',
    ProfileStatesGroup.recognize
)
async def attractions(
        callback: types.CallbackQuery,
        state: FSMContext
):
    # получение дороги
    data = await state.get_data()
    route = data["road"]
    longitude = data["longitude"]
    latitude = data["latitude"]

    # запрос геолокаци мест с достопримечательностями
    list_attractions = await get_request_for_dots(
        road_name=route,
        longitude=longitude,
        latitude=latitude,
        point_type='Event'
    )

    count = len(list_attractions['points'])  # сколько пришло точек
    if count == 0:
        await callback.message.answer('К сожалению ближайших к вам точек нет')
        return

    text = ''
    for i in range(count):
        name_attractions = list_attractions['points'][i]['name']
        distance_attractions = round(list_attractions['points'][i]['distanceFromUser'], 2)
        text += f"{i + 1}. {name_attractions} : {distance_attractions}км. от вас\n"
    await callback.message.answer(text=text)

    # вывод карты
    load_map(longitude=longitude, latitude=latitude, list_dots=list_attractions, color='or')
    file = FSInputFile('map.png')
    await callback.message.answer_photo(file)
    os.remove('map.png')

    await callback.message.answer(
        text='Для просмотра других точек нажмите /start',
        reply_markup=return_to_start()
    )
    await state.clear()


# Экстренная ситуация(type_6) ------------------------------------------------------------------
@router.callback_query(
    F.data == 'type_6',
    ProfileStatesGroup.recognize
)
async def dangerous_situation(callback: types.CallbackQuery,):
    await callback.message.answer(
        text=mes_data['dangerous_situation'],
        reply_markup=return_to_start()
    )


# ------------------------------------------------------------------------------------------------------
# Логируем каждое обновление
@router.message()
async def log_message(message: types.Message):
    logging.info(f'New message: {message.text}')


async def on_startup(bot: Bot) -> None:
    await bot.set_webhook(f"{WEBHOOK_URL}{WEBHOOK_PATH}")


async def main() -> None:
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    dp.include_router(router)

    # Настраиваем логирование
    logging.basicConfig(level=logging.INFO,
                        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
                        handlers=[
                            logging.FileHandler('../loging/bot.log'),
                            logging.StreamHandler()
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
