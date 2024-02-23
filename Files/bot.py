import asyncio
import json
import os


from aiogram import F, Bot, types, Dispatcher
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from request import (
    get_request_for_dots,
    post_request_media,
    post_request_location_and_description,
    get_request_urgent_message
)

with open('toc.json', 'r') as json_file:
    inf_toc = json.load(json_file)

bot = Bot(token=inf_toc['token'])
dp = Dispatcher()

with open('../base/data_for_mess.json', 'r') as json_file:
    mes_data = json.load(json_file)

with open('../base/data_for_recognize.json', 'r') as json_file:
    recognize_data = json.load(json_file)

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
callback_type_road_deficiencies = [f'type_for_choose_{i + 1}' for i in range(9)]
callback_type_deficiencies = [f'type_for_help_{i + 1}' for i in range(9)]
callback_continue_or_return = ['continue', 'return']

callback_map_for_meal = [f'location_meal_{i}'for i in range(10)]
callback_map_for_gas_station = [f'location_gas_station_{i}'for i in range(10)]
callback_map_for_car_service = [f'location_car_service_{i}'for i in range(10)]
callback_map_for_parking_lot = [f'location_parking_lot_{i}'for i in range(10)]
callback_map_for_attractions = [f'location_attractions_{i}'for i in range(10)]


class ProfileStatesGroup(StatesGroup):
    input_photo = State()
    input_location = State()
    input_description = State()


# функция создания клавитатуры из 4 рядов по 1 кнопке
def get_route_mk(city, count):
    markup = InlineKeyboardBuilder()
    for i in range(count):
        btn = types.InlineKeyboardButton(
            text=mes_data[f'route_{city}'][i],
            callback_data=mes_data[f'route_callback_{city}'][i]
        )
        markup.row(btn)   # заносится по 1 кнопке на ряд
    return markup


def types_deficiencies(purpose):
    markup = InlineKeyboardBuilder()
    for i in range(9):
        btn = types.InlineKeyboardButton(
            text=mes_data['type_road_deficiencies'][i],
            callback_data=f'type_{purpose}{i + 1}'
        )
        markup.add(btn)
    markup.adjust(2, 1, 2, 2, 2)
    return markup


def btn_to_send_loc():
    kb = [[types.KeyboardButton(text="Отправить нынешнюю локацию", request_location=True)]]
    markup = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder='Отправьте геолокацию')
    return markup


@dp.message(Command('start'))
async def choice_of_area(message: types.Message):
    markup = InlineKeyboardBuilder()
    btn1 = types.InlineKeyboardButton(text='Челябинская область', callback_data='chelyabinsk')
    btn2 = types.InlineKeyboardButton(text='Курганская область', callback_data='kurgan')
    markup.row(btn1, btn2)
    await message.answer(
        text=mes_data['choice_of_area'],
        reply_markup=markup.as_markup()
    )


@dp.callback_query(F.data.in_(callback_area))
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


@dp.callback_query(F.data.in_(callback_route_for_post))
async def route_for_post(callback: types.CallbackQuery):
    global route
    route = callback.data

    # внезапныое сообщение
    answer = await get_request_urgent_message(road_name=route)
    if answer['danger_report'][0]['mes'] == '':
        await callback.message.answer(text=mes_data['good_situation'])
    else:
        await callback.message.answer(answer['danger_report'][0]['mes'])

    markup = InlineKeyboardBuilder()
    btn1 = types.InlineKeyboardButton(text='Сообщить', callback_data='report')
    btn2 = types.InlineKeyboardButton(text='Узнать', callback_data='recognize')
    markup.row(btn1, btn2)
    await callback.message.answer(
        text=mes_data['choose_action'],
        reply_markup=markup.as_markup()
    )


@dp.callback_query(F.data == 'report')
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


@dp.callback_query(F.data == 'option_1')
async def traffic_accident(callback: types.CallbackQuery):
    await callback.message.answer(text=mes_data['traffic_accident'])


