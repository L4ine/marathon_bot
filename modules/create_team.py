from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from modules.keyboards import choice_menu
from modules.database import get_user_info, add_new_team
from modules.menu_team import teams_list


class StartState(StatesGroup):
	confrim_create_team = State()
	count_players_enter = State()
	players_enter = State()


async def new_team(message: types.Message):
	await message.answer('Вы действительно хотите создать новую команду?', reply_markup = choice_menu)
	await StartState.confrim_create_team.set()


async def team_yes(call: types.CallbackQuery, state: FSMContext):
	info = get_user_info(call.message.chat.id)
	name = info[1]

	if len(info[4].split(',')) == 1:
		count_team = 1
	else:
		count_team = int(sorted(info[4].split(', '))[-1][-1:])+1

	await state.update_data(count_team = count_team)
	await call.message.answer(f'Название вашей новой команды: <b>Команда {name} {count_team}</b>')
	await call.message.answer('Сколько игроков будет в вашей команде (6, 9, 15)?')
	await StartState.count_players_enter.set()


async def count_players_enter(message: types.Message, state: FSMContext):
	if message.text in ['6', '9', '15']:
		await message.answer(f'Введите по очереди имена и фамилии {int(message.text) - 1} игроков, нажимая enter после каждого.')
		await state.update_data(count_players = message.text)
		await StartState.players_enter.set()
	else: 
		await message.answer('Сколько игроков будет в вашей команде (6, 9, 15)?')


async def players_enter(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		players = data.get('players')
		count_team = data.get('count_team')
		count_players = int(data.get('count_players'))

	if players == None:
		name = get_user_info(message.chat.id)[1]
		await state.update_data(players = [name, message.text])
		await message.answer(f'<b>1</b> зарегистрирован, введите следующего')
	
	elif message.text in players:
		return await message.answer('Имена не должны повторяться!')
	
	else:
		players.append(message.text)
		await state.update_data(players = players)

		if len(players) == count_players:
			await message.answer(f'Все {count_players} игроков, включая вас (Тренер), зарегистрированы')
			await message.answer('Всё в порядке? Вы всегда можете зайти в "/teams" и отредактировать каждого игрока')
			
			add_new_team(message.chat.id, players, count_team)
			
			await state.finish()
			return await teams_list(message, state)
		else:
			await message.answer(f'<b>{len(players)-1}</b> зарегистрировано, введите следующего')


async def choice_no(call: types.CallbackQuery, state: FSMContext):
	await call.message.answer('Без проблем, вы всегда можете начать сначала, нажав "/start"')
	await state.finish()


def register_create_team(dp: Dispatcher):
	dp.register_message_handler(new_team, commands = 'newteam')
	dp.register_message_handler(players_enter, state = StartState.players_enter)
	dp.register_message_handler(count_players_enter, state = StartState.count_players_enter)
	dp.register_callback_query_handler(team_yes, text = 'cb_yes', state = StartState.confrim_create_team)
	dp.register_callback_query_handler(choice_no, text = 'cb_no', state = StartState.confrim_create_team)