import aiogram
import asyncio
import json

from aiogram import F, Bot, types, Dispatcher
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import Command

bot = Bot(token='6747593068:AAGdf7qZtm5ptYQ8FShElqKnkcZRZxiWGlA')
dp = Dispatcher()

with open('data_for_mess.json', 'r') as json_file:
    mes_data = json.load(json_file)

callback_area = ['chelyabinsk', 'kurgan']


def get_route_chelyabinsk_mk():
    markup = InlineKeyboardBuilder()
    for i in range(4):
        btn = types.InlineKeyboardButton(
            text=mes_data['route_chelyabinsk'][i],
            callback_data=f'route_chelyabinsk_{i + 1}')
        markup.row(btn)
    return markup


def get_route_kurgan_mk():
    markup = InlineKeyboardBuilder()
    for i in range(4):
        btn = types.InlineKeyboardButton(
            text=mes_data['route_kurgan'][i],
            callback_data=f'route_kurgan_{i + 1}')
        markup.row(btn)
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
            reply_markup=get_route_chelyabinsk_mk().as_markup()
        )
    else:
        await callback.message.answer(text='Курганская область')
        await callback.message.answer(
            text=mes_data['route_choice'],
            reply_markup=get_route_kurgan_mk().as_markup()
        )


@dp.callback_query(F.data)  # обрабатываются все колбэки, кроме конкретных
async def choose_action(callback: types.CallbackQuery):
    markup = InlineKeyboardBuilder()
    btn1 = types.InlineKeyboardButton(text='Сообщить', callback_data='report')
    btn2 = types.InlineKeyboardButton(text='Узнать', callback_data='recognize')
    markup.row(btn1, btn2)
    await callback.message.answer(
        text=mes_data['choose_action'],
        reply_markup=markup.as_markup()
    )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
