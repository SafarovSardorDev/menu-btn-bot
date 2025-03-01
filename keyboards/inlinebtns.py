from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from prisma import Prisma

db = Prisma()

async def get_remove_admin_buttons():
    """Barcha adminlarni inline button sifatida chiqaradi. Agar adminlar bo'lmasa, None qaytaradi."""
    if not db.is_connected():  # Avval ulanish borligini tekshiramiz
        await db.connect()

    admins = await db.user.find_many(where={"role": "admin"})  # Asinxron query

    if not admins:
        return None

    keyboard = InlineKeyboardMarkup(row_width=1)  # Har bir qatorda 1 ta tugma
    for admin in admins:
        keyboard.add(InlineKeyboardButton(text=admin.username, callback_data=f"remove_admin:{admin.telegramId}"))

    return keyboard

def cancel_button():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("❌ Bekor qilish", callback_data="cancel")
    )
    return keyboard

def get_add_data_btn_buttons():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("📄 Ma’lumot qo‘shish", callback_data="add_content"))
    keyboard.add(InlineKeyboardButton("🔘 Ichiga tugmalar qo‘shish", callback_data="add_subbuttons"))
    return keyboard


def get_confirmation_buttons():
    """Tasdiqlash tugmalari"""
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("✅ Ha", callback_data="confirm"))
    keyboard.add(InlineKeyboardButton("❌ Yo‘q", callback_data="stop_media"))
    return keyboard

def get_add_more_buttons():
    """Yana ma'lumot qo‘shish yoki yakunlash"""
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("➕ Yana qo‘shish", callback_data="add_more"))
    keyboard.add(InlineKeyboardButton("✅ Tugatish", callback_data="finish"))
    return keyboard







