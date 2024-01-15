import datetime, sqlite3
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from modules.keyboards import *
from modules.database import *
from modules.make_collage import *
from modules.menu_team import teams_list
from modules.make_report import make_report
from modules.loader import logging


class EnterWeightState(StatesGroup):
	add_weight = State()


async def start_run(call: types.CallbackQuery):
	await call.message.answer('Важно выбрать Помощника Тренера в каждой Команде. Это поможет вам найти и развить следующего потенциального Тренера')
	await call.message.answer('Вы хотите выбрать или изменить Помощника Тренера или его игроков?', reply_markup = change_helper_menu)
	

async def first_day_run(call: types.CallbackQuery, state: FSMContext):
	async with state.proxy() as data:
		team_id = data.get('team_id')

	run_info = get_run_info(team_id)
	day_close = run_info[3]
	action = get_team_info(team_id)[5]

	await state.update_data(run_info = run_info)
	
	set_team_action(team_id, 1)

	if day_close == 1:
		await end_day(call.message, team_id)
	else:
		await call.message.answer('Введите начальный вес (день 0), выберите игрока из списка', reply_markup = create_players_weight_keyboard(team_id))


async def marathon(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
	team_id = callback_data['id']
	run_info = get_run_info(team_id)

	await state.update_data(team_id = team_id, run_info = run_info)

	if run_info[2] == 0:
		await first_day_run(call, state)
	else:
		if run_info[3] == 0:
			await call.message.answer('День ещё не закрыт, выберите игрока для регистрации веса', reply_markup = create_players_weight_keyboard(team_id))
		else:
			await end_day(call.message, team_id)


async def enter_weight(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
	async with state.proxy() as data:
		team_id = data.get('team_id')
		run_info = data.get('run_info')

	player_id = callback_data['id']
	players_name = get_team_info(team_id)[1].split(', ')
	name = players_name[int(player_id)]
	current_day = run_info[2]

	if current_day == 0:
		await call.message.answer(f'Какой вес у <b>{name}</b> сегодня?')
	else:
		last_weight = run_info[int(current_day)+3].split(', ')[int(player_id)]

		if last_weight == '':
			for day in range(current_day, -1, -1):
				last_weight_prev = run_info[4 + day].split(', ')[int(player_id)]

				if last_weight_prev == '':
					continue
				else:
					last_weight = last_weight_prev
					break

		await call.message.answer(f'Какой вес у <b>{name}</b> сегодня (последний отчет: {last_weight})?')
		await state.update_data(last_weight = last_weight)

	await state.update_data(player_id=player_id, name=name)
	await EnterWeightState.add_weight.set()


async def add_weight(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		team_id = data.get('team_id')
		player_id = data.get('player_id')
		name = data.get('name')
		last_weight = data.get('last_weight')
		run_info = data.get('run_info')

	try:
		if last_weight != None:
			if abs(float(message.text) - float(last_weight)) > 2:
				return await message.answer(f'Неверный вес. Изменение за один день не может быть таким значительным (вчерашний вес был <b>{last_weight}</b>Кг)') 

		if float(message.text) <= 200 and float(message.text) >= 40:
			run_info = get_run_info(team_id)
			current_day = run_info[2]
			players_weight = run_info[int(current_day)+4].split(', ')
			players_weight[int(player_id)] = str(float(message.text))
			update_players_weight(team_id, current_day, players_weight)

			if players_weight.count('') == 0:
				await state.finish()
				await state.update_data(team_id = team_id)
				await message.answer('День закрыт')
				await end_day(message, team_id)
			else:
				await message.answer(f'Принято. Вес игрока <b>{name}</b> - <b>{players_weight[int(player_id)]}</b>Кг. Выберите другого игрока для введения веса.', reply_markup = create_players_weight_keyboard(team_id))
				await state.finish()
				await state.update_data(team_id = team_id, run_info = run_info)
		else:
			await message.answer('Неверный вес') 
			await message.answer(f'Какой вес у <b>{name}</b> сегодня?')

	except ValueError:
		await message.answer('Неверный вес') 
		await message.answer(f'Какой вес у <b>{name}</b> сегодня?')


async def end_day(message: types.Message, team_id):
	set_day_close(team_id, 1)

	user_info = get_user_info(message.chat.id)
	team_info = get_team_info(team_id)
	players_name = team_info[1].split(', ')
	players_photos = team_info[2].split(', ')
	players_photos.insert(0, user_info[2])

	run_info = get_run_info(team_id)
	current_day = int(run_info[2])
	players_weight = run_info[current_day+4].split(', ')

	if current_day == 0:
		text = f'Это нулевой день этого забега, новые данные отсутствуют. Не забудьте добавить вес всех игроков завтра утром\n\nЗабег #{run_info[1]+1}, Начальный вес\n\n'

		for i in range(len(players_name)):
			text += f'<b>{players_name[i]}</b>: {players_weight[i]}Кг.\n'
		
		await message.answer(text)
		await message.answer_photo(await make_start(players_photos, team_id, user_info[1]))

		await message.answer('Каждый вечер вы будете получать отчёт.\nНе забудьте ввести вес каждого игрока завтра утром')
	else:
		first_weight = run_info[4].split(', ')

		best_of_run = [[], []]
		best_of_day = []

		sum_lost_weight = [[0 * i for i in range(len(players_name))], [0 * i for i in range(len(players_name))]]

		for day in range(current_day):
			day_weight = run_info[5 + day].split(', ')
			last_weight = run_info[4 + day].split(', ')

			lost_weight = []

			for i in range(len(day_weight)):
				if day_weight[i] == '':
					lost_weight.append(0)
					continue
				
				if last_weight[i] == '':
					for d in range(day - 1, -1, -1):
						last_weight_prev = run_info[4 + d].split(', ')[i]
						if last_weight_prev == '':
							continue
						else:
							last_weight[i] = last_weight_prev
							break

				lost_weight.append(round(float(last_weight[i]) - float(day_weight[i]), 1))

			max_lost_weight = max(lost_weight)

			if lost_weight.count(0) != len(lost_weight):
				for i in range(len(lost_weight)):
					sum_lost_weight[0][i] += lost_weight[i]
					sum_lost_weight[1][i] += lost_weight[i]/float(first_weight[i])*100

					if day == current_day - 1:
						if float(lost_weight[i]) == float(max_lost_weight):
							best_of_day.append(players_name[i])


		if sum_lost_weight[0].count(0) != len(sum_lost_weight[0]):
			max_sum_lost_weight_kg = max(sum_lost_weight[0])
			max_sum_lost_weight_pr = max(sum_lost_weight[1])

			for i in range(len(sum_lost_weight[0])):
				if float(sum_lost_weight[0][i]) == float(max_sum_lost_weight_kg):
					best_of_run[0].append(players_name[i])

				if float(sum_lost_weight[1][i]) == float(max_sum_lost_weight_pr):
					best_of_run[1].append(players_name[i])

		await message.answer(f'<b>Команда {user_info[1]} {team_id.split("_")[1]}</b>\nЗабег #{run_info[1]+1}, День #{current_day}:\n\nЛидер дня: <b>{", ".join(best_of_day)}</b>\nСнижение веса: <b>{sum(sum_lost_weight[0]):.2f}Кг</b>', reply_markup=restart_menu)
		await message.answer_photo(await make_end_day(players_photos, team_id, [round(float(players_weight[i]) - float(last_weight[i]), 2) for i in range(len(players_weight))], [best_of_day, best_of_run[0]]))

		for leader in best_of_day:
			await message.answer_photo(await make_best_of(leader, players_photos[players_name.index(leader)], 'day', team_id, user_info[1]))

		for leader in best_of_run[0]:
			await message.answer_photo(await make_best_of(leader, players_photos[players_name.index(leader)], 'run', team_id, user_info[1]))

		if current_day in [3, 8]:
			await message.answer('Разгрузочный день!')


async def restart_day(call: types.CallbackQuery, state: FSMContext):
	async with state.proxy() as data:
		team_id = data.get('team_id')

	set_day_close(team_id, 0)
	await call.message.answer('День обновлён')


async def notify_user(dp: Dispatcher):
	users = get_all_user()

	for user in users:
		await dp.bot.send_message(user, 'Не забудьте сообщить вес всех игроков до конца дня')
		await dp.bot.send_message(user, 'Вот ваши команды, нажмите чтобы редактировать:', reply_markup=create_teams_keyboard(user))


async def report_user(dp: Dispatcher):
	users = get_all_user()
	date_report = datetime.datetime.now().strftime('%d.%m.%Y')

	for user in users:
		await dp.bot.send_message(user, 'Вот отчёт PDF со статистикой команд')
		await dp.bot.send_document(user, (f'Marathon_Statistics_{date_report}.pdf', make_report(user)))


def register_start_run(dp: Dispatcher):
	dp.register_callback_query_handler(start_run, text='cb_start', state='*')
	dp.register_callback_query_handler(restart_day, text='cb_update_day')
	dp.register_callback_query_handler(marathon, button.filter(action='cb_marathon'))
	dp.register_callback_query_handler(first_day_run, text='cb_helper_no', state='*')
	dp.register_callback_query_handler(enter_weight, button.filter(action='cb_add_weight'), state='*')
	dp.register_message_handler(add_weight, state=EnterWeightState.add_weight)