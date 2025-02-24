from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def owner_panel_keyboard():
    """Admin uchun default tugmalar (pastda chiqadigan)"""
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(
        KeyboardButton("🆕 Admin qo‘shish"),
        KeyboardButton("❌ Adminni o‘chirish"),
    )
    return keyboard

