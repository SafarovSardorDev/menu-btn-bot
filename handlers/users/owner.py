from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InputMediaPhoto, InputMediaVideo, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters import Text
from loader import dp, bot
from prisma import Prisma
from aiogram.types  import ContentTypes, ContentType
from states.btnsstates import AddAdminState, ButtonCreation
from keyboards.inlinebtns import get_remove_admin_buttons, get_add_data_btn_buttons, get_add_more_buttons, get_confirmation_buttons, cancel_button
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()

OWNER_ID = int(os.getenv("OWNER_ID"))
db = Prisma()


#Owner uchun yangi admin qo'shish qismi!!!
@dp.message_handler(Text(equals="🆕 Admin qo‘shish"))
async def ask_admin_id(message: types.Message):
    """Admin qo‘shish uchun ID so‘rash"""
    if message.from_user.id != OWNER_ID:
        return await message.answer("Bu funksiyadan faqat Owner foydalanishi mumkin.")

    await message.answer("🆔 Admin qilib qo‘shmoqchi bo‘lgan foydalanuvchining Telegram ID sini kiriting (faqat son kiritish mumkin):")
    await AddAdminState.waiting_for_admin_id.set()

@dp.message_handler(state=AddAdminState.waiting_for_admin_id)
async def add_admin_by_id(message: types.Message, state: FSMContext):
    """Owner admin qo'shishi uchun"""
    if not message.text.isdigit():
        return await message.answer("❌ Noto‘g‘ri format! Faqat son kiriting.\n🆔 Admin ID ni kiriting:", reply_markup=cancel_button())

    admin_id = int(message.text.strip())

    await db.connect()

    user = await db.user.find_first(where={"telegramId": admin_id})

    if not user:
        await message.answer("Bunday foydalanuvchi topilmadi! \nAdmin qilmoqchi bo'lgan user oldin botga /start bosishi kerak!!!")
        await db.disconnect()
        return
    
    username = user.username  

    if username:
        username_text = f"[@{username}](https://t.me/{username})"
    else:
        username_text = "Ismi mavjud emas"

    if user.role == "admin":
        await message.answer(
            f"id-{admin_id}, {username_text} - bu foydalanuvchi allaqachon admin❗️",
            parse_mode="Markdown",
            disable_web_page_preview=True
            )
        await db.disconnect()
        await state.finish()
        return
    

    await db.user.update(
        where={"telegramId": admin_id},
        data={"role": "admin"}
    )

    await message.answer(
        f"Foydalanuvchi {admin_id} {username_text} endi admin sifatida belgilandi ✅",
        parse_mode="Markdown",
        disable_web_page_preview=True
    )
    
    await db.disconnect()
    await state.finish()

