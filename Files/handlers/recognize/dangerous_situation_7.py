from json import load
from aiogram import F, types, Router
from filters.States import States
from support_function import return_to_start
router = Router()

with open(r'/usr/src/app/recurses/text_for_message/data_for_mess.json',
          'r') as data_for_mess:
    mes_data = load(data_for_mess)


@router.callback_query(
    F.data == 'type_7',
    States.recognize
)
async def dangerous_situation(callback: types.CallbackQuery):
    await callback.message.answer(
        text=mes_data['dangerous_situation'],
        reply_markup=return_to_start()
    )
