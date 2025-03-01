from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from loader import db

async def get_remove_admin_buttons():
    """Barcha adminlarni inline button sifatida chiqaradi. Agar adminlar bo'lmasa, None qaytaradi."""

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

def get_add_data_btn_finish_buttons():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("➕📩 Ma'lumot qo'shish", callback_data="add_more_data"))
    keyboard.add(InlineKeyboardButton(text="➕📂 Ichki tugma qo'shish", callback_data="add_subbutton"))
    keyboard.add(InlineKeyboardButton(text="✅ Tugatish", callback_data="finish")) 
    return keyboard






