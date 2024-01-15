from aiogram import types

from modules.database import *
from aiogram.utils.callback_data import CallbackData

confirm_menu = types.InlineKeyboardMarkup()
confirm_menu.add(types.InlineKeyboardButton('ПРИНЯТЬ', callback_data = 'cb_confirm'))

choice_menu = types.InlineKeyboardMarkup()
choice_menu.add(types.InlineKeyboardButton('Да', callback_data = 'cb_yes'), types.InlineKeyboardButton('Нет', callback_data = 'cb_no'))

restart_menu = types.InlineKeyboardMarkup()
restart_menu.add(types.InlineKeyboardButton('Перезапустить день', callback_data = 'cb_update_day'))

change_helper_menu = types.InlineKeyboardMarkup()
change_helper_menu.add(types.InlineKeyboardButton('Да', callback_data = 'cb_trainer_helper'), types.InlineKeyboardButton('Нет', callback_data = 'cb_helper_no'))

enter_photo_menu = types.InlineKeyboardMarkup()
enter_photo_menu.add(types.InlineKeyboardButton('ОК', callback_data = 'cb_enter_photo'))

button = CallbackData('text', 'id', 'action')

def create_team_menu_keyboard(team_id):
	team_menu_keyboard = types.InlineKeyboardMarkup()
	
	runs = get_run_info(team_id)[1]
	
	team_menu_keyboard.add(types.InlineKeyboardButton(f'Начать забег #{runs+1}', callback_data = 'cb_start'), types.InlineKeyboardButton('Редактировать игроков', callback_data = 'cb_edit_team'))
	team_menu_keyboard.add(types.InlineKeyboardButton('Помощник Тренера', callback_data = 'cb_trainer_helper'), types.InlineKeyboardButton('Удалить Команду', callback_data = 'cb_delete_team'))

	if runs >= 1:
		team_menu_keyboard.add(types.InlineKeyboardButton('Статистика предыдущих забегов', callback_data = 'cb_old_runs_stat'))

	return team_menu_keyboard

def create_teams_keyboard(user_id):
	teams_list_keyboard = types.InlineKeyboardMarkup()
	
	info = get_user_info(user_id)

	name = info[1]
	teams = info[4].split(', ')[1:]

	for team in teams:
		team_info = get_team_info(team)
		runs = get_run_info(team)
		count_team = team.split('_')[1]

		if team_info[5] == 0:
			active = 'Команда не активирована'
			teams_list_keyboard.add(types.InlineKeyboardButton(f'Команда {name} {count_team} (Неактивная), Забег: #{runs[1]+1}', callback_data = button.new(id = team, action = 'cb_team')))
		
		else:
			active = 'Активная'
			teams_list_keyboard.add(types.InlineKeyboardButton(f'Команда {name} {count_team} (Активная), Забег: #{runs[1]+1}, День: #{runs[2]}', callback_data = button.new(id = team, action = 'cb_marathon')))

	return teams_list_keyboard


def create_players_keyboard(user_id, team_id, action, only = None):
	players_list_keyboard = types.InlineKeyboardMarkup()
	name = get_user_info(user_id)[1]
	team_info = get_team_info(team_id)
	players = team_info[1].split(', ')

	if only == None:
		for i in range(len(players)):
			players_list_keyboard.add(types.InlineKeyboardButton(players[i], callback_data = button.new(id = i, action = action)))

	else:
		for i in only:
			players_list_keyboard.add(types.InlineKeyboardButton(players[i], callback_data = button.new(id = i, action = action)))

	return players_list_keyboard


def create_clients_keyboard(team_info, clients):
	clients_list_keyboard = types.InlineKeyboardMarkup()

	current_clients = team_info[4].split(', ')
	players = team_info[1].split(', ')

	for client in clients:
		if client in current_clients:
			name = client+'(КлПТ)'
		else:
			name = client

		clients_list_keyboard.add(types.InlineKeyboardButton(name, callback_data = button.new(id = players.index(client), action = 'cb_enter_client')))

	clients_list_keyboard.add(types.InlineKeyboardButton('Начать забег', callback_data = 'cb_helper_no'))

	return clients_list_keyboard


def create_helper_keyboard(user_id, team_id):
	helper_list_keyboard = types.InlineKeyboardMarkup()
	team_info = get_team_info(team_id)
	players = team_info[1].split(', ')
	current_helper = str(team_info[3])

	helper_list_keyboard.add(types.InlineKeyboardButton(get_user_info(user_id)[1]+'(К)', callback_data = button.new(id = 0, action = 'cb_enter_helper')))

	for i in range(1, len(players)):
		if players[i] == current_helper:
			name = players[i]+'(ПТ)'
		else:
			name = players[i]

		helper_list_keyboard.add(types.InlineKeyboardButton(name, callback_data = button.new(id = i, action = 'cb_enter_helper')))

	if current_helper != '':
		helper_list_keyboard.add(types.InlineKeyboardButton('Изменить Клиентов Помощника Тренера', callback_data = 'cb_helper_clients'))

	return helper_list_keyboard


def create_players_weight_keyboard(team_id):
	players_weight_keyboard = types.InlineKeyboardMarkup()
	team_info = get_team_info(team_id)
	players = team_info[1].split(', ')

	run_info = get_run_info(team_id)
	current_day = run_info[2]
	players_weight = run_info[int(current_day)+4].split(', ')

	for i in range(len(players)):
		if players_weight[i] != '':
			players_weight_keyboard.add(types.InlineKeyboardButton(players[i]+' ('+players_weight[i]+' Кг)', callback_data = button.new(id = i, action = 'cb_add_weight')))
		else:
			players_weight_keyboard.add(types.InlineKeyboardButton(players[i], callback_data=button.new(id = i, action = 'cb_add_weight')))

	return players_weight_keyboard
