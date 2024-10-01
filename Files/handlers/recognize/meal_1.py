from os import remove
from json import load
from aiogram import F, types, Router
from filters.States import States
from aiogram.fsm.context import FSMContext
from request import get_request_for_dots
from support_function import return_to_start
from aiogram.types import FSInputFile
from map import load_map

router = Router()

with open(r'../recurses/text_for_message/data_for_mess.json',
          'r') as data_for_mess:
    mes_data = load(data_for_mess)


@router.callback_query(
    F.data == 'type_1',
    States.recognize
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

    if list_meal is None:
        await callback.message.answer(text=mes_data['bad_situation'])
        await state.clear()
        return

    count = len(list_meal['points'])  # сколько пришло точек
    if count == 0:
        await callback.message.answer('К сожалению ближайших к вам точек нет')
        await callback.message.answer(
            text='Для просмотра других точек нажмите /start',
            reply_markup=return_to_start()
        )
        await state.clear()
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
    remove('map.png')

    await callback.message.answer(
        text='Для просмотра других точек нажмите /start',
        reply_markup=return_to_start()
    )
    await state.clear()
