from json import load
from aiogram import F, types, Router
from filters.States import States
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()

with open(r'../recurses/text_for_message/data_for_recognize.json',
          'r') as data_for_recognize:
    recognize_data = load(data_for_recognize)


@router.callback_query(
    F.data == 'recognize',
    States.report_or_recognize
)
async def choose_que(callback: types.CallbackQuery, state: FSMContext):
    markup = InlineKeyboardBuilder()
    for i in range(7):
        btn = types.InlineKeyboardButton(
            text=recognize_data['questions_for_recognize'][i],
            callback_data=f'type_{i + 1}'
        )
        markup.row(btn)
    await callback.message.answer(
        text=recognize_data['recognize'],
        reply_markup=markup.as_markup()
    )
    await state.set_state(States.recognize)
