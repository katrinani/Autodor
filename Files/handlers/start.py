from os import remove
from json import load
from aiogram import F, types, Router
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import FSInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from pydub import AudioSegment
from Files.filters.States import States
from Files.request import (
    get_road_and_region,
    get_request_urgent_message,
    get_advertisements_for_region
)
from Files.support_function import btn_to_send_loc, concate_files, btn_yes_or_not

router = Router()

with open(r'../recurses/text_for_message/data_for_mess.json',
          'r') as data_for_mess:
    mes_data = load(data_for_mess)


@router.message(Command('start'))
async def start(message: types.Message, state: FSMContext):
    await message.answer(text=mes_data['start_talk'], reply_markup=btn_to_send_loc())
    await state.set_state(States.input_location)


@router.message(
        F.location,
        States.input_location
    )
async def location_confirmation(message: types.Message, state: FSMContext):
    if message.reply_to_message is None:
        print('Самостоятельно отправленная локация')
        await state.update_data({"reliability_level": 2})
    else:
        print('Локация через кнопку')
        await state.update_data({"reliability_level": 1})
    longitude = message.location.longitude
    latitude = message.location.latitude
    # сохраняем локацию
    await state.update_data({"longitude": longitude})
    await state.update_data({"latitude": latitude})

    # запрос на бэк для получения области и дороги
    answer = await get_road_and_region(
        longitude=longitude,
        latitude=latitude
    )
    print(answer)
    if answer is None:
        # в случае если не получилось обратиться к бэку или статус код 4хх-5хх
        await message.answer(text=mes_data['bad_situation'])
        await state.clear()
        return
    elif not answer['roadName'] and not answer['regionName']:
        await message.answer('Вы слишком далеко от киллометрового столба. Попробуйте еще раз позже')
        await state.set_state(States.input_location)
        return

    # сохраняем место
    await state.update_data({"road": answer['roadName']})
    await state.update_data({"region": answer['regionName']})

    text = f"Вы находитесь на дороге {answer['roadName']} в {answer['regionName']}. Верно?"
    await message.answer(text=text, reply_markup=btn_yes_or_not().as_markup())
    await state.set_state(States.text_or_voice)


@router.callback_query(
    F.data == 'no',
    States.text_or_voice
)
async def retry_send_location(callback: types.CallbackQuery, state: FSMContext):
    print(callback)
    await callback.message.answer(
        text='Попробуйте еще раз отправить локацию',
        reply_markup=btn_to_send_loc()
    )
    await state.set_state(States.input_location)


@router.callback_query(
    F.data == 'yes',
    States.text_or_voice
)
async def text_or_voice(callback: types.CallbackQuery, state: FSMContext):
    markup = InlineKeyboardBuilder()
    btn_1 = types.InlineKeyboardButton(text='Продолжить в текстовом формате', callback_data='text')
    btn_2 = types.InlineKeyboardButton(text='Отправить голосовое сообщение', callback_data='voice')
    markup.add(btn_1, btn_2)
    markup.adjust(1, 1)
    await callback.message.answer(
        text=mes_data['text_or_voice'],
        reply_markup=markup.as_markup()
    )
    await state.set_state(States.advertisements)


@router.callback_query(
    F.data == 'text',
    States.advertisements
)
async def regional_advertisements(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    route = data["road"]
    region = data["region"]

    # запрос на обьяления по области
    request_advertisements = await get_advertisements_for_region(region_name=region)
    if request_advertisements is None:
        # в случае если не получилось обратиться к бэку или статус код 4хх-5хх
        await callback.message.answer(text=mes_data['bad_situation'])
        await state.clear()
        return
    elif len(request_advertisements['advertisements']) == 0:
        await callback.message.answer(text=mes_data['good_situation'])
    else:
        print(request_advertisements)
        count = len(request_advertisements['advertisements'])
        text = ''
        for i in range(count):
            title = request_advertisements['advertisements'][i]['title']
            message = request_advertisements['advertisements'][i]['description']
            text += f'{i + 1}. {title}\n{message}\n\n'
        await callback.message.answer(text)
        # озвучка
        audio = AudioSegment.empty()
        flag = False
        flag, audio = await concate_files(
            count, request_advertisements, callback.from_user.id, flag, audio
        )

        if flag:
            res_path = f"res-{callback.from_user.id}.ogg"
            audio.export(res_path, format="ogg")
            audio = FSInputFile(path=res_path)
            await callback.message.answer_audio(
                audio=audio,
                caption="⚡️⚡️⚡️ Новости ⚡️⚡️⚡️",
            )
            remove(res_path)

    # обьявление для дороги
    answer = await get_request_urgent_message(road_name=route)
    if answer is None:
        # в случае если не получилось обратиться к бэку или статус код 4хх-5хх
        await callback.message.answer(text=mes_data['bad_situation'])
        await state.clear()
        return
    elif len(answer['advertisements']) == 0:
        await callback.message.answer(text=mes_data['good_situation'])
    else:
        print(answer)
        count = len(answer['advertisements'])
        text = ''
        for i in range(count):
            title = answer['advertisements'][i]['title']
            message = answer['advertisements'][i]['description']
            text += f'{i + 1}. {title}\n{message}\n\n'
        await callback.message.answer(text)
        # озвучка
        audio = AudioSegment.empty()
        flag, audio = await concate_files(
            count, answer, callback.from_user.id, False, audio
        )

        if flag:
            res_path = f"res-{callback.from_user.id}.ogg"
            audio.export(res_path, format="ogg")
            audio = FSInputFile(path=res_path)
            await callback.message.answer_audio(
                audio=audio,
                caption="⚡️⚡️⚡️ Новости⚡️⚡️⚡️",
            )
            remove(res_path)

    markup = InlineKeyboardBuilder()
    btn1 = types.InlineKeyboardButton(text='Сообщить', callback_data='report')
    btn2 = types.InlineKeyboardButton(text='Узнать', callback_data='recognize')
    markup.row(btn1, btn2)
    await callback.message.answer(
        text=mes_data['choose_action'],
        reply_markup=markup.as_markup()
    )
    await state.set_state(States.report_or_recognize)
