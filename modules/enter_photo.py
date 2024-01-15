from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from modules.keyboards import *
from modules.database import *
from modules.make_collage import make_collage
from modules.loader import bot


class EnterPhotoState(StatesGroup):
	add_photo = State()
	add_player_photo = State()


async def photos_tip(message: types.Message):
	await message.answer('Теперь загрузите фотографии игроков, чтобы мы могли создать коллаж вашей команды')
	await message.answer('Вот пример коллажа команды:')
	# await message.answer_photo('AgACAgQAAxkBAAMmYrDGCb9YTZYH2JNpar-XAAG1whAxAALluTEbo_qBUdAYVALR7v7yAQADAgADdwADKAQ')
	await message.answer('Для этого приготовьте фотографии ваших игроков и отредактируйте их перед загрузкой, чтобы создать качественные квадратные портреты (улыбка важна 😀).', reply_markup=enter_photo_menu)


async def enter_players_photos(call: types.CallbackQuery, state: FSMContext):
	async with state.proxy() as data:
		team_id = data.get('team_id')

	if isinstance(call, types.CallbackQuery):
		message = call.message
	else:
		message = call

	team_info = get_team_info(team_id)
	super_photo = get_user_info(message.chat.id)[2]
	players_photos = team_info[2].split(', ')

	need_photo = []

	if super_photo == '':
		need_photo.append(0)

	for i in range(len(players_photos)):
		if players_photos[i] == '':
			need_photo.append(i+1)

	if players_photos.count('') == len(players_photos):
		await message.answer('Вот пример квадратного портрета:')
		# await message.answer_photo('AgACAgQAAxkBAAMlYrDF7HWCx5wz8S8C6XTeFJxfiVAAAua5MRuj-oFRqSr4h8Q1yLsBAAMCAAN4AAMoBA')

	if need_photo == []:
		players_photos.insert(0, super_photo)

		await state.finish()
		await message.answer('Вот коллаж вашей команды')
		await message.answer_photo(await make_collage(players_photos))
		await message.answer('Всё в порядке? Вы всегда можете зайти в "/teams" и отредактировать каждого игрока')
		await message.answer('Вот ваши команды, нажмите чтобы редактировать:', reply_markup = create_teams_keyboard(message.chat.id))
	else:		
		await message.answer('Добавьте недостающие фотографии следующих игроков:', reply_markup = create_players_keyboard(message.chat.id, team_id, 'cb_add_photo', only=need_photo))
		
		await state.update_data(team_info = team_info)
		await EnterPhotoState.add_photo.set()


async def add_photo(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
	async with state.proxy() as data:
		team_info = data.get('team_info')

	player_id = callback_data['id']
	players_name = team_info[1].split(', ')
	name = players_name[int(player_id)]

	await call.message.answer(f'Пошлите сюда фото для <b>{name}</b>')
	await state.update_data(players_photos = team_info[2], player_id = player_id, name = name)
	await EnterPhotoState.add_player_photo.set()


async def add_player_photo(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		team_id = data.get('team_id')
		players_photos = data.get('players_photos')
		player_id = data.get('player_id')
		name = data.get('name')

	players_photos = players_photos.split(', ')

	if player_id == '0':
		update_trainer_photo(message.chat.id, message.photo[-1].file_id)
	else:
		players_photos[int(player_id)-1] = message.photo[-1].file_id
		update_players_photos(team_id, players_photos)

	if players_photos.count('') == 0:
		await message.answer(f'<b>{name} фото сохранено</b>')
	else:
		await message.answer(f'<b>{name} фото сохранено</b>,\nвыберите другого игрока...')

	await enter_players_photos(message, state)


def register_enter_photo(dp: Dispatcher):
	dp.register_callback_query_handler(enter_players_photos, text = 'cb_enter_photo')
	dp.register_callback_query_handler(add_photo, button.filter(action = 'cb_add_photo'), state = EnterPhotoState.add_photo)
	dp.register_message_handler(add_player_photo, state = EnterPhotoState.add_player_photo, content_types = ['photo'])