# ------------------------------------------------------
@dp.callback_query(F.data == 'option_2')
async def locate_road_deficiencies(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(text=mes_data['road_deficiencies'])
    await callback.message.answer(text=mes_data['locate_road_deficiencies'], reply_markup=btn_to_send_loc())
    await state.set_state(ProfileStatesGroup.input_location)  # вешаем статус ожидания геолокации


@dp.message(F.location, ProfileStatesGroup.input_location)
async def end_road_deficiencies(message: types.Message, state: FSMContext):
    # post запрос
    longitude = message.location.longitude
    latitude = message.location.latitude
    post_result = await post_request_location_and_description(
        road_name=route,
        longitude=longitude,
        latitude=latitude,
        type_road='RoadDisadvantages'
    )
    global point_id_for_road_deficiencies
    point_id_for_road_deficiencies = post_result['addedPointId']

    markup = types_deficiencies(purpose='for_choose_')
    btn = types.InlineKeyboardButton(text='Помощь', callback_data='help')
    markup.row(btn)
    await message.answer(
        text=mes_data['text_for_type_road_deficiencies'],
        reply_markup=markup.as_markup()
    )
    await state.clear()


@dp.callback_query(F.data.in_(callback_type_road_deficiencies))
async def photo_road_deficiencies(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(text=mes_data['photo_road_deficiencies'])
    await state.set_state(ProfileStatesGroup.input_photo)  # вешаем cтатус ожидания фото


@dp.message(F.photo, ProfileStatesGroup.input_photo)
async def locate_road_deficiencies(message: types.Message, state: FSMContext):
    await bot.download(message.photo[-1], destination=f'{message.photo[-1].file_id}.jpg')
    status = await post_request_media(
        file_id=message.photo[-1].file_id,
        point_id=point_id_for_road_deficiencies,
        type_media='jpg'
     )
    if status:
        await message.answer(mes_data['end_road_deficiencies'])
        await state.clear()
    else:
        await message.answer('Хмм что-то пошло не так, попробуйте отправить еще раз')
        await state.set_state(ProfileStatesGroup.input_photo)
    os.remove(f'{message.photo[-1].file_id}.jpg')


# помощь ----------------------------------------------------
@dp.callback_query(F.data == 'help')
async def road_deficiencies(callback: types.CallbackQuery):
    await callback.message.answer(
        text=mes_data['text_for_help_type'],
        reply_markup=types_deficiencies(purpose='for_help_').as_markup()
    )


@dp.callback_query(F.data.in_(callback_type_deficiencies))
async def description_road_deficiencies(callback: types.CallbackQuery):
    for i in range(9):
        if callback.data == f'type_for_help_{i + 1}':
            markup = InlineKeyboardBuilder()
            btn1 = types.InlineKeyboardButton(text='Продолжить поиск', callback_data='continue')
            btn2 = types.InlineKeyboardButton(text='Вернуться к выбору', callback_data='return')
            markup.row(btn1, btn2)
            await callback.message.answer(
                text=mes_data['type_definitions'][i],
                reply_markup=markup.as_markup()
            )
    global mes_id
    mes_id = str(callback.message.message_id)


@dp.callback_query(F.data.in_(callback_continue_or_return))
async def continue_or_return(callback: types.CallbackQuery):
    if callback.data == 'continue':  # удалить сообщение с типом
        await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    elif callback.data == 'return':  # удалить сообщения с типом и помощью
        await bot.delete_messages(chat_id=callback.message.chat.id,
                                  message_ids=[callback.message.message_id, mes_id])


# --------------------------------------------------------------------------------------------
@dp.callback_query(F.data == 'option_3')
async def illegal_actions(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(text=mes_data['instructions_for_contact'])
    await callback.message.answer(text=mes_data['locate_road_deficiencies'], reply_markup=btn_to_send_loc())
    await state.set_state(ProfileStatesGroup.input_location)


@dp.message(F.location, ProfileStatesGroup.input_location)
async def input_description(message: types.Message, state: FSMContext):
    global locate
    locate = [message.location.longitude, message.location.latitude]

    await message.answer(text=mes_data['action_description'])
    await state.set_state(ProfileStatesGroup.input_description)


@dp.message(F.text, ProfileStatesGroup.input_description)
async def input_photo_or_video(message: types.Message, state: FSMContext):
    # post запрос
    description = message.text
    longitude = locate[0]
    latitude = locate[1]
    post_result = await post_request_location_and_description(
        road_name=route,
        longitude=longitude,
        latitude=latitude,
        description=description,
        type_road='ThirdPartyIllegalActions'
    )
    global point_id_for_illegal_actions
    point_id_for_illegal_actions = post_result['addedPointId']

    await message.answer(text=mes_data['media_of_illegal_actions'])
    await state.set_state(ProfileStatesGroup.input_photo)


@dp.message(F.photo or F.video, ProfileStatesGroup.input_photo)
async def input_photo_or_video(message: types.Message, state: FSMContext):
    if message.photo:
        await bot.download(message.photo[-1], destination=f'{message.photo[-1].file_id}.jpg')
        # обработка фото
        status = await post_request_media(
            file_id=message.photo[-1].file_id,
            point_id=point_id_for_illegal_actions,
            type_media='jpg'
        )
        if status:
            await message.answer(mes_data['end_road_deficiencies'])
            await state.clear()
        else:
            await message.answer('Хмм что-то пошло не так, попробуйте отправить еще раз')
            await state.set_state(ProfileStatesGroup.input_photo)
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
            await message.answer(mes_data['end_road_deficiencies'])
            await state.clear()
        else:
            await message.answer('Хмм что-то пошло не так, попробуйте отправить еще раз')
            await state.set_state(ProfileStatesGroup.input_photo)
        os.remove(f'{message.video.file_id}.mp4')

    await state.clear()


# ---------------------------------------------------------------------------------------------
@dp.callback_query(F.data == 'recognize')
async def choose_que(callback: types.CallbackQuery):
    markup = InlineKeyboardBuilder()
    for i in range(7):
        btn = types.InlineKeyboardButton(
            text=recognize_data['questions_for_recognize'][i],
            callback_data=f'type_{i + 1}'
        )
        markup.row(btn)
    await callback.message.answer(text=recognize_data['recognize'], reply_markup=markup.as_markup())


# Точки с едой (meal) -----------------------------------------------------------------
@dp.callback_query(F.data == 'type_1')
async def meal(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(text=recognize_data['start_and_send_location'], reply_markup=btn_to_send_loc())
    await state.set_state(ProfileStatesGroup.input_location)  # вешаем статус ожидания геолокации


@dp.message(F.location, ProfileStatesGroup.input_location)
async def choose_meal(message: types.Message, state: FSMContext):
    # запрос геолокаци мест с едой
    longitude = message.location.longitude
    latitude = message.location.latitude
    global list_meal
    list_meal = await get_request_for_dots(
        road_name=route,
        longitude=longitude,
        latitude=latitude,
        point_type='Cafes'
    )  # get запрос

    count = len(list_meal['points'])  # сколько пришло точек

    await message.answer(recognize_data['choose_meal'])
    markup = InlineKeyboardBuilder()
    for i in range(count):
        btn = types.InlineKeyboardButton(
            text=str(i + 1),
            callback_data=f'location_meal_{i}'
        )
        markup.add(btn)
    markup.adjust(5, 5)

    text = ''
    for i in range(count):
        name_meal = list_meal['points'][i]['name']
        distance_meal = round(list_meal['distancesFromUser'][i], 2)
        text += f"{i + 1}. {name_meal} : {distance_meal}км. от вас"

    await message.answer(text=text, reply_markup=markup.as_markup())
    await state.clear()


@dp.callback_query(F.data.in_(callback_map_for_meal))
async def send_meal(callback: types.CallbackQuery):
    await callback.message.answer(text=list_meal['points'][int(callback.data[9])]['name'])
    await bot.send_location(
        chat_id=callback.message.chat.id,
        longitude=list_meal['points'][int(callback.data[9])]['longitude'],
        latitude=list_meal['points'][int(callback.data[9])]['latitude']
    )


# АЗС (type_2) -------------------------------------------------------------------------------------------
@dp.callback_query(F.data == 'type_2')
async def gas_station(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(text=recognize_data['start_and_send_location'], reply_markup=btn_to_send_loc())
    await state.set_state(ProfileStatesGroup.input_location)  # вешаем статус ожидания геолокации


@dp.message(F.location, ProfileStatesGroup.input_location)
async def choose_gas_station(message: types.Message, state: FSMContext):
    # запрос геолокаци заправок
    longitude = message.location.longitude
    latitude = message.location.latitude
    global list_gas_station
    list_gas_station = await get_request_for_dots(
        road_name=route,
        longitude=longitude,
        latitude=latitude,
        point_type='GasStations'
    )
    count = len(list_gas_station['points'])  # сколько пришло точек

    await message.answer(recognize_data['choose_gas_station'])
    markup = InlineKeyboardBuilder()
    for i in range(count):
        btn = types.InlineKeyboardButton(
            text=str(i + 1),
            callback_data=f'location_gas_station_{i}'
        )
        markup.add(btn)
    markup.adjust(5, 5)

    text = ''
    for i in range(count):
        name_gas_station = list_gas_station['points'][i]['name']
        distance_gas_station = round(list_gas_station['distancesFromUser'][i], 2)
        text += f"{i + 1}. {name_gas_station} : {distance_gas_station}км. от вас"

    await message.answer(text=text, reply_markup=markup.as_markup())
    await state.clear()


@dp.callback_query(F.data.in_(callback_map_for_gas_station))
async def send_gas_station(callback: types.CallbackQuery):
    await callback.message.answer(text=list_gas_station['points'][int(callback.data[9])]['name'])
    await bot.send_location(
        chat_id=callback.message.chat.id,
        longitude=list_gas_station['points'][int(callback.data[9])]['longitude'],
        latitude=list_gas_station['points'][int(callback.data[9])]['latitude']
    )


# Точки с автосервисами (type_3) ---------------------------------------------------------
@dp.callback_query(F.data == 'type_3')
async def car_service(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(text=recognize_data['start_and_send_location'], reply_markup=btn_to_send_loc())
    await state.set_state(ProfileStatesGroup.input_location)  # вешаем статус ожидания геолокации


@dp.message(F.location, ProfileStatesGroup.input_location)
async def choose_car_service(message: types.Message, state: FSMContext):
    # запрос геолокаци мест с автосервисов
    longitude = message.location.longitude
    latitude = message.location.latitude
    global list_car_service
    list_car_service = await get_request_for_dots(
        road_name=route,
        longitude=longitude,
        latitude=latitude,
        point_type='CarServices'
    )

    count = len(list_car_service['points'])  # сколько пришло точек

    await message.answer(recognize_data['choose_car_service'])
    markup = InlineKeyboardBuilder()
    for i in range(count):
        btn = types.InlineKeyboardButton(
            text=str(i + 1),
            callback_data=f'location_car_service_{i}'
        )
        markup.add(btn)
    markup.adjust(5, 5)

    text = ''
    for i in range(count):
        name_car_service = list_car_service['points'][i]['name']
        distance_car_service = round(list_car_service['distancesFromUser'][i], 2)
        text += f"{i + 1}. {name_car_service} : {distance_car_service}км. от вас"

    await message.answer(text=text, reply_markup=markup.as_markup())
    await state.clear()


@dp.callback_query(F.data.in_(callback_map_for_car_service))
async def send_car_service(callback: types.CallbackQuery):
    await callback.message.answer(text=list_car_service['points'][int(callback.data[9])]['name'])
    await bot.send_location(
        chat_id=callback.message.chat.id,
        longitude=list_car_service['points'][int(callback.data[9])]['longitude'],
        latitude=list_car_service['points'][int(callback.data[9])]['latitude']
    )


# Точки с временной парковкой (type_4) ----------------------------------------------------------------
@dp.callback_query(F.data == 'type_4')
async def parking_lot(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(text=recognize_data['start_and_send_location'], reply_markup=btn_to_send_loc())
    await state.set_state(ProfileStatesGroup.input_location)  # вешаем статус ожидания геолокации


@dp.message(F.location, ProfileStatesGroup.input_location)
async def choose_parking_lot(message: types.Message, state: FSMContext):
    # запрос геолокаци мест с парковкой
    longitude = message.location.longitude
    latitude = message.location.latitude
    global list_parking_lot
    list_parking_lot = await get_request_for_dots(
        road_name=route,
        longitude=longitude,
        latitude=latitude,
        point_type='RestPlaces'
    )

    count = len(list_parking_lot['points'])  # сколько пришло точек

    await message.answer(recognize_data['choose_parking_lot'])
    markup = InlineKeyboardBuilder()
    for i in range(count):
        btn = types.InlineKeyboardButton(
            text=str(i + 1),
            callback_data=f'location_parking_lot_{i}'
        )
        markup.add(btn)
    markup.adjust(5, 5)

    text = ''
    for i in range(count):
        name_parking_lot = list_parking_lot['points'][i]['name']
        distance_parking_lot = round(list_parking_lot['distancesFromUser'][i], 2)
        text += f"{i + 1}. {name_parking_lot} : {distance_parking_lot}км. от вас"

    await message.answer(text=text, reply_markup=markup.as_markup())
    await state.clear()


@dp.callback_query(F.data.in_(callback_map_for_parking_lot))
async def send_parking_lot(callback: types.CallbackQuery):
    await callback.message.answer(text=list_parking_lot['points'][int(callback.data[9])]['name'])
    await bot.send_location(
        chat_id=callback.message.chat.id,
        longitude=list_parking_lot['points'][int(callback.data[9])]['longitude'],
        latitude=list_parking_lot['points'][int(callback.data[9])]['latitude']
    )


# # Что меня ждет на дороге (type_5)--------------------------------------------------------------------------
# @dp.callback_query(F.data == 'type_5')
# async def interesting_places(callback: types.CallbackQuery, state: FSMContext):
#     await callback.message.answer(text=recognize_data['start_and_send_location'], reply_markup=btn_to_send_loc())
#     await state.set_state(ProfileStatesGroup.input_location)  # вешаем статус ожидания геолокации
#
#
# # @dp.message(F.location, ProfileStatesGroup.input_location)
# async def choose_interesting_places(message: types.Message, state: FSMContext):
#     # запрос геолокаци интересных мест
#     longitude = message.location.longitude
#     latitude = message.location.latitude
#     global list_interesting_places
#     list_interesting_places = await get_request_for_map(road_name=route, x=longitude, y=latitude)  # get запрос
#
#     await message.answer(recognize_data['choose_interesting_places'])
#     markup = InlineKeyboardBuilder()
#     for i in range(10):
#         btn = types.InlineKeyboardButton(
#             text=str(i + 1),
#             callback_data=f'location_interesting_places_{i}'
#         )
#         markup.add(btn)
#     markup.adjust(5, 5)
#
#     text = ''
#     for i in range(10):
#         name_interesting_places = list_parking_lot['interesting_places'][i]['name']
#         distance_interesting_places = list_parking_lot['interesting_places'][i]['s']
#         text += f"{i + 1}. {name_interesting_places} : {distance_interesting_places}км. от вас"
#
#     await message.answer(text=text, reply_markup=markup.as_markup())
#     await state.clear()
#
#
# @dp.callback_query(F.data.in_(callback_map_for_interesting_places))
# async def send_interesting_places(callback: types.CallbackQuery):
#     await callback.message.answer(text=list_interesting_places['interesting_places'][int(callback.data[9])]['name'])
#     await bot.send_location(
#         chat_id=callback.message.chat.id,
#         longitude=list_parking_lot['interesting_places'][int(callback.data[9])]['y'],
#         latitude=list_parking_lot['interesting_places'][int(callback.data[9])]['x']
#     )
#

# Точки с достопримечательностями (type_6) ------------------------------------------------------------
@dp.callback_query(F.data == 'type_6')
async def attractions(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(text=recognize_data['start_and_send_location'], reply_markup=btn_to_send_loc())
    await state.set_state(ProfileStatesGroup.input_location)  # вешаем статус ожидания геолокации


@dp.message(F.location, ProfileStatesGroup.input_location)
async def choose_attractions(message: types.Message, state: FSMContext):
    # запрос геолокаци мест с достопримечательностями
    longitude = message.location.longitude
    latitude = message.location.latitude
    global list_attractions
    list_attractions = await get_request_for_dots(
        road_name=route,
        longitude=longitude,
        latitude=latitude,
        point_type='InterestingPlaces'
    )

    count = len(list_attractions['points'])  # сколько пришло точек

    await message.answer(recognize_data['choose_attractions'])
    markup = InlineKeyboardBuilder()
    for i in range(count):
        btn = types.InlineKeyboardButton(
            text=str(i + 1),
            callback_data=f'location_attractions_{i}'
        )
        markup.add(btn)
    markup.adjust(5, 5)

    text = ''
    for i in range(count):
        name_attractions = list_attractions['points'][i]['name']
        distance_attractions = round(list_attractions['distancesFromUser'][i], 2)
        text += f"{i + 1}. {name_attractions} : {distance_attractions}км. от вас "

    await message.answer(text=text, reply_markup=markup.as_markup())
    await state.clear()


@dp.callback_query(F.data.in_(callback_map_for_attractions))
async def send_attractions(callback: types.CallbackQuery):
    await callback.message.answer(text=list_attractions['points'][int(callback.data[9])]['name'])
    await bot.send_location(
        chat_id=callback.message.chat.id,
        longitude=list_attractions['points'][int(callback.data[9])]['longitude'],
        latitude=list_attractions['points'][int(callback.data[9])]['latitude']
    )


# Экстренная ситуация(type_7 / option_4) ------------------------------------------------------------------
@dp.callback_query(F.data == 'option_4' or F.data == 'type_7')
async def dangerous_situation(callback: types.CallbackQuery):
    await callback.message.answer(text=mes_data['dangerous_situation'])

# ------------------------------------------------------------------------------------------------------


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
