from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from modules.database import delete_team, get_user_info
from modules.menu_team import teams_list


class DeleteState(StatesGroup):
	confirm_delete_team = State()


async def delete_team_menu(call: types.CallbackQuery, state: FSMContext):
	await state.update_data(team_id = filter(str.isdigit, call.message.text))
	await call.message.answer('Введите ваш ID чтобы удалить команду')
	await DeleteState.confirm_delete_team.set()


async def confirm_delete(message: types.Message, state: FSMContext):
	super_id = get_user_info(message.chat.id)[3]
	
	if message.text == str(super_id):
		async with state.proxy() as data:
			team_id = data.get('team_id')

		delete_team(message.chat.id, ''.join(team_id))
		
		await message.answer('Команда удалена.')
		
		await state.finish()
		await teams_list(message, state)
	else:
		await message.answer('Неверный номер ID. Попробуйте снова.')


def register_delete_team(dp: Dispatcher):
	dp.register_callback_query_handler(delete_team_menu, text = 'cb_delete_team')
	dp.register_message_handler(confirm_delete, state = DeleteState.confirm_delete_team)