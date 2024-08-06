from os import remove
from json import load
from aiogram import F, types, Router
from Files.filters.States import States
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
    F.data == 'type_4',
    States.recognize
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

    if list_parking_lot is None:
        await callback.message.answer(text=mes_data['bad_situation'])
        await state.clear()
        return

    count = len(list_parking_lot['points'])  # сколько пришло точек
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
        name_parking_lot = list_parking_lot['points'][i]['name']
        distance_parking_lot = round(list_parking_lot['points'][i]['distanceFromUser'], 2)
        text += f"{i + 1}. {name_parking_lot} : {distance_parking_lot}км. от вас\n"
    await callback.message.answer(text=text)

    # вывод карты
    load_map(longitude=longitude, latitude=latitude, list_dots=list_parking_lot, color='vv')
    file = FSInputFile('map.png')
    await callback.message.answer_photo(file)
    remove('map.png')

    await callback.message.answer(
        text='Для просмотра других точек нажмите /start',
        reply_markup=return_to_start()
    )
    await state.clear()
