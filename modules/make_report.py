import pdfkit, datetime, time
from modules.database import *


def make_report(user_id):
	user_info = get_user_info(user_id)
	trainer = user_info[1]
	teams = user_info[4].split(', ')
	date_report = datetime.datetime.now().strftime('%d.%m.%Y')

	baza = '''<!DOCTYPE html>
	<html>
	<meta name="pdfkit-orientation" content="Landscape"/>
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
	<head>
		<style type="text/css">
			* { 
				font-family:Arial, sans-serif;
			}

			#title_header {
				font-size: 26px;
				padding-bottom: 10px;
			}

			#title {
				display: block;
				margin-left: -8px;
			}

			.oboz_table td, .team_table, .title_table {
				text-align: left;
				font-size: 18px;
			}

			.team {
				margin-bottom: 40px;
	        }
	        

			.oboz {
				margin-top: 20px;
				margin-bottom: 20px;
				margin-left: 100px;
			}

			.team, .oboz {
				width: fit-content;
				height: fit-content;
				float: left;

				border-style: solid;
				border-color: #9b9b9b;
				border-width: 2px;
			}

			#info_header {
				font-size: 26px;
				padding-top: 5px;
				padding-bottom: 20px;
			}

			.team .header {
				padding-left: 10px;
				padding-top: 10px;
				padding-bottom: 5px;
				font-size: 22px;
			}

			.oboz .header {
				padding-top: 10px;
				padding-bottom: 2px;
				font-size: 18px;
				text-align: center;
			}

			.tg  {
				border-collapse: collapse;
				border-spacing: 5px;
			}

			.tg th {
				border-style: solid;
				border-width: 2px;
				font-size: 14px;
				overflow: hidden;
				padding: 10px 5px;
			}

			.tg td {
				border-style:solid;
				border-width:2px;
				font-size:14px;
				overflow:hidden;
				padding:5px 5px;
			}

			.tg * {
				border-color: #9b9b9b;
				text-align: center;
				vertical-align: middle;
			}

			.tg .tg-45l0{background-color:#cccccc;font-weight:bold;}
			.tg .tg-jes8{background-color:#cccccc;font-weight:bold;text-align: left;}
			.tg .tg-qcst{font-weight:bold;}
		</style>
	</head>
	<body>
		<div id="title_header">
			<b>Отчёт по командам</b>
		</div>

		<div id="title">
			<table class="title_table" cellspacing="8">
				<colgroup>
					<col style="width: 200px">
				</colgroup>
				<tbody>
					<tr>
						<th class="info_h1">Дата:</th>
						<td class="info_d1">'''+date_report+'''</td>
					</tr>            

					<tr>             
						<th class="info_h2">Тренер:</th>
						<td class="info_d2">'''+trainer+'''</td>
					</tr>
				</tbody>
			</table>
		</div>

		<hr>

		<div id="info_header">
			<b>Активные команды:</b>
		</div>
	'''

	for team in sorted(teams[1:]):
		team_info = get_team_info(team)
		run_info = get_run_info(team)
		first_weight = run_info[4].split(', ')

		runs = run_info[1]
		days = run_info[2]

		if days == 0:
			continue

		start_date_report = datetime.datetime.utcfromtimestamp(time.time() - 84000 * days).strftime('%d.%m.%Y')
		players_name = team_info[1].split(', ')

		day_text = ''
		
		best_of_days = []
		best_of_run = [[], []]
