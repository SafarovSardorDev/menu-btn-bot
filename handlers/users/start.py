import os
from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
from prisma import Prisma
from loader import dp, db
from datetime import datetime
from dotenv import load_dotenv
from keyboards.defaultbtns import owner_panel_keyboard, admin_panel_keyboard

load_dotenv()

OWNER_ID = int(os.getenv("OWNER_ID"))



async def save_user_to_db(user: types.User):
    """Foydalanuvchi ma'lumotlarini saqlash funksiyasi"""
    try:
        print(f"Saving user {user.id} to the database...")

        if user.id == OWNER_ID:
            role = "owner"
        else:
            existing_admin = await db.user.find_first(where={"telegramId": user.id, "role": "admin"})
            role = "admin" if existing_admin else "user"

        existing_user = await db.user.find_first(where={"telegramId": user.id})

        if existing_user:
            print(f"User {user.id} exists, updating...")
            await db.user.update(
                where={"telegramId": user.id},
                data={
                    "firstName": user.first_name,
                    "lastName": user.last_name,
                    "isPremium": False,
                    "isBot": user.is_bot,
                    "languageCode": user.language_code,
                    "username": user.username,
                    "role": role, 
                    "updatedAt": datetime.now()
                }
            )
        else:
            print(f"User {user.id} not found, creating...")
            await db.user.create(
                data={
                    "telegramId": user.id,
                    "firstName": user.first_name,
                    "lastName": user.last_name,
                    "isPremium": False,
                    "isBot": user.is_bot,
                    "languageCode": user.language_code,
                    "username": user.username,
                    "role": role
                }
            )
    except Exception as e:
        print(f"Error saving user to database: {e}")


@dp.message_handler(commands=['start'])
async def handle_start(message: types.Message):

    await save_user_to_db(message.from_user)

    if message.from_user.id == OWNER_ID:
        role = "Owner"
        keyboard = owner_panel_keyboard()
    elif await db.user.find_first(where={"telegramId": message.from_user.id, "role": "admin"}):
        role = "Admin"
        keyboard = admin_panel_keyboard()
    else:
        role = "User"
        keyboard = None

    if message.from_user.username:
        await message.answer(
            f"Salom {message.from_user.username}. Botga xush kelibsiz. Siz {role} sifatida ro'yxatga olindingiz.",
            reply_markup=keyboard
        )
    else:
        await message.answer(
            f"Salom {message.from_user.first_name} {message.from_user.last_name}. Botga xush kelibsiz. Siz {role} sifatida ro'yxatga olindingiz.",
            reply_markup=keyboard
        )


    
