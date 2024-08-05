from json import load
from os import remove
from aiogram import F, types, Router, Bot
from Files.filters.States import States
from Files.filters.IsPhotoOrVideo import IsPhotoOrVideo
from aiogram.fsm.context import FSMContext
from Files.request import post_request_location_and_description, post_request_media
from Files.support_function import return_to_start, btn_yes_or_not

router = Router()

with open(r'../recurses/text_for_message/data_for_mess.json',
          'r') as data_for_mess:
    mes_data = load(data_for_mess)


@router.callback_query(F.data == 'option_3', States.report)
async def illegal_actions(
        callback: types.CallbackQuery,
        state: FSMContext
):
    await callback.message.answer(text=mes_data['instructions_for_contact'])

    await callback.message.answer(text=mes_data['action_description'])
    await state.set_state(States.input_description_for_illegal_actions)


@router.message(
    F.text,
    States.input_description_for_illegal_actions
)
async def input_photo_or_video(message: types.Message, state: FSMContext):
    # получение иформации
    data = await state.get_data()

    route = data["road"]
    description = message.text
    longitude = data["longitude"]
    latitude = data["latitude"]
    level = data["reliability_level"]

    # post запрос
    post_result = await post_request_location_and_description(
        road_name=route,
        longitude=longitude,
        latitude=latitude,
        description=description,
        type_road=3,
        level=level
    )
    if post_result is None:
        await message.answer(mes_data['bad_situation'])
        await state.clear()
        return

    point_id_for_illegal_actions = post_result['pointId']
    # сохранение id точки
    await state.update_data({"id_for_illegal_actions": point_id_for_illegal_actions})
    await message.answer(text=mes_data['photo_or_not'], reply_markup=btn_yes_or_not().as_markup())
    await state.set_state(States.photo_sending_option_for_illegal_actions)


@router.callback_query(F.data == 'no', States.photo_sending_option_for_illegal_actions)
async def photo_consent(
        callback: types.CallbackQuery,
        state: FSMContext
):
    await callback.message.answer(text=mes_data['lack_of_photo'])
    await state.clear()


@router.callback_query(F.data == 'yes', States.photo_sending_option_for_illegal_actions)
async def photo_consent(
        callback: types.CallbackQuery,
        state: FSMContext
):
    await callback.message.answer(text=mes_data['media_of_illegal_actions'])
    await state.set_state(States.input_photo_for_illegal_actions)


@router.message(
    IsPhotoOrVideo(),
    States.input_photo_for_illegal_actions
)
async def input_photo_or_video(
        message: types.Message,
        state: FSMContext,
        bot: Bot
):
    # получение id сообщения
    data = await state.get_data()
    point_id_for_illegal_actions = data["id_for_illegal_actions"]

    if message.photo:
        await bot.download(message.photo[-1], destination=f'{message.photo[-1].file_id}.jpg')
        # обработка фото
        status = await post_request_media(
            file_id=message.photo[-1].file_id,
            point_id=point_id_for_illegal_actions,
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
            await state.set_state(States.input_photo_for_illegal_actions)
        remove(f'{message.photo[-1].file_id}.jpg')

    elif message.video:
        await bot.download(message.video, destination=f'{message.video.file_id}.mp4')
        # обработка видео
        status = await post_request_media(
            file_id=message.video.file_id,
            point_id=point_id_for_illegal_actions,
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
            await state.set_state(States.input_photo_for_illegal_actions)
        remove(f'{message.video.file_id}.mp4')
    await state.clear()
