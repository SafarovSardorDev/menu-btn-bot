from prisma import Prisma
from aiogram import executor
from loader import dp
import middlewares, filters, handlers
from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands

prisma_db = Prisma()

async def on_startup(dispatcher):
    """Bot ishga tushganda Prisma client’ni bog‘lash"""
    await set_default_commands(dispatcher)
    await prisma_db.connect()

    # Bot ishga tushgani haqida adminga xabar berish
    await on_startup_notify(dispatcher)

async def on_shutdown(dispatcher):
    """Bot o‘chirilganda Prisma client’ni uzish"""
    await prisma_db.disconnect()


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown)