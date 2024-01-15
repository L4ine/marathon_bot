from datetime import datetime
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext

from modules.keyboards import create_teams_keyboard, create_team_menu_keyboard, button
from modules.database import *
from modules.enter_photo import photos_tip, enter_players_photos
from modules.make_collage import make_best_of
from modules.make_report import make_report


async def teams_list(message: types.Message, state: FSMContext):
	await state.finish()
	await message.answer('Вот ваши команды, нажмите чтобы редактировать:', reply_markup=create_teams_keyboard(message.chat.id))


async def team_menu(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
	team_id = callback_data['id']
	team_info = get_team_info(team_id)
	user_info = get_user_info(call.message.chat.id)
	players_photos = team_info[2].split(', ')

	await state.update_data(team_id=team_id)

	if players_photos.count('') == len(team_info[1].split(', '))-1:
		await photos_tip(call.message)

	elif '' in players_photos:
		await enter_players_photos(call, state)
	
	else:
		count_team = team_id.split('_')[1]
		await call.message.answer(f'Команда {user_info[1]} {count_team} ещё не активирована - активируйте её сейчас', reply_markup=create_team_menu_keyboard(team_id))


async def old_run_stat(call: types.CallbackQuery, state: FSMContext):
	async with state.proxy() as data:
		team_id = data.get('team_id')

	team_info = get_old_run_info(team_id)
	leaders = team_info[3].split(', ')
	leaders_photos = team_info[6].split(', ')

	time_end = team_info[1]
	year_end = datetime.fromtimestamp(time_end).year
	month_end = datetime.fromtimestamp(time_end).month
	day_end = datetime.fromtimestamp(time_end).day

	time_start = time_end - 864000
	year_start = datetime.fromtimestamp(time_start).year
	month_start = datetime.fromtimestamp(time_start).month
	day_start = datetime.fromtimestamp(time_start).day

	await call.message.answer(f'<b>Забег ({day_start}.{month_start}.{year_start} - {day_end}.{month_end}.{year_end}) Статистика:</b>\nЛидер забега: <b>{team_info[3]}</b>\nСнижение веса: <b>{team_info[4]}Кг</b>\n\nСнижение веса в этом забеге: <b>{team_info[5]}Кг</b>')
	await call.message.answer_photo(team_info[7])

	for i in range(len(leaders)):
		await call.message.answer_photo(await make_best_of(leaders[i], leaders_photos[i], 'end', team_id, team_info[2], team_info[8]))


async def send_report(message: types.Message):
	await message.answer('Создаю файл PDF, подождите…')
	date_report = datetime.now().strftime('%d.%m.%Y')
	await message.answer_document((f'Marathon_Statistics_{date_report}.pdf', make_report(message.chat.id)))


def register_menu(dp: Dispatcher):
	dp.register_message_handler(teams_list, commands = 'teams', state = '*')
	dp.register_message_handler(send_report, commands='report', state='*')
	dp.register_callback_query_handler(team_menu, button.filter(action = 'cb_team'))
	dp.register_callback_query_handler(old_run_stat, text = 'cb_old_runs_stat')