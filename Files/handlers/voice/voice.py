from json import load
from os import remove
from aiogram import F, types, Router, Bot
from Files.filters.States import States
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext

from Files.handlers.recognize.attractions_5 import attractions
from Files.handlers.recognize.car_service_3 import car_service
from Files.handlers.recognize.dangerous_situation_7 import dangerous_situation
from Files.handlers.recognize.gas_station_2 import gas_station
from Files.handlers.recognize.meal_1 import meal
from Files.handlers.recognize.parking_lot_4 import parking_lot
from Files.handlers.report.illegal_actions_3 import illegal_actions
from Files.handlers.report.road_block_4 import road_block
from Files.handlers.report.road_deficiencies_2 import road_deficiencies
from Files.handlers.report.traffic_accident_1 import traffic_accident
from Files.request import get_audio_label

router = Router()

with open(r"../recurses/text_for_message/data_for_mess.json", "r") as data_for_mess:
    mes_data = load(data_for_mess)

with open(r"../recurses/text_for_message/callback_data.json", "r") as callback_mes_data:
    callback_data = load(callback_mes_data)


@router.callback_query(F.data == "voice", States.advertisements)
async def voice_requirements(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(text=mes_data["voice_requirements"])
    await state.set_state(States.input_voice)


@router.message(F.voice, States.input_voice)
async def voice_processing(message: types.Message, state: FSMContext, bot: Bot):
    file_path = f"{message.voice.file_id}.ogg"
    await bot.download(message.voice, destination=file_path)
    await state.update_data({"file_name": file_path})

    # запрос для отправки гс на ии
    skip_information = await get_audio_label(file_path)  # полученный ответ
    await state.update_data({"to_do": skip_information[0]})

    text = f"Вы хотите перейти к действию под названием: {skip_information[0]}. Верно?"
    markup = InlineKeyboardBuilder()
    btn_1 = types.InlineKeyboardButton(text="Да", callback_data="voice_good")
    btn_2 = types.InlineKeyboardButton(text="Нет", callback_data="voice_bad")
    markup.add(btn_1, btn_2)
    markup.adjust(2)

    await message.answer(text=text, reply_markup=markup.as_markup())
    await state.set_state(States.voice_right_or_not)


@router.callback_query(F.data == "voice_bad", States.voice_right_or_not)
async def voice_bad(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Попробуйте отправить голосовое сообщение еще раз")
    await state.set_state(States.input_voice)


@router.callback_query(F.data == "voice_good", States.voice_right_or_not)
async def voice_good(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    to_do = data["to_do"]
    file_name = data["file_name"]

    if to_do == callback_data["all_type_actions"]["report_traffic_accident"]:
        await traffic_accident(callback=callback, state=state)
        await state.set_state(States.input_description_for_traffic_accident)
    elif to_do == callback_data["all_type_actions"]["report_road_deficiencies"]:
        await road_deficiencies(callback=callback, state=state)
        await state.set_state(States.output_text_for_road_deficiencies)

    elif to_do == callback_data["all_type_actions"]["report_illegal_actions"]:
        await illegal_actions(callback=callback, state=state)
        await state.set_state(States.input_description_for_illegal_actions)
    elif to_do == callback_data["all_type_actions"]["report_road_block"]:
        await road_block(callback=callback, state=state)
        await state.set_state(States.input_description_for_road_block)
    elif to_do == callback_data["all_type_actions"]["recognize_meal"]:
        await meal(callback=callback, state=state)
        await state.set_state(States.recognize)
    elif to_do == callback_data["all_type_actions"]["recognize_gas_station"]:
        await gas_station(callback=callback, state=state)
        await state.set_state(States.recognize)
    elif to_do == callback_data["all_type_actions"]["recognize_car_service"]:
        await car_service(callback=callback, state=state)
        await state.set_state(States.recognize)
    elif to_do == callback_data["all_type_actions"]["recognize_parking_lot"]:
        await parking_lot(callback=callback, state=state)
        await state.set_state(States.recognize)
    elif to_do == callback_data["all_type_actions"]["recognize_attractions"]:
        await attractions(callback=callback, state=state)
        await state.set_state(States.recognize)
    elif to_do == callback_data["all_type_actions"]["recognize_dangerous_situation"]:
        await dangerous_situation(callback)
        await state.set_state(States.report)
    else:
        await callback.message.answer(text=mes_data["bad_situation"])
        await state.set_state(States.input_voice)
    remove(file_name)
    print(f"voice_good: Current state: {await state.get_state()}")