@dp.callback_query_handler(lambda call: call.data == "cancel", state=AddAdminState.waiting_for_admin_id)
async def cancel_add_admin(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text("❌ Jarayon bekor qilindi!")
    await state.finish()

#Owner uchun adminni o'chirish qismi!!!
@dp.message_handler(text="❌ Adminni o‘chirish")
async def remove_admin_handler(message: types.Message):
    """Owner adminlarni o‘chirish uchun ro‘yxatni chiqaradi."""
    if message.from_user.id != OWNER_ID:
        await message.reply("🚫 Bu funksiyadan faqat bot egasi foydalanishi mumkin.")
        return

    try:
        keyboard = await get_remove_admin_buttons() 
        if keyboard is None:
            await message.reply("🚫 Hozircha hech qanday admin yo‘q!")
            return
        await message.reply("🛑 O‘chirish uchun adminni tanlang:", reply_markup=keyboard)
    except Exception as e:
        await message.reply(f"Xatolik yuz berdi: {e}")


@dp.callback_query_handler(lambda c: c.data.startswith("remove_admin:"))
async def remove_admin(callback_query: types.CallbackQuery):
    """Tanlangan adminni bazadan o‘chirish."""
    admin_id = int(callback_query.data.split(":")[1])

    await db.connect()

    admin = await db.user.find_first(where={"telegramId": admin_id})

    if not admin:
        await callback_query.answer("⚠️ Bunday admin topilmadi!", show_alert=True)
        return

    await db.user.update(where={"telegramId": admin_id}, data={"role": "user"})

    await callback_query.message.edit_text(f"✅ Admin {admin.username} oddiy userga aylantirildi!")
    await db.disconnect() 

















#owner va admin uchun tugma qo'shish 
import json

@dp.message_handler(lambda message: message.text == "➕ Yangi tugma qo‘shish", state=None)
async def add_new_button(message: types.Message, state: FSMContext):
    await db.connect()
    user = await db.user.find_first(where={"telegramId": message.from_user.id})
    if not user or user.role not in ["admin", "owner"]:
        await message.answer("❌ Sizga bu amalni bajarishga ruxsat berilmagan!")
        return
    await message.answer("✏️ Yangi tugma nomini kiriting (64 ta belgidan oshmasin):")
    await state.set_state(ButtonCreation.name)

@dp.message_handler(state=ButtonCreation.name)
async def enter_button_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Tugmaga ma'lumot (matn yoki media) yuboring:")
    await state.set_state(ButtonCreation.add_data)

@dp.message_handler(content_types=['text', 'photo', 'video'], state=ButtonCreation.add_data)
async def add_data_to_button(message: types.Message, state: FSMContext):
    data = await state.get_data()
    menu_name = data.get("name")
    user_id = message.from_user.id

    # Tugmani bazaga qo‘shish
    menu = await db.menu.create({
        "name": menu_name,
        "creatorId": user_id
    })

    if not menu or not menu.id:
        await message.answer("❌ Tugma yaratishda xatolik yuz berdi!")
        return

    # Ma'lumotni bazaga qo‘shish
    if message.text:
        await db.menumessage.create({
            "message": json.dumps({"text": message.text}),
            "type": "text",
            "menuId": menu.id
        })
    elif message.photo:
        await db.menumessage.create({
            "message": json.dumps({"photo": message.photo[-1].file_id}),
            "type": "image",
            "menuId": menu.id
        })
    elif message.video:
        await db.menumessage.create({
            "message": json.dumps({"video": message.video.file_id}),
            "type": "video",
            "menuId": menu.id
        })

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Yana ma'lumot qo'shish", callback_data="add_more_data")],
        [InlineKeyboardButton(text="Ichki tugma qo'shish", callback_data="add_subbutton")],
        [InlineKeyboardButton(text="Tugatish", callback_data="finish")]
    ])

    await message.answer("Ma'lumot qo'shildi. Keyingi qadamni tanlang:", reply_markup=keyboard)
    await state.set_state(ButtonCreation.confirm_data)

@dp.callback_query_handler(lambda c: c.data == "add_more_data", state=ButtonCreation.confirm_data)
async def add_more_data(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Tugmaga yana ma'lumot yuboring:")
    await state.set_state(ButtonCreation.add_data)

@dp.callback_query_handler(lambda c: c.data == "add_subbutton", state=ButtonCreation.confirm_data)
async def add_subbutton(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Ichki tugma nomini kiriting:")
    await state.set_state(ButtonCreation.add_subbutton)

@dp.message_handler(state=ButtonCreation.add_subbutton)
async def enter_subbutton_name(message: types.Message, state: FSMContext):
    data = await state.get_data()
    parent_menu = await db.menu.find_first(where={"name": data.get("name")})
    
    if not parent_menu:
        await message.answer("❌ Asosiy tugma topilmadi!")
        return
    
    sub_menu = await db.menu.create({
        "name": message.text,
        "creatorId": message.from_user.id,
        "parentId": parent_menu.id
    })

    await message.answer(f"Ichki tugma '{message.text}' yaratildi! Tugmani tugatish yoki davom ettirishni tanlang.")
    await state.set_state(ButtonCreation.confirm)

@dp.callback_query_handler(lambda c: c.data == "finish", state=ButtonCreation.confirm_data)
async def finish_button_creation(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Tugma yaratildi va bazaga saqlandi! ✅")
    await state.finish()