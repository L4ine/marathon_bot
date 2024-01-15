from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from modules.database import *
from modules.keyboards import *
from modules.menu_team import teams_list
from modules.make_collage import make_collage


class EnterHelperState(StatesGroup):
	add_helper = State()
	add_client_helper = State()


async def enter_helper(call: types.CallbackQuery, state: FSMContext):
	async with state.proxy() as data:
		team_id = data.get('team_id')

	await call.message.answer('Чтобы выбрать Помощника Тренера мы рекомендуем вам поговорить со всеми игроками и идентифицировать наиболее активного, который в будущем сам хочет стать Тренером')
	await call.message.answer('Выберите Помощника Тренера', reply_markup = create_helper_keyboard(call.message.chat.id, team_id))
	await call.message.answer('Выберите одну из опций выше')
	await EnterHelperState.add_helper.set()


async def choice_helper(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
	async with state.proxy() as data:
		team_id = data.get('team_id')

	team_info = get_team_info(team_id)

	player_id = callback_data['id']
	player_name = call.message.reply_markup.inline_keyboard[int(player_id)][0].text
	
	players_photos = team_info[2].split(', ')
	current_helper = team_info[3]
	
	players_photos.insert(0, get_user_info(call.message.chat.id)[2])

	if player_id == '0':
		await call.message.answer('Тренер не может быть Помощником Тренера')
	
	elif player_name[-4:] == '(ПТ)':
		set_helper(team_id, '')
		await call.message.answer(f'{player_name[:-4]} более не Помощник Тренера')
	
	elif player_name != current_helper:
		await state.finish()
		
		set_helper(team_id, player_name)
		
		await call.message.answer(f'{player_name} назначен Помощником Тренера')
@		await call.message.answer_photo(await make_collage(players_photos, team_id))
		
		await state.update_data(team_id = team_id)
		return await enter_helper_clients(call, state)

	await call.message.answer_photo(await make_collage(players_photos, team_id))
	await teams_list(call.message, state)


async def enter_helper_clients(call: types.CallbackQuery, state: FSMContext):
	async with state.proxy() as data:
		team_id = data.get('team_id')
	
	team_info = get_team_info(team_id)
	current_helper = str(team_info[3])
	clients = team_info[1].split(', ')[1:]

	if current_helper in clients:
		clients.remove(current_helper)

	await call.message.answer('Важно: игроки Помощника Тренера - это Клиенты «Родник здоровья», которых он сам и привел.')
	await call.message.answer('Выберите Клиентов Помощника Тренера', reply_markup = create_clients_keyboard(team_info, clients))
	await call.message.answer('Выберите одну из опций выше')
	await EnterHelperState.add_client_helper.set()


async def choice_helper_client(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
	async with state.proxy() as data:
		team_id = data.get('team_id')

	team_info = get_team_info(team_id)

	players_name = team_info[1].split(', ')
	players_photos = team_info[2].split(', ')
	current_clients = team_info[4].split(', ')
	
	player_name = players_name[int(callback_data['id'])]
	
	players_photos.insert(0, get_user_info(call.message.chat.id)[2])

	if player_name in current_clients:
		current_clients.remove(player_name)
		await call.message.answer(f'{player_name} более не Клиент Помощника Тренера')
	else:
		current_clients.append(player_name)
		await call.message.answer(f'{player_name} теперь Клиент Помощника Тренера')
	
	set_helper_clients(team_id, ', '.join(current_clients))

	await state.finish()
	await state.update_data(team_id = team_id)
	
	await call.message.answer_photo(await make_collage(players_photos, team_id))
	await enter_helper_clients(call, state)


def register_enter_helper(dp: Dispatcher):
	dp.register_callback_query_handler(enter_helper, text = 'cb_trainer_helper')
	dp.register_callback_query_handler(enter_helper_clients, text = 'cb_helper_clients', state = '*')
	dp.register_callback_query_handler(choice_helper, button.filter(action = 'cb_enter_helper'), state = EnterHelperState.add_helper)
	dp.register_callback_query_handler(choice_helper_client, button.filter(action = 'cb_enter_client'), state = EnterHelperState.add_client_helper)