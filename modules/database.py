import sqlite3, time
from aiogram.contrib.fsm_storage.memory import MemoryStorage


# Подключение базы данных.
print('Подключение базы данных...')
DB = sqlite3.connect('data/teams.db', check_same_thread=False)
Cursor = DB.cursor()

# Подключение хранилища для FMS.
print('Подключение хранилища...')
storage = MemoryStorage()


def get_all_user():
	return Cursor.execute('SELECT id FROM supervisors').fetchone()


def get_user_info(user):
	return Cursor.execute('SELECT * FROM supervisors WHERE id = ?', [str(user)]).fetchone()


def get_team_info(team_id):
	return Cursor.execute('SELECT * FROM teams WHERE id = ?', [str(team_id)]).fetchone()


def get_run_info(team_id):
	return Cursor.execute('SELECT * FROM runs WHERE id = ?', [str(team_id)]).fetchone()


def get_old_run_info(team_id):
	return Cursor.execute('SELECT * FROM old_run_stats WHERE id = ?', [str(team_id)]).fetchone()


def add_new_user(user, name, super_id):
	Cursor.execute('INSERT INTO supervisors VALUES (?, ?, "", ?, "")', [str(user), str(name), str(super_id)])
	DB.commit()


@def add_new_team(user, players, team_id):
	teams_id = get_user_info(user)[4]
	photo_comma = (len(players) - 2) * ', '
	run_comma = (len(players) - 1) * ', '
	Cursor.execute('INSERT INTO teams VALUES (?, ?, ?, "", "", 0)', [str(user)+'_'+str(team_id), ', '.join(players), photo_comma])
	Cursor.execute('INSERT INTO runs VALUES (?, 0, 0, 0, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', [str(user)+'_'+str(team_id), run_comma, run_comma, run_comma, run_comma, run_comma, run_comma, run_comma, run_comma, run_comma, run_comma, run_comma])
	Cursor.execute('UPDATE supervisors SET teams_id = ? WHERE id = ?', [teams_id+', '+str(user)+'_'+str(team_id), user])
	DB.commit()


def update_trainer_photo(user, photo):
	Cursor.execute('UPDATE supervisors SET photo = ? WHERE id = ?', [photo, user])
	DB.commit()


def update_players_names(team_id, names):
	Cursor.execute('UPDATE teams SET players = ? WHERE id = ?', [', '.join(names), team_id])
	DB.commit()


def update_players_photos(team_id, photos):
	Cursor.execute('UPDATE teams SET photos = ? WHERE id = ?', [', '.join(photos), team_id])
	DB.commit()


def update_players_weight(team_id, day, players_weight):
	Cursor.execute(f'UPDATE runs SET day_{day} = ? WHERE id = ?', [', '.join(players_weight), team_id])
	DB.commit()


def set_day_close(team_id, state):
	Cursor.execute('UPDATE runs SET day_close = ? WHERE id = ?', [state, team_id])
	DB.commit()


def set_team_action(team_id, action):
	Cursor.execute('UPDATE teams SET action = ? WHERE id = ?', [action, team_id])
	DB.commit()


def set_helper(team_id, name):
	set_helper_clients(team_id, '')
	Cursor.execute('UPDATE teams SET helper = ? WHERE id = ?', [name, team_id])
	DB.commit()


def set_helper_clients(team_id, names):
	Cursor.execute('UPDATE teams SET helper_clients = ? WHERE id = ?', [names, team_id])
	DB.commit()


def delete_team(user, team_id):
	user_teams = get_user_info(user)[4].split(', ')
	user_teams.remove(str(user)+'_'+str(team_id))
	Cursor.execute('DELETE FROM teams WHERE id = ?', [str(user)+'_'+str(team_id)])
	Cursor.execute('UPDATE supervisors SET teams_id = ? WHERE id = ?', [', '.join(user_teams), user])
	DB.commit()


def check_user_in_db(user):
	if get_user_info(user) is None:
		return False
	else:
		return True


async def update_all_day():
	complete_run = Cursor.execute('SELECT id FROM runs WHERE current_day = 10').fetchone()

	if complete_run != None:
		Cursor.execute('UPDATE runs SET total_runs = total_runs + 1 WHERE current_day = 10')
		
		for team in complete_run:
			Cursor.execute('UPDATE teams SET action = 0 WHERE id = ?', [team])

			run_info = get_run_info(team)
			user_info = get_user_info(team.split('_')[0])
			team_info = get_team_info(team)

			players_name = team_info[1].split(', ')
			players_photos = team_info[2].split(', ')
			players_photos.insert(0, user_info[2])

			current_day = run_info[2]

			first_weight = run_info[4].split(', ')

			best_of_run = [[], []]
			best_of_day = []

			sum_lost_weight = [[0 * i for i in range(9)], [0 * i for i in range(9)]]

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

					lost_weight.append(round(float(day_weight[i]) - float(last_weight[i]), 1))

				for i in range(len(lost_weight)):
					sum_lost_weight[0][i] += lost_weight[i]
					sum_lost_weight[1][i] += lost_weight[i]/float(first_weight[i])*100

			max_sum_lost_weight_kg = min(sum_lost_weight[0])
			max_sum_lost_weight_pr = min(sum_lost_weight[1])

			for i in range(len(sum_lost_weight[0])):
				if float(sum_lost_weight[0][i]) == float(max_sum_lost_weight_kg):
					best_of_run[0].append(players_name[i])

				if float(sum_lost_weight[1][i]) == float(max_sum_lost_weight_pr):
					best_of_run[1].append(players_name[i])

			leaders_photos = []

			for i in best_of_run[0]:
				leaders_photos.append(players_photos[players_name.index(i)])

			collage = await make_finish(players_photos, 3, 3, team, user_info[1], sum(sum_lost_weight[0]), sum_lost_weight[0], [[], best_of_run[0]])

			Cursor.execute('INSERT INTO old_run_stats VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', [team, str(time.time()), user_info[1], ', '.join(best_of_run[0]), str(max_sum_lost_weight_kg), str(sum(sum_lost_weight[0])), ', '.join(leaders_photos), collage, run_info[1]])
			
		Cursor.execute('''UPDATE runs SET day_0 = ", , , , , , , , ", 
										day_1 = ", , , , , , , , ", 
										day_2 = ", , , , , , , , ",
										day_3 = ", , , , , , , , ",
										day_4 = ", , , , , , , , ",
										day_5 = ", , , , , , , , ",
										day_6 = ", , , , , , , , ",
										day_7 = ", , , , , , , , ",
										day_8 = ", , , , , , , , ",
										day_9 = ", , , , , , , , ",
										day_10 = ", , , , , , , , "
		 					WHERE current_day = 10'''
		)

		Cursor.execute('UPDATE runs SET current_day = 0 WHERE current_day = 10')

	for i in range(9, -1, -1):
		if i == 0:
			Cursor.execute('UPDATE runs SET current_day = 1 WHERE day_close = 1')
		else:
			Cursor.execute('UPDATE runs SET current_day = ? WHERE current_day = ?', [i+1, i])

	Cursor.execute('UPDATE runs SET day_close = 0 WHERE day_close = 1')
	DB.commit()
	logging.warning('Days updated successfully...')