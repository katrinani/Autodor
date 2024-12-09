from os import remove
from json import load
from aiogram import F, types, Router
from filters.States import States
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
from support_function import return_to_start
from request import get_request_for_dots
from map import load_map

router = Router()

with open(r'/usr/src/app/recurses/text_for_message/data_for_mess.json',
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
    await callback.message.answer(
        "Посетите [Азбуку мероприятий](https://regions.kp.ru/chel/azbuka-festival-ural/) Южного Урала!",
        parse_mode="Markdown"
    )

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

    if list_attractions is None:
        await callback.message.answer(text=mes_data['bad_situation'])
        await state.clear()
        return

    count = len(list_attractions['points'])  # сколько пришло точек
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
        name_attractions = list_attractions['points'][i]['name']
        distance_attractions = round(list_attractions['points'][i]['distanceFromUser'], 2)
        description = list_attractions['points'][i]['description']
        text += f"{i + 1}. {name_attractions} : {distance_attractions}км. от вас\n {description}\n"
    await callback.message.answer(text=text)

    # вывод карты
    load_map(longitude=longitude, latitude=latitude, list_dots=list_attractions, color='or')
    file = FSInputFile('map.png')
    await callback.message.answer_photo(file)
    remove('map.png')

    await callback.message.answer(
        text='Для возврата в главное меню нажмите /start',
        reply_markup=return_to_start()
    )
    await state.clear()
