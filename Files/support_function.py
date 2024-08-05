# импорты из библиотеки aiogram
from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types
from pydub import AudioSegment
import os

# импорты из файла request.py
from request import get_request_audio


def btn_yes_or_not():
    # кнопки да/нет
    markup = InlineKeyboardBuilder()
    btn_1 = types.InlineKeyboardButton(text='Да', callback_data='yes')
    btn_2 = types.InlineKeyboardButton(text='Нет', callback_data='no')
    markup.add(btn_1, btn_2)
    markup.adjust(2)
    return markup


def btn_to_send_loc() -> ReplyKeyboardMarkup:
    """
        Создаёт реплай-клавиатуру с кнопкой в один ряд для отправления локации
        :return: ReplyKeyboardMarkup
    """
    kb = [[types.KeyboardButton(text='Отправьте свою геолокацию', request_location=True)]]
    markup = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder='Отправьте геолокацию'
    )

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


async def concate_files(
    count: int, answer: [any, any, any], callback: int, flag: True, audio: AudioSegment
) -> tuple[bool, AudioSegment]:
    audio = AudioSegment.empty()
    for i in range(count):
        file_path = f"{answer['advertisements'][i]['id']}-{callback}.ogg"
        r = await get_request_audio(answer["advertisements"][i]["id"])

        if r is not None:
            flag = True
            with open(file_path, "wb") as f:
                f.write(r.content)
            if i == 0:
                audio = AudioSegment.from_file(file_path, format="ogg")
                i = +1
            else:
                audio = audio + AudioSegment.silent(1000)
                audio = audio + AudioSegment.from_file(file_path, format="ogg")
            os.remove(file_path)
    return flag, audio
