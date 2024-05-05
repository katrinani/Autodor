# импорты из библиотеки aiogram
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup
from aiogram import types

# импорты из файла request.py
from request import (get_all_regions, get_all_roads)


async def make_callback_regions() -> list:
    """
    C помощью запроса создает список из всех пришедших регонов
    :return: callback: list - список регионов
    """
    request = await get_all_regions()
    callback = [request['regions'][i]['name'] for i in range(len(request['regions']))]
    return callback


async def make_callback_route() -> list:
    """
    С помощью запроса создает список из всех пришедших дорог
    :return: callback: list - список дорог
    """
    request = await get_all_roads()
    callback = [request['roads'][i]['roadName'] for i in range(len(request['roads']))]
    return callback


def get_route_mk(
        all_roads: list,
        count: int
) -> InlineKeyboardBuilder:
    """
        Создаёт инлайн-клавиатуру по 1 кнопке в произвольном количестве рядов для конкретной области
        :param all_roads: список из словарей, в каждом из которых имя дороги
        :param count: количество рядов с кнопками
        :return: InlineKeyboardBuilder
    """
    markup = InlineKeyboardBuilder()
    for i in range(count):
        btn = types.InlineKeyboardButton(
            text=all_roads[i]['roadName'],
            callback_data=all_roads[i]['roadName']
        )
        markup.row(btn)
    return markup


def btn_to_send_loc() -> ReplyKeyboardMarkup:
    """
        Создаёт реплай-клавиатуру с кнопкой в один ряд для отправления локации
        :return: ReplyKeyboardMarkup
    """
    kb = [[types.KeyboardButton(text="Отправить нынешнюю локацию", request_location=True)]]
    markup = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder='Отправьте геолокацию')
    return markup


def return_to_start() -> ReplyKeyboardMarkup:
    """
        Создает реплай-клавиатуру с кнопкой для возврата в стартовую функцию
        :return: ReplyKeyboardMarkup
    """
    kb = [[types.KeyboardButton(text="/start")]]
    markup = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        one_time_keyboard=True)
    return markup