import asyncio
import traceback

from aiogram import Bot, Dispatcher, types

from modules.loader import dp, scheduler, logging
from modules.database import storage, update_all_day
from modules.start import register_start
from modules.menu_team import register_menu
from modules.create_team import register_create_team
from modules.edit_team import register_edit_team
from modules.delete_team import register_delete_team
from modules.enter_photo import register_enter_photo
from modules.enter_helper import register_enter_helper
from modules.marathon import register_start_run, notify_user, report_user


def register_handlers(dp: Dispatcher):
	register_menu(dp)
	register_start(dp)
	register_create_team(dp)
	register_edit_team(dp)
	register_delete_team(dp)
	register_enter_photo(dp)
	register_enter_helper(dp)
	register_start_run(dp)


def register_scheduler(dp):
	scheduler.add_job(update_all_day, 'cron', day_of_week='mon-sun', hour=0, minute=00)
	scheduler.add_job(notify_user, 'cron', day_of_week='mon-sun', hour=8, minute=55, args=(dp,))
	scheduler.add_job(report_user, 'cron', day_of_week='mon-sun', hour=21, minute=0, args=(dp,))


async def main():
	await dp.bot.set_my_commands(
		[types.BotCommand('teams', 'Видеть свои команды и управлять ими'), 
		types.BotCommand('newteam', 'Создать новую команду'),
		types.BotCommand('report', 'Отчет в PDF обо всех ваших активных командах')]
	)

	register_scheduler(dp)
	register_handlers(dp)

	try:
		print('Бот начал работу...')
		logging.warning('The bot is running...')
		scheduler.start()
		await dp.start_polling()
	finally:
		await dp.storage.close()
		await dp.storage.wait_closed()
		await dp.bot.session.close()

if __name__ == "__main__":
	try:
		asyncio.run(main())
	except (KeyboardInterrupt, SystemExit):
		logging.error('Bot stopped!')
	except:
		logging.error(traceback.format_exc())
