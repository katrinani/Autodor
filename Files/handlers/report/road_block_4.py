from json import load
from aiogram import F, types, Router
from Files.filters.States import ProfileStatesGroup
from aiogram.fsm.context import FSMContext
from Files.request import post_request_location_and_description
from Files.support_function import return_to_start

router = Router()

with open(r'../recurses/text_for_message/data_for_mess.json',
          'r') as data_for_mess:
    mes_data = load(data_for_mess)


@router.callback_query(F.data == 'option_4', ProfileStatesGroup.report)
async def road_block(
        callback: types.CallbackQuery,
        state: FSMContext
):
    await callback.message.answer(text=mes_data['traffic_accident'])
    await state.set_state(ProfileStatesGroup.input_description_for_road_block)


@router.message(
    F.text,
    ProfileStatesGroup.input_description_for_road_block
)
async def description_for_traffic_accident(message: types.Message, state: FSMContext):
    data = await state.get_data()
    route = data["road"]  # получение дороги
    longitude = data["longitude"]
    latitude = data["latitude"]
    level = data["reliability_level"]

    request = await post_request_location_and_description(
        road_name=route,
        longitude=longitude,
        latitude=latitude,
        type_road=2,  # RoadBlock = 2
        description=message.text,
        level=level
    )
    if request:
        await message.answer(mes_data['end_road_deficiencies'])
        await message.answer(
            text='Для повторного выбора нажмите /start',
            reply_markup=return_to_start()
        )
        await state.clear()
    else:
        await message.answer(mes_data['bad_situation'])
        await state.clear()
