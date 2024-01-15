from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from modules.database import *
from modules.menu_team import teams_list
from modules.keyboards import create_players_keyboard, button
from modules.make_collage import make_collage
from modules.loader import bot


class EditState(StatesGroup):
	new_player_name = State()
	new_player_photo = State()


async def edit_team(call: types.CallbackQuery, state: FSMContext):
	async with state.proxy() as data:
		team_id = data.get('team_id')

	await call.message.answer('Вот все игроки этой команды, выберите игрока для редактирования', reply_markup=create_players_keyboard(call.message.chat.id, team_id, 'cb_edit_player'))
	await call.message.answer('Выберите игрока для редактирования')


async def edit_player(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
	player_id = callback_data['id']
	name = call.message.reply_markup.inline_keyboard[int(player_id)][0].text

	if player_id != '0':
		await call.message.answer(f'Введите имя нового игрока вместо <b>{name}</b>')
		await EditState.new_player_name.set()
	else:
		await call.message.answer(f'Пошлите сюда фото для <b>{name}</b>')
		await EditState.new_player_photo.set()
	
	await state.update_data(player_id = player_id, name = name)


async def new_player_name(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		team_id = data.get('team_id')
		player_id = data.get('player_id')
		name = data.get('name')

	team_info = get_team_info(team_id)
	players_name = team_info[1].split(', ')
	current_clients = team_info[4]
	current_helper = team_info[3]

	if message.text in players_name:
		players_name.remove(message.text)

@	if message.text not in players_name:
		if players_name[int(player_id)] == current_helper:
			set_helper(team_id, message.text)

		elif players_name[int(player_id)] in current_clients:
			current_clients = current_clients.replace(players_name[int(player_id)], message.text)
			set_helper_clients(team_id, current_clients)

		players_name[int(player_id)] = message.text
		
		update_players_names(team_id, players_name)
			
		await message.answer(f'Игрок <b>{name}</b> заменён на <b>{message.text}</b>')
		await message.answer(f'Пошлите сюда фото для <b>{message.text}</b>')
		
		await state.update_data(name = message.text)
		await EditState.new_player_photo.set()
	else:
		await message.answer('Имена не должны повторяться!')


async def new_player_photo(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		player_id = data.get('player_id')
		team_id = data.get('team_id')
		name = data.get('name')

	team_info = get_team_info(team_id)
	players_photos = team_info[2].split(', ')

	if player_id != '0':
		players_photos[int(player_id)-1] = message.photo[-1].file_id
		
		update_players_photos(team_id, players_photos)
		
		players_photos.insert(0, get_user_info(message.chat.id)[2])
	else:
		update_trainer_photo(message.chat.id, message.photo[-1].file_id)
		
		players_photos.insert(0, message.photo[-1].file_id)

	await message.answer(f'<b>{name} фото сохранено</b>')
	await message.answer('Вот коллаж вашей команды')
	await message.answer_photo(await make_collage(players_photos))
	await message.answer('Всё в порядке? Вы всегда можете зайти в "/teams" и отредактировать каждого игрока')
	
	await state.finish()
	await teams_list(message, state)


def register_edit_team(dp: Dispatcher):
	dp.register_callback_query_handler(edit_team, text = 'cb_edit_team')
	dp.register_callback_query_handler(edit_player, button.filter(action = 'cb_edit_player'))

	dp.register_message_handler(new_player_name, state = EditState.new_player_name)
	dp.register_message_handler(new_player_photo, state = EditState.new_player_photo, content_types = ['photo'])