import numpy, io
from aiogram import Dispatcher, types
from PIL import Image, ImageOps, ImageFilter, ImageDraw, ImageFont

from modules.loader import bot
from modules.database import *

	
trainer_logo = Image.open('photos/trainer.png')
helper_logo = Image.open('photos/ht.png')
client_logo = Image.open('photos/client.png')
leader_day = Image.open('photos/ld.png')
leader_run = Image.open('photos/lr.png')
name_field = Image.open('photos/nf.png')
weight_field = Image.open('photos/wf.png')

end_day_photo = Image.open('photos/endday.png')
finish_photo = Image.open('photos/finish.jpg')
start_photo = Image.open('photos/start.jpg')

leader_run_photo = Image.open('photos/lrun.jpg')
leader_day_photo = Image.open('photos/lday.jpg')
champion_photo = Image.open('photos/champion.jpg')

font = ImageFont.truetype('data/Calibri.ttf', 50, encoding = 'UTF-8')
head_font = ImageFont.truetype('data/Calibri.ttf', 50, encoding='UTF-8')
name_font = ImageFont.truetype('data/Calibri.ttf', 55, encoding='UTF-8')


def crop_image(image):
	crop_width, crop_height = min(image.size), min(image.size)
	img_width, img_height = image.size
	return image.crop(((img_width - crop_width) // 2, (img_height - crop_height) // 2, (img_width + crop_width) // 2, (img_height + crop_height) // 2))


def edit_images(images, helper = '', clients = '', names = '', weight = None, besties = None):
	edited_images = []

	for image in images:
		image_obj = Image.open(image).convert('RGBA')
		image_croped = crop_image(image_obj)
		image_resized = image_croped.resize((450, 450))
		
		if names != '':
			image_resized.paste(name_field, (0, 390))
			draw = ImageDraw.Draw(image_resized)
			draw.text((225, 420), names[images.index(image)], (255, 255, 255, 255), font = font, anchor = 'mm')

		if weight != None:
			image_resized.paste(weight_field, (300, 20))
			draw.text((365, 53), str(int(weight[images.index(image)]*1000)), (255, 255, 255, 255), font = font, anchor = 'mm')

		image_with_border = ImageOps.expand(image_resized, border = 12, fill = (255, 255, 255, 255))
		image_with_border = ImageOps.expand(image_with_border, border = 1, fill = (0, 0, 0, 255))

		if images.index(image) == 0:
			image_with_border.paste(trainer_logo, (30, 30), mask = trainer_logo)
		
		if helper != '':
			if images.index(image) == helper:
				image_with_border.paste(helper_logo, (30, 30), mask = helper_logo)

		if clients != '':
			if images.index(image) in clients:
				image_with_border.paste(client_logo, (30, 30), mask = client_logo)

		if besties != None:
			if names[images.index(image)] in besties[0]:
				image_with_border.paste(leader_day, (355, 110), mask = leader_day)

			if names[images.index(image)] in besties[1]:
				if names[images.index(image)] in besties[0]:
					image_with_border.paste(leader_run, (355, 220), mask = leader_run)
				else:
					image_with_border.paste(leader_run, (355, 110), mask = leader_run)

		edited_images.append(image_with_border)
	
	return edited_images


async def collage_maker(players_photos, team_id, weight = None, besties = None):
	photo_bytes = []

	for photo in players_photos:
		file_info = await bot.get_file(photo)
		photo_bytes.append(await bot.download_file(file_info.file_path))

	if team_id != None:
		team_info = get_team_info(team_id)
		players = team_info[1].split(', ')
		clients = team_info[4].split(', ')

		if team_info[3] != '':
			helper = players.index(str(team_info[3]))
		else:
			helper = ''

		if clients != ['']:
			for client in clients[1:]:
				clients.append(players.index(client))
				clients.remove(client)
		else:
			clients = ''

		images = edit_images(photo_bytes, helper, clients, players, weight, besties)
	else:
		images = edit_images(photo_bytes)

	num_images = []

	for i in images:
		num_images.append(numpy.array(i))

	collage = []
	added_photo = 0

@	if len(players_photos) == 6:
		rows = 2
		columns = 3
	elif len(players_photos) == 9:
		rows = 3
		columns = 3
	elif len(players_photos) == 15:
		rows = 5
		columns = 3

	for row in range(rows):
		col_images = []

		for column in range(columns):
			col_images.append(num_images[added_photo])
			added_photo += 1

		collage.append(numpy.hstack(col_images))

	return Image.fromarray(numpy.vstack(collage))


async def make_collage(players_photos, team_id = None):
	img_byte = io.BytesIO()

	collage = await collage_maker(players_photos, team_id)
	collage.save(img_byte, format = 'png')
	
	return img_byte.getvalue()


async def make_start(players_photos, team_id, user_name):
	img_byte = io.BytesIO()

	collage = await collage_maker(players_photos, team_id)
	collage = collage.resize((1000, 1000))
	
	fon = start_photo.copy()
	fon.paste(collage, (250, 420))

	runs = get_run_info(team_id)[1]
	count_team = team_id.split('_')[1]

	draw = ImageDraw.Draw(fon)
	draw.text((250, 1460), f'Команда {user_name} {count_team}', (0, 0, 0, 255), font = font)
	draw.text((250, 1540), f'Забег #{runs+1}', (0, 0, 0, 255), font = font)

	fon.save(img_byte, format = 'jpeg')
	return img_byte.getvalue()


async def make_finish(players_photos, team_id, user_name, result, weight, besties):
	img_byte = io.BytesIO()

	collage = await collage_maker(players_photos, team_id, weight, besties)
	collage = collage.resize((1000, 1000))

	fon = finish_photo.copy()
	fon.paste(collage, (250, 420))

	runs = get_run_info(team_id)[1]
	count_team = team_id.split('_')[1]

	draw = ImageDraw.Draw(fon)
	draw.text((250, 1460), f'Команда {user_name} {count_team}', (0, 0, 0, 255), font = font)
	draw.text((250, 1540), f'Забег #{runs+1}', (0, 0, 0, 255), font = font)
	draw.text((450, 1540), f'Результат {result} Кг', (0, 0, 0, 255), font = font)

	fon.save(img_byte, format = 'jpeg')
	return img_byte.getvalue()


async def make_end_day(players_photos, team_id, weight, besties):
	img_byte = io.BytesIO()
	fon = end_day_photo.copy()

	collage = await collage_maker(players_photos, team_id, weight, besties)
	collage = collage.resize((1500, 1500))

	fon.paste(collage, (0, 213))
	fon.save(img_byte, format = 'jpeg')

	return img_byte.getvalue()


async def make_best_of(name, image, type, team_id, user_name, run_num = None):
	img_byte = io.BytesIO()

	file_info = await bot.get_file(image)
	image = await bot.download_file(file_info.file_path)
	
	image_obj = Image.open(image)
	image_croped = crop_image(image_obj)
	image_resized = image_croped.resize((550, 550))

	mask = Image.new('L', image_resized.size, 0)
	draw_mask = ImageDraw.Draw(mask)
	draw_mask.ellipse((0, 0, image_resized.size), fill=255)
	
	run_info = get_run_info(team_id)
	run_number = run_info[1]+1
	day = run_info[2]
	count_team = team_id.split('_')[1]

	if type == 'day':
		leader = leader_day_photo.copy()

	elif type == 'run':
		leader = leader_run_photo.copy()

	elif type == 'end':
		run_number = run_num
		day = 10
		leader = champion_photo.copy()
	
	leader.paste(image_resized, (225, 215), mask = mask)

	draw = ImageDraw.Draw(leader)
	draw.text((500, 50), f'Команда', (255, 255, 255, 255), font = head_font, anchor = 'mm')
	draw.text((500, 110), f'{user_name} {count_team}', (255, 255, 255, 255), font = head_font, anchor = 'mm')
	draw.text((500, 180), f'Забег #{run_number}, День {day}', (255, 255, 255, 255), font = head_font, anchor = 'mm')
	draw.text((500, 830), name, (255, 255, 255, 255), font = name_font, anchor = 'mm')

	leader.save(img_byte, format = 'jpeg')
	return img_byte.getvalue()