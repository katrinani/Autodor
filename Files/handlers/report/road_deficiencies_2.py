from json import load
from os import remove
from aiogram import F, types, Router, Bot
from Files.filters.States import States
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from Files.request import post_request_location_and_description, post_request_media
from Files.support_function import return_to_start, btn_yes_or_not

router = Router()

with open(r'../recurses/text_for_message/data_for_mess.json',
          'r') as data_for_mess:
    mes_data = load(data_for_mess)

with open(r'../recurses/text_for_message/callback_data.json',
          'r') as callback_mes_data:
    callback_data = load(callback_mes_data)


@router.callback_query(F.data == 'option_2', States.report)
async def road_deficiencies(
        callback: types.CallbackQuery,
        state: FSMContext
):
    await callback.message.answer(text=mes_data['road_deficiencies'])

    markup = InlineKeyboardBuilder()
    for i in range(4):
        btn = types.InlineKeyboardButton(
            text=mes_data['type_road_deficiencies'][i],
            callback_data=mes_data['type_road_deficiencies'][i]
        )
        markup.add(btn)
        print(mes_data['type_road_deficiencies'][i])
    markup.adjust(1, 2, 1)

    await callback.message.answer(
        text=mes_data['text_for_type_road_deficiencies'],
        reply_markup=markup.as_markup()
    )
    await state.set_state(States.output_text_for_road_deficiencies)
    print(f"road_deficiencies: Current state: {await state.get_state()}")


@router.callback_query(
    F.data.in_(callback_data['callback_type_road_deficiencies']),
    States.output_text_for_road_deficiencies
)
async def photo_road_deficiencies(callback: types.CallbackQuery, state: FSMContext):
    print(f"photo_road_deficiencies: Current state: {await state.get_state()}")
    print(f"photo_road_deficiencies: Callback data: {callback.data}")

    data = await state.get_data()
    route = data["road"]  # получение дороги
    longitude = data["longitude"]
    latitude = data["latitude"]
    level = data["reliability_level"]

    # post запрос
    list_road_deficiencies = await post_request_location_and_description(
        road_name=route,
        longitude=longitude,
        latitude=latitude,
        type_road=1,
        description=callback.data,
        level=level
    )
    if not list_road_deficiencies:
        await callback.message.answer(mes_data['bad_situation'])
        await state.clear()
        return
    print(list_road_deficiencies)
    # сохраняем id точки
    point_id_for_road_deficiencies = list_road_deficiencies['pointId']
    await state.update_data({"id_for_road_deficiencies": point_id_for_road_deficiencies})

    await callback.message.answer(text=mes_data['photo_or_not'], reply_markup=btn_yes_or_not().as_markup())
    await state.set_state(States.photo_sending_option_for_road_deficiencies)


@router.callback_query(F.data == 'no', States.photo_sending_option_for_road_deficiencies)
async def photo_consent(
            callback: types.CallbackQuery,
            state: FSMContext
    ):
    await callback.message.answer(text=mes_data['lack_of_photo'])
    await state.clear()


@router.callback_query(F.data == 'yes', States.photo_sending_option_for_road_deficiencies)
async def photo_consent(
            callback: types.CallbackQuery,
            state: FSMContext
    ):
    await callback.message.answer(text=mes_data['photo_road_deficiencies'])
    await state.set_state(States.input_photo_for_road_deficiencies)


@router.message(
    F.photo,
    States.input_photo_for_road_deficiencies
)
async def photo_road_deficiencies(
        message: types.Message,
        state: FSMContext,
        bot: Bot
):
    # получение id точки
    data = await state.get_data()
    point_id_for_road_deficiencies = data['id_for_road_deficiencies']

    if message.photo:
        await bot.download(message.photo[-1], destination=f'{message.photo[-1].file_id}.jpg')
        # обработка фото
        status = await post_request_media(
            file_id=message.photo[-1].file_id,
            point_id=point_id_for_road_deficiencies,
            type_media='jpg'
        )
        if status:
            await message.answer(
                mes_data['end_road_deficiencies'],
                reply_markup=return_to_start()
            )
            await state.clear()
        else:
            await message.answer(text=mes_data['bad_situation'])
            await state.set_state(States.input_photo_for_road_deficiencies)
        remove(f'{message.photo[-1].file_id}.jpg')

    elif message.video:
        await bot.download(message.video, destination=f'{message.video.file_id}.mp4')
        # обработка видео
        status = await post_request_media(
            file_id=message.video.file_id,
            point_id=point_id_for_road_deficiencies,
            type_media='mp4'
        )
        if status:
            await message.answer(
                mes_data['end_road_deficiencies'],
                reply_markup=return_to_start()
            )
            await state.clear()
        else:
            await message.answer(text=mes_data['bad_situation'])
            await state.set_state(States.input_photo_for_road_deficiencies)
        remove(f'{message.video.file_id}.mp4')
    await state.clear()
