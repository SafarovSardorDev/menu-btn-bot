from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def owner_panel_keyboard():
    """Admin uchun default tugmalar (pastda chiqadigan)"""
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(
        KeyboardButton("🆕 Admin qo‘shish"),
        KeyboardButton("❌ Adminni o‘chirish"),
    )
    keyboard.add(
        KeyboardButton("➕ Yangi tugma qo‘shish"),
        KeyboardButton("📝 Tugmalarim")
    )
    keyboard.add(
        KeyboardButton("✏️ Tugmani tahrirlash"),
        KeyboardButton("🗑 Tugmani o‘chirish"),
    )
    return keyboard

def admin_panel_keyboard():
    """Admin uchun default tugmalar (pastda chiqadigan)"""
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(
        KeyboardButton("➕ Yangi tugma qo‘shish"),
        KeyboardButton("📝 Tugmalarim"),
    )
    keyboard.add(
        KeyboardButton("✏️ Tugmani tahrirlash"),
        KeyboardButton("🗑 Tugmani o‘chirish"),
    )
    return keyboard

