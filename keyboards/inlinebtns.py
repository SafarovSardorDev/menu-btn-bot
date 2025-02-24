from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from prisma import Prisma

db = Prisma()

async def get_remove_admin_buttons():
    """Barcha adminlarni inline button sifatida chiqaradi."""
    if not db.is_connected():  # Avval ulanish borligini tekshiramiz
        await db.connect()

    admins = await db.user.find_many(where={"role": "admin"})  # Asinxron query

    keyboard = InlineKeyboardMarkup(row_width=1)  # Har bir qatorda 1 ta tugma
    for admin in admins:
        keyboard.add(InlineKeyboardButton(text=admin.username, callback_data=f"remove_admin:{admin.telegramId}"))

    return keyboard






