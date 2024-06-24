from os import remove
from json import load
from aiogram import F, types, Router
from Files.filters.States import ProfileStatesGroup
from aiogram.fsm.context import FSMContext
from Files.request import get_request_for_dots
from Files.support_function import return_to_start
from aiogram.types import FSInputFile
from Files.map import load_map

router = Router()

with open(r'../recurses/text_for_message/data_for_mess.json',
          'r') as data_for_mess:
    mes_data = load(data_for_mess)


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
    if not list_meal:
        await callback.message.answer(text=mes_data['bad_situation'])
        return
    elif count == 0:
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
    remove('map.png')

    await callback.message.answer(
        text='Для просмотра других точек нажмите /start',
        reply_markup=return_to_start()
    )
    await state.clear()
