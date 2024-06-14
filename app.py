import asyncio
from aiogram.types import BotCommand

from config import bot, dp, logger
from handlers import register_handlers
from database import Database


async def main():
    await Database.db_init()

    bot_commands = (
        ("start", "Начало работы с ботом"),
        ('menu', 'Переход в меню')
    )

    commands_for_bot = []
    for cmd in bot_commands:
        commands_for_bot.append(BotCommand(command=cmd[0], description=cmd[1]))
    await bot.set_my_commands(commands=commands_for_bot)

    await register_handlers(dp)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Database was disconnected")
        logger.info("Bot was stopped")
