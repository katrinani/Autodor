from os import remove
from json import load
from aiogram import F, types, Router
from Files.filters.States import States
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
from Files.support_function import return_to_start
from Files.request import get_request_for_dots
from Files.map import load_map

router = Router()

with open(r'../recurses/text_for_message/data_for_mess.json',
          'r') as data_for_mess:
    mes_data = load(data_for_mess)


@router.callback_query(
    F.data == 'type_5',
    States.recognize
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
    if not list_attractions:
        await callback.message.answer(text=mes_data['bad_situation'])
        return
    elif count == 0:
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
    remove('map.png')

    await callback.message.answer(
        text='Для просмотра других точек нажмите /start',
        reply_markup=return_to_start()
    )
    await state.clear()
