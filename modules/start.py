from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from modules.database import check_user_in_db, add_new_user
from modules.keyboards import choice_menu, confirm_menu
from modules.menu_team import teams_list
from modules.create_team import new_team


class StartState(StatesGroup):
	confirm_data = State()
	confirm_conf = State()
	supervisor_choice = State()
	id_enter = State()
	name_enter = State()


async def confirm_data(message: types.Message):
	await message.answer_document('BQACAgIAAxkBAAIHRWK-8282FhO7gmULyoASUb0Ksg5GAAKUGAACuTP4SRpVsduu3yt8KQQ', caption='Я прочитал (-а) и согласен (-на) с Условиями защиты данных дистрибьютора', reply_markup=confirm_menu)
	await StartState.confirm_data.set()


async def confirm_conf(call: types.CallbackQuery, state: FSMContext):
	await call.message.answer_document('BQACAgIAAxkBAAIHRGK-8uXj9T0nUAlNHTgl8PHXkeGcAAKSGAACuTP4ST9MfDneM7WgKQQ', caption='Я прочитал (-а) Информацию об обеспечении конфиденциальности для онлайн-марафонов по здоровью и согласен (-на) их соблюдать', reply_markup=confirm_menu)
	await StartState.confirm_conf.set()


async def trainer(call: types.CallbackQuery, state: FSMContext):
	await call.message.answer('<b>Привет, я - Бот-помощник Тренера</b>')
	await call.message.answer('Я помогу вам в управлении вашими командами')
	await call.message.answer_document('BQACAgIAAxkBAAIIR2LARR19gSUS0Xyerz50-hIYn0-UAAJWFwACuTMAAUrZEqwylOTZKykE')
	await call.message.answer_document('BQACAgIAAxkBAAIISGLARUPykUOkAVCBMDvD5ZcJDDQ4AAJXFwACuTMAAUrsOcaVIpFuqykE')
	await call.message.answer('Вы - Тренер по питанию?', reply_markup=choice_menu)
	await StartState.supervisor_choice.set()


async def start(message: types.Message, state: FSMContext):
	await state.finish()

	if check_user_in_db(message.chat.id):
		await message.answer('<b>Привет, я - Бот-помощник Тренера</b>')
		await teams_list(message, state)
	else:
		await confirm_data(message)


async def confirm_super(call: types.CallbackQuery, state: FSMContext):
	await call.message.answer('Введите свой номер ID')
	await StartState.id_enter.set()


async def id_enter(message: types.Message, state: FSMContext):
	if len(message.text) > 6 and message.text.isdigit():
		await message.answer('Спасибо.\nВведите ваши имя и фамилию так, как они записаны в «Родник здоровья»')
		await state.update_data(id = int(message.text))
		await StartState.name_enter.set()
	else:
		await message.answer('Неверный номер ID.\nПопробуйте снова.')


async def name_enter(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		super_id = data.get('id')

	add_new_user(message.chat.id, message.text, super_id)
	
	await message.answer('ОК, <b>'+message.text+'</b>')
	await new_team(message)


async def choice_no(call: types.CallbackQuery, state: FSMContext):
	await call.message.answer('Без проблем, вы всегда можете начать сначала, нажав "/start"')
	await state.finish()


async def choice_no_state(call: types.CallbackQuery):
	await call.message.answer('Попробуйте снова')


def register_start(dp: Dispatcher):
	dp.register_message_handler(start, commands = 'start')
	dp.register_message_handler(id_enter, state = StartState.id_enter)
	dp.register_message_handler(name_enter, state = StartState.name_enter)

	dp.register_callback_query_handler(confirm_conf, text = 'cb_confirm', state = StartState.confirm_data)
	dp.register_callback_query_handler(trainer, text = 'cb_confirm', state = StartState.confirm_conf)

	dp.register_callback_query_handler(confirm_super, text = 'cb_yes', state = StartState.supervisor_choice)

	dp.register_callback_query_handler(choice_no, text = 'cb_no', state = StartState.supervisor_choice)
	dp.register_callback_query_handler(choice_no_state, text = ['cb_yes', 'cb_no'])