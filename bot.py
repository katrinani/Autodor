# import aiogram
import asyncio
import json

from aiogram import F, Bot, types, Dispatcher
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
# from aiogram.enums import ParseMode

from db_map import db_start, create_profile, edit_area

bot = Bot(token='6747593068:AAGdf7qZtm5ptYQ8FShElqKnkcZRZxiWGlA')
dp = Dispatcher()

with open('data_for_mess.json', 'r') as json_file:
    mes_data = json.load(json_file)

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

callback_type_road_deficiencies = [f'type_for_choose_{i + 1}' for i in range(9)]
callback_type_deficiencies = [f'type_for_help_{i + 1}' for i in range(9)]
callback_continue_or_return = ['continue', 'return']


class ProfileStatesGroup(StatesGroup):
    input_photo = State()
    input_location = State()


# функция создания клавитатуры из 4 рядов по 1 кнопке
def get_route_mk(city):
    markup = InlineKeyboardBuilder()
    for i in range(4):
        btn = types.InlineKeyboardButton(
            text=mes_data[f'route_{city}'][i],
            callback_data=f'route_{city}_{i + 1}'
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
        await edit_area(area='Челябинская область', user_id=tg_user_id)
        await callback.message.answer(
            text=mes_data['route_choice'],
            reply_markup=get_route_mk(city='chelyabinsk').as_markup()
        )
    else:
        await callback.message.answer(text='Курганская область')
        await edit_area(area='Курганская область', user_id=tg_user_id)
        await callback.message.answer(
            text=mes_data['route_choice'],
            reply_markup=get_route_mk(city='kurgan').as_markup()
        )


@dp.callback_query(F.data.in_(callback_route))  # обрабатываются все колбэки, кроме конкретных
async def choose_action(callback: types.CallbackQuery):
    markup = InlineKeyboardBuilder()
    btn1 = types.InlineKeyboardButton(text='Сообщить', callback_data='report')
    btn2 = types.InlineKeyboardButton(text='Узнать', callback_data='recognize')
    markup.row(btn1, btn2)
    await callback.message.answer(
        text=mes_data['choose_action'],
        reply_markup=markup.as_markup()
    )


@dp.callback_query(F.data == 'report' or Command('report'))
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
    kb = [[types.KeyboardButton(text="Отправить локацию", request_location=True)]]
    markup = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder='Отправьте геолокацию')
    await message.answer(text=mes_data['locate_road_deficiencies'], reply_markup=markup)
    await state.set_state(ProfileStatesGroup.input_location)  # вешаем статус ожидания геолокации


@dp.message(F.location, ProfileStatesGroup.input_location)
async def end_road_deficiencies(message: types.Message, state: FSMContext):
    await message.answer(text=mes_data['end_road_deficiencies'])
    await state.clear()


# @dp.callback_query(F.data == 'option_3')
# async def illegal_acts(callback: types.CallbackQuery):


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