@		sum_lost_weight = [[0 * i for i in range(len(players_name))], [0 * i for i in range(len(players_name))]]

		for day in range(days):
			day_text += f'<th class="tg-45l0">День {day+1}</th>\n'

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

			best_of_day = []

			if lost_weight.count(0) != len(lost_weight):
				for i in range(len(lost_weight)):
					sum_lost_weight[0][i] += lost_weight[i]
					sum_lost_weight[1][i] += lost_weight[i]/float(first_weight[i])*100

					if float(lost_weight[i]) == float(max_lost_weight):
						best_of_day.append(i)

			best_of_days.append(best_of_day)

		if sum_lost_weight[0].count(0) != len(sum_lost_weight[0]):
			max_sum_lost_weight_kg = max(sum_lost_weight[0])
			max_sum_lost_weight_pr = max(sum_lost_weight[1])
			
			for i in range(len(sum_lost_weight[0])):
				if float(sum_lost_weight[0][i]) == float(max_sum_lost_weight_kg):
					best_of_run[0].append(i)

				if float(sum_lost_weight[1][i]) == float(max_sum_lost_weight_pr):
					best_of_run[1].append(i)

		players_text = ''
		
		for player in range(len(players_name)):
			players_text += f'<tr><td class="tg-jes8">{players_name[player]}</td>'
			players_text += f'<td class="tg-ohj9">{first_weight[player]} Кг</td>'

			player_weight = 0
			
			for day in range(days):
				players_weight = run_info[5 + day].split(', ')
				last_weight = run_info[4 + day].split(', ')

				if players_weight[player] == '':
					players_text += f'<td class="tg-ohj9" style="background-color: #cf6e69;">0</td>'

				else:
					if last_weight[player] == '':
						for d in range(day-1, -1, -1):
							last_weight_prev = run_info[4 + d].split(', ')[player]
							if last_weight_prev == '':
								continue
							else:
								last_weight[player] = last_weight_prev
								break

					lost_weight_player = int((float(players_weight[player]) - float(last_weight[player])) * 1000)

					player_weight += lost_weight_player/1000

					if player in best_of_days[day]:
						players_text += f'<td class="tg-ohj9" style="background-color: #9fc284;">{lost_weight_player}</td>'
					else:
						players_text += f'<td class="tg-ohj9">{lost_weight_player}</td>'

			if player in best_of_run[0]:
				players_text += f'<td class="tg-qcst" style="background-color: #d9944a;"><b>{player_weight} Кг</b></td>'
			else:
				players_text += f'<td class="tg-qcst"><b>{player_weight:.1f} Кг</b></td>'

			if player in best_of_run[1]:
				players_text += f'<td class="tg-ohj9" style="background-color: #d9944a;"><b>{(float(player_weight)/float(first_weight[player])*100):.2f}%</b></td></tr>'
			else:
				players_text += f'<td class="tg-ohj9"><b>{(player_weight/float(first_weight[player])*100):.2f}%</b></td></tr>'	

		lost_weight = '<tr><td class="tg-jes8">Всего за день:</td><td class="tg-ohj9"><b>0 Кг</b></td>'
		
		for day in range(days):
			players_weight = run_info[5 + day].split(', ')
			last_weight = run_info[4 + day].split(', ')
			lost_weight_today = []

			for i in range(len(players_weight)):
				if players_weight[i] == '':
					lost_weight_today.append(0)
					continue
				
				if last_weight[i] == '':
					for d in range(day-1, -1, -1):
						last_weight_prev = run_info[4 + d].split(', ')[i]
						if last_weight_prev == '':
							continue
						else:
							last_weight[i] = last_weight_prev
							break

				lost_weight_today.append(float(players_weight[i]) - float(last_weight[i]))

			lost_weight += f'<td class="tg-ohj9"><b>{sum(lost_weight_today):.1f} Кг</b></td>'
		
		lost_weight += '<td colspan="2" class="tg-640t"></td></tr>'

		baza += '''
		<div class="team">
			<div class="header">
				<b>Команда '''+trainer+''' '''+str(team.split('_')[1])+'''</b>
			</div>

			<table class="team_table" style="text-align: left;padding: 5px;" cellspacing="8">
				<colgroup>
					<col style="width: 90px">
				</colgroup>
				<tr>
					<th class="info_h1">Забег:</th>
					<td class="info_d1">'''+str(runs)+'''</td>
				</tr>            

				<tr>             
					<th class="info_h2">День:</th>
					<td class="info_d2">'''+str(days)+'''</td>
				</tr>
				<tr>
					<th class="info_h1">Тренер:</th>
					<td class="info_d1">'''+trainer+'''</td>
				</tr>            

				<tr>             
					<th class="info_h2">Даты:</th>
					<td class="info_d2">'''+start_date_report+''' - '''+date_report+'''</td>
				</tr>
			</table>
		</div>

		<div class="oboz">
			<div class="header">
				<b>Обозначения</b>
			</div>

			<table class="oboz_table" style="padding: 2px;" cellspacing="8" width="238">
				<colgroup>
					<col style="width: 45px">
				</colgroup>
				<tr>
					<th class="h1" style="background-color: #9fc284;"></th>
					<td class="d1">Лидер дня</td>
				</tr>            
				<tr>             
					<th class="h2" style="background-color: #d9944a;"></th>
					<td class="d2">Лидер забега</td>
				</tr>
				<tr>             
					<th class="h3" style="background-color: #cf6e69;"></th>
					<td class="d3">Нет отчёта за день</td>
				</tr>
			</table>
		</div>

		<div id="main_table">
			<table class="tg" style="table-layout: fixed;width: 100%;">
				<thead>
					<tr>
						<th class="tg-45l0">Игрок</th>
						<th class="tg-45l0">Нулевой день</th>
						'''+day_text+'''
						<th class="tg-45l0">Изменение веса в кг</th>
						<th class="tg-45l0">Изменение веса в %</th>
					</tr>
				</thead>

				<tbody>
					'''+players_text+'''
					'''+lost_weight+'''
				</tbody>
			</table>
		</div>
		'''

		if sorted(teams).index(team) == 1:
			baza += '<br><br><br><br><br><br><br>'
		else:
			baza += '<br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br>'

		baza += '</body></html>'

	return pdfkit.from_string(baza)