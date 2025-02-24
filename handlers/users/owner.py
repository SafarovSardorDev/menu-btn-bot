from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from loader import dp
from prisma import Prisma
from states.add_admin import AddAdminState  
from keyboards.inlinebtns import get_remove_admin_buttons
from dotenv import load_dotenv
import os

load_dotenv()

OWNER_ID = int(os.getenv("OWNER_ID"))
db = Prisma()


#Owner uchun yangi admin qo'shish qismi!!!
@dp.message_handler(Text(equals="🆕 Admin qo‘shish"))
async def ask_admin_id(message: types.Message):
    """Admin qo‘shish uchun ID so‘rash"""
    if message.from_user.id != OWNER_ID:
        return await message.answer("Bu funksiyadan faqat Owner foydalanishi mumkin.")

    await message.answer("Admin qilib qo‘shmoqchi bo‘lgan foydalanuvchining Telegram ID sini kiriting:")
    await AddAdminState.waiting_for_admin_id.set()

@dp.message_handler(state=AddAdminState.waiting_for_admin_id)
async def add_admin_by_id(message: types.Message, state: FSMContext):
    """Owner admin qo'shishi uchun"""
    admin_id = int(message.text.strip())

    await db.connect() 

    user = await db.user.find_first(where={"telegramId": admin_id})
    if not user:
        await message.answer("Bunday foydalanuvchi topilmadi!")
        await db.disconnect() 
        return
    

    await db.user.update(
        where={"telegramId": admin_id},
        data={"role": "admin"}
    )

    await message.answer(f"Foydalanuvchi {admin_id} endi admin sifatida belgilandi ✅")
    
    await db.disconnect() 
    await state.finish()  




#Owner uchun adminni o'chirish qismi!!!
@dp.message_handler(text="❌ Adminni o‘chirish")
async def remove_admin_handler(message: types.Message):
    """Owner adminlarni o‘chirish uchun ro‘yxatni chiqaradi."""
    if message.from_user.id != OWNER_ID:
        await message.reply("Bu funksiyadan faqat bot egasi foydalanishi mumkin.")
        return

    try:
        keyboard = await get_remove_admin_buttons() 
        await message.reply("O‘chirish uchun adminni tanlang:", reply_markup=keyboard)
    except Exception as e:
        await message.reply(f"Xatolik yuz berdi: {e}")


@dp.callback_query_handler(lambda c: c.data.startswith("remove_admin:"))
async def remove_admin(callback_query: types.CallbackQuery):
    """Tanlangan adminni bazadan o‘chirish."""
    admin_id = int(callback_query.data.split(":")[1])  # Admin ID ni ajratish

    if not db.is_connected():
        await db.connect()

    admin = await db.user.find_first(where={"telegramId": admin_id})

    if not admin:
        await callback_query.answer("Bunday admin topilmadi!", show_alert=True)
        return

    await db.user.update(where={"telegramId": admin_id}, data={"role": "user"})  # Admin userga aylantiriladi

    await callback_query.message.edit_text(f"✅ Admin {admin.username} oddiy userga aylantirildi!")
    await db.disconnect() 



