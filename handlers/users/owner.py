from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InputMediaPhoto, InputMediaVideo, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters import Text
from loader import dp, db
from aiogram.types  import ContentTypes, ContentType
from states.btnsstates import AddAdminState, ButtonCreation
from keyboards.inlinebtns import get_remove_admin_buttons, get_add_data_btn_finish_buttons, cancel_button
from dotenv import load_dotenv
import os
import json
import asyncio

load_dotenv()

OWNER_ID = int(os.getenv("OWNER_ID"))



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


    user = await db.user.find_first(where={"telegramId": admin_id})

    if not user:
        await message.answer("Bunday foydalanuvchi topilmadi! \nAdmin qilmoqchi bo'lgan user oldin botga /start bosishi kerak!!!")
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


    admin = await db.user.find_first(where={"telegramId": admin_id})

    if not admin:
        await callback_query.answer("⚠️ Bunday admin topilmadi!", show_alert=True)
        return

    await db.user.update(where={"telegramId": admin_id}, data={"role": "user"})

    await callback_query.message.edit_text(f"✅ Admin {admin.username} oddiy userga aylantirildi!")













#owner va admin uchun tugma qo'shish 
@dp.message_handler(lambda message: message.text == "➕ Yangi tugma qo‘shish", state=None)
async def add_new_button(message: types.Message, state: FSMContext):
    await message.answer("✏️ Yangi tugma nomini kiriting (64 ta belgidan oshmasin):")
    await state.set_state(ButtonCreation.name)

# **2. Tugma nomini kiritish**
@dp.message_handler(state=ButtonCreation.name)
async def enter_button_name(message: types.Message, state: FSMContext):
    existing_menu = await db.menu.find_first(where={"name": message.text})
    
    if existing_menu:
        await message.answer("❌ Bunday nomdagi tugma allaqachon mavjud! Iltimos, boshqa nom kiriting:")
        return 
    await state.update_data(name=message.text, messages=[], subbuttons=[])
    await message.answer("Tugmaga ma'lumot (matn yoki media) yuboring yoki ichki tugma qo‘shing:", reply_markup=get_add_data_btn_finish_buttons())
    await state.set_state(ButtonCreation.add_data)

# **3. Ma'lumot qo'shish**
@dp.message_handler(content_types=types.ContentType.ANY, state=ButtonCreation.add_data)
async def add_data_to_button(message: types.Message, state: FSMContext):
    data = await state.get_data()
    messages = data.get("messages", [])

    # Ma'lumotni shakllantirish
    msg = {}
    if message.text:
        msg["type"] = "text"
        msg["content"] = message.text
    elif message.photo:
        msg["type"] = "image"
        msg["content"] = message.photo[-1].file_id
    elif message.video:
        msg["type"] = "video"
        msg["content"] = message.video.file_id
    elif message.document:
        msg["type"] = "document"
        msg["content"] = message.document.file_id
    elif message.audio:
        msg["type"] = "audio"
        msg["content"] = message.audio.file_id
    elif message.caption and message.photo:
        msg["type"] = "image"
        msg["content"] = {
            "photo": message.photo[-1].file_id,
            "caption": message.caption
        }
    elif message.caption and message.video:
        msg["type"] = "video"
        msg["content"] = {
            "video": message.video.file_id,
            "caption": message.caption
        }

    # **Xatolikni oldini olish**
    if "type" not in msg or "content" not in msg:
        await message.answer("❌ Xatolik: Ma'lumot noto‘g‘ri formatda. Iltimos, qayta yuboring.")
        return

    messages.append(msg)
    await state.update_data(messages=messages)

    await message.answer("✅ Ma'lumot qo'shildi. Keyingi qadamni tanlang:", reply_markup=get_add_data_btn_finish_buttons())

# **4. Ma'lumot qo'shish tugmasi bosilganda**
@dp.callback_query_handler(lambda c: c.data == "add_more_data", state=ButtonCreation.add_data)
async def add_more_data(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("📩 Yangi ma'lumot (matn yoki media) yuboring:")

# **5. Ichki tugma qo'shish**
@dp.callback_query_handler(lambda c: c.data == "add_subbutton", state=ButtonCreation.add_data)
async def add_subbutton(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Ichki tugma nomini kiriting:")
    await state.set_state(ButtonCreation.add_subbutton)

# **6. Ichki tugma nomini kiritish**
@dp.message_handler(state=ButtonCreation.add_subbutton)
async def enter_subbutton_name(message: types.Message, state: FSMContext):
    data = await state.get_data()
    subbuttons = data.get("subbuttons", [])
    subbuttons.append({"name": message.text, "messages": []})
    await state.update_data(subbuttons=subbuttons)

    await message.answer(f"📌 Ichki tugma '{message.text}' yaratildi! Keyingi qadamni tanlang:", reply_markup=get_add_data_btn_finish_buttons())
    await state.set_state(ButtonCreation.add_data)  # Ichki tugmaga ma'lumot qo'shish uchun qayta `add_data` state'iga o'tamiz

# **7. Tugatish bosilganda**
@dp.callback_query_handler(lambda c: c.data == "finish", state=ButtonCreation.add_data)
async def finish_button_creation(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    menu_name = data.get("name", "Noma'lum tugma")
    messages = data.get("messages", [])
    subbuttons = data.get("subbuttons", [])

    if not messages and not any(sub["messages"] for sub in subbuttons):
        await callback.message.edit_text("❌ Siz tugmaga hech qanday ma'lumot kiritmadingiz! Kamida bitta ma'lumot qo'shing.")
        return

    menu = await db.menu.create({"name": menu_name, "creatorId": callback.from_user.id})
    # for msg in messages:
    #     await db.menumessage.create({"message": json.dumps(msg), "menuId": menu.id})

    for msg in messages:
        if "type" not in msg or "content" not in msg:
            print("DEBUG: msg ->", msg)  # msg obyektini tekshiramiz
            await callback.message.edit_text("❌ Xatolik: Ma'lumot noto‘g‘ri formatda.")
            return
        
        await db.menumessage.create({
            "type": msg["type"],  # ✅ Type maydonini aniq qo‘shamiz
            "message": json.dumps(msg["content"]),  # ✅ Content maydonini saqlaymiz
            "menuId": menu.id
        })


    for sub in subbuttons:
        if not sub["messages"]:
            await callback.message.edit_text(f"❌ Ichki tugma '{sub['name']}' ichida hech qanday ma'lumot yo‘q! Iltimos, unga ma'lumot qo'shing.")
            return
        sub_menu = await db.menu.create({"name": sub["name"], "creatorId": callback.from_user.id, "parentId": menu.id})
        for sub_msg in sub["messages"]:
            await db.menumessage.create({"message": json.dumps(sub_msg), "menuId": sub_menu.id})

    summary = (f"✅ Tugma yaratildi va bazaga saqlandi!\n\n"
               f"📌 Tugma nomi: {menu_name}\n"
               f"📩 Tugmaga kiritilgan ma'lumotlar soni: {len(messages)}\n"
               f"📂 Ichki tugmalar soni: {len(subbuttons)}\n")
    for sub in subbuttons:
        summary += f"  ├ {sub['name']} - {len(sub['messages'])} ta ma'lumot\n"

    await callback.message.answer(summary)
    await state.finish()


