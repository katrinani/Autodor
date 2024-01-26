# import aiogram
import asyncio
import json


from aiogram import F, Bot, types, Dispatcher
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
# from aiogram.enums import ParseMode

from db_map import db_start, create_profile, edit_route, edit_location
from request import post_request_for_road_deficiencie, get_request_for_map

bot = Bot(token='6747593068:AAGdf7qZtm5ptYQ8FShElqKnkcZRZxiWGlA')
dp = Dispatcher()

with open('data_for_mess.json', 'r') as json_file:
    mes_data = json.load(json_file)

with open('data_for_recognize.json', 'r') as json_file:
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
callback_route_for_post = ['М-5', 'А-310', 'Р-254', 'Р-354', 'Тест']
callback_type_road_deficiencies = [f'type_for_choose_{i + 1}' for i in range(9)]
callback_type_deficiencies = [f'type_for_help_{i + 1}' for i in range(9)]
callback_continue_or_return = ['continue', 'return']
callback_map_for_gas_station = [f'location_{i}'for i in range(10)]


class ProfileStatesGroup(StatesGroup):
    input_photo = State()
    input_location = State()
    location_for_azs = State()


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
    # работа с бд
    global tg_user_id
    tg_user_id = str(message.from_user.id)
    await db_start()
    await create_profile(user_id=tg_user_id)


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
    # db
    global route
    route = callback.data
    await edit_route(route=route, user_id=tg_user_id)

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


@dp.callback_query(F.data == 'option_2')
async def road_deficiencies(callback: types.CallbackQuery):
    await callback.message.answer(text=mes_data['road_deficiencies'])
    markup = types_deficiencies(purpose='for_choose_')
    btn = types.InlineKeyboardButton(text='Помощь', callback_data='help')
    markup.row(btn)
    await callback.message.answer(
        text=mes_data['text_for_type_road_deficiencies'],
        reply_markup=markup.as_markup()
    )


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
        await bot.delete_message(chat_id=tg_user_id, message_id=callback.message.message_id)
    elif callback.data == 'return':  # удалить сообщения с типом и помощью
        await bot.delete_messages(chat_id=tg_user_id,
                                  message_ids=[callback.message.message_id, mes_id])


@dp.callback_query(F.data.in_(callback_type_road_deficiencies))
async def photo_road_deficiencies(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(text=mes_data['photo_road_deficiencies'])
    await state.set_state(ProfileStatesGroup.input_photo)  # вешаем cтатус ожидания фото


@dp.message(F.photo, ProfileStatesGroup.input_photo)
async def locate_road_deficiencies(message: types.Message, state: FSMContext):
    kb = [[types.KeyboardButton(text="Отправить нынешнюю локацию", request_location=True)]]
    markup = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder='Отправьте геолокацию')
    await message.answer(text=mes_data['locate_road_deficiencies'], reply_markup=markup)
    await state.set_state(ProfileStatesGroup.input_location)  # вешаем статус ожидания геолокации


@dp.message(F.location, ProfileStatesGroup.input_location)
async def end_road_deficiencies(message: types.Message, state: FSMContext):
    # бд
    longitude = message.location.longitude
    latitude = message.location.latitude
    await edit_location(longitude=longitude, latitude=latitude, user_id=tg_user_id)
    status = await post_request_for_road_deficiencie(road_name=route, x=longitude, y=latitude)  # post запрос

    if status:
        await message.answer(text=mes_data['end_road_deficiencies'])
        await state.clear()
    else:
        await message.answer('Хмм что-то не так с геолокацией, попробуйте еще раз')
        await state.set_state(ProfileStatesGroup.input_location)


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


@dp.callback_query(F.data == 'type_2')
async def gas_station(callback: types.CallbackQuery, state: FSMContext):
    kb = [[types.KeyboardButton(text="Отправить нынешнюю локацию", request_location=True)]]
    markup = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder='Отправьте геолокацию')
    await callback.message.answer(text=recognize_data['start_and_send_location'], reply_markup=markup)
    await state.set_state(ProfileStatesGroup.location_for_azs)  # вешаем статус ожидания геолокации


@dp.message(F.location, ProfileStatesGroup.location_for_azs)
async def choose_gas_station(message: types.Message, state: FSMContext):
    # запрос геолокаци заправок
    longitude = message.location.longitude
    latitude = message.location.latitude
    result = await get_request_for_map(road_name=route, x=longitude, y=latitude)  # get запрос
    global list_gas_station
    list_gas_station = result
    # global list_gas_station
    # with open('test.json', 'r') as file: 
    #     list_gas_station = json.load(file)

    await message.answer(recognize_data['choose_gas_station'])
    markup = InlineKeyboardBuilder()
    for i in range(10):
        btn = types.InlineKeyboardButton(
            text=str(i + 1),
            callback_data=f'location_{i}'
        )
        markup.add(btn)
    markup.adjust(5, 5)

    text = ''
    for i in range(10):
        text += f"{i + 1}. {list_gas_station['gasStations'][i]['name']} \n"

    await message.answer(text=text, reply_markup=markup.as_markup())
    await state.clear()


@dp.callback_query(F.data.in_(callback_map_for_gas_station))
async def send_gas_station(callback: types.CallbackQuery):
    await callback.message.answer(text=list_gas_station['gasStations'][int(callback.data[9])]['name'])
    await bot.send_location(
        chat_id=tg_user_id,
        longitude=list_gas_station['gasStations'][int(callback.data[9])]['x'],
        latitude=list_gas_station['gasStations'][int(callback.data[9])]['y']
    )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
