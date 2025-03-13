from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InputMediaPhoto, InputMediaVideo, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters import Text
from loader import dp, db
from aiogram.types  import ContentTypes, ContentType
from states.btnsstates import AddAdminState, ButtonCreation
from keyboards.defaultbtns import owner_panel_keyboard, admin_panel_keyboard
from keyboards.inlinebtns import get_remove_admin_buttons, cancel_button, get_add_data_btn_finish_buttons
from dotenv import load_dotenv
from aiogram.utils.exceptions import MessageNotModified
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

@dp.message_handler(lambda message: message.text == "➕ Yangi tugma qo‘shish", state="*")
async def add_new_button(message: types.Message, state: FSMContext):
    await message.answer("✏️ Yangi tugma nomini kiriting (64 ta belgidan oshmasin):")
    await state.set_state(ButtonCreation.name)

@dp.message_handler(state=ButtonCreation.name)
async def enter_button_name(message: types.Message, state: FSMContext):
    existing_menu = await db.menu.find_first(where={"name": message.text})
    if existing_menu:
        await message.answer("❌ Bunday nomdagi tugma allaqachon mavjud! Iltimos, boshqa nom kiriting:")
        return
    
    await state.update_data(name=message.text, messages=[], subbuttons=[])
    await message.answer("Tugmaga ma'lumot (matn yoki media) yuboring yoki ichki tugma qo‘shing:", reply_markup=get_add_data_btn_finish_buttons())
    await state.set_state(ButtonCreation.add_data)

@dp.callback_query_handler(lambda c: c.data == "add_more_data", state=ButtonCreation.add_data)
async def add_more_data(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("📩 Yangi ma'lumot (matn yoki media) yuboring:")


@dp.callback_query_handler(lambda c: c.data == "add_subbutton", state=ButtonCreation.add_data)
async def add_subbutton(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Ichki tugma nomini kiriting:")
    await state.set_state(ButtonCreation.add_subbutton)


@dp.message_handler(state=ButtonCreation.add_subbutton)
async def enter_subbutton_name(message: types.Message, state: FSMContext):
    data = await state.get_data()
    parent_id = data.get("current_subbutton") or data.get("parent_id") 
    subbuttons = data.get("subbuttons", [])

    subbuttons.append({
        "name": message.text,
        "messages": [],
        "parentId": parent_id
    })

    await state.update_data(subbuttons=subbuttons)
    await message.answer(
        f"📌 Ichki tugma '{message.text}' yaratildi! Keyingi qadamni tanlang:",
        reply_markup=get_add_data_btn_finish_buttons()
    )
    await state.set_state(ButtonCreation.add_data)


@dp.callback_query_handler(lambda c: c.data.startswith("subbtn_"), state=ButtonCreation.add_data)
async def select_subbutton(callback: types.CallbackQuery, state: FSMContext):
    subbutton_name = callback.data.replace("subbtn_", "")
    await state.update_data(current_subbutton=subbutton_name)
    await callback.message.edit_text(f"📩 '{subbutton_name}' ichki tugmasiga ma'lumot qo'shing:")


@dp.message_handler(content_types=types.ContentType.ANY, state=ButtonCreation.add_data)
async def add_data_to_button(message: types.Message, state: FSMContext):
    data = await state.get_data()
    messages = data.get("messages", [])
    subbuttons = data.get("subbuttons", [])
    current_subbutton = data.get("current_subbutton")

    media_group_id = message.media_group_id if message.media_group_id else None
    content_types = {
        "text": message.text if message.text else None,
        "image": message.photo[-1].file_id if message.photo else None,
        "video": message.video.file_id if message.video else None,
        "document": message.document.file_id if message.document else None,
        "gif": message.animation.file_id if message.animation else None,
        "audio": message.audio.file_id if message.audio else None,
        "voice": message.voice.file_id if message.voice else None,
        "sticker": message.sticker.file_id if message.sticker else None,
        "contact": {
            "phone_number": message.contact.phone_number,
            "first_name": message.contact.first_name,
            "last_name": message.contact.last_name
        } if message.contact else None,
        "location": {
            "latitude": message.location.latitude,
            "longitude": message.location.longitude
        } if message.location else None
    }

    
    new_message = None
    for media_type, content in content_types.items():
        if content:
            new_message = {
                "type": media_type,
                "message": {
                    "content": content if media_type not in ["contact", "location"] else {},
                    "caption": message.caption if hasattr(message, 'caption') and message.caption else None,
                    "media_group_id": media_group_id,
                    "extra": {}
                }
            }
            if media_group_id:
                existing_group = [m for m in messages if m.get("media_group_id") == media_group_id]
                if existing_group:
                    existing_group[0]["message"]["content"].append(content)  # Bir xil media_group ichiga qo‘shish
                else:
                    new_message["message"]["content"] = [content]
                    messages.append(new_message)
            else:
                messages.append(new_message)
            if media_type == "contact":
                new_message["message"]["content"] = {
                    "phone_number": content.phone_number,
                    "first_name": content.first_name,
                    "last_name": content.last_name
                }
            elif media_type == "location":
                new_message["message"]["content"] = {
                    "latitude": content.latitude,
                    "longitude": content.longitude
                }
            break  # Faqat bitta media turi ishlaydi

    if new_message:
        if current_subbutton:
            # Ichki tugmani topib, unga ma'lumot qo‘shamiz
            for sub in subbuttons:
                if sub["name"] == current_subbutton:
                    sub["messages"].append(new_message)
                    break
            await state.update_data(subbuttons=subbuttons)
        else:
            # Agar hech qanday ichki tugma tanlanmagan bo‘lsa, asosiy tugmaga qo‘shamiz
            messages.append(new_message)
            await state.update_data(messages=messages)

    await message.answer("✅ Ma'lumot qo'shildi. Keyingi qadamni tanlang:", reply_markup=get_add_data_btn_finish_buttons())

@dp.callback_query_handler(lambda c: c.data == "finish", state=ButtonCreation.add_data)
async def finish_button_creation(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    menu_name = data.get("name", "Noma'lum tugma")
    messages = data.get("messages", [])
    subbuttons = data.get("subbuttons", [])
    creator_id = callback.from_user.id
    parent_id = data.get("parent_id")

    # Agar tugmaga hech qanday ma'lumot qo'shilmagan bo'lsa
    if not messages and not any(sub.get("messages") for sub in subbuttons):
        await callback.message.edit_text(
            "❌ Siz tugmaga hech qanday ma'lumot kiritmadingiz! Kamida bitta ma'lumot qo‘shing.",
            reply_markup=get_add_data_btn_finish_buttons()
        )
        return
    
    try:
        # Asosiy tugmani yaratish
        menu = await db.menu.create({
            "name": menu_name,
            "creatorId": creator_id,
            "parentId": parent_id,
            "order": await db.menu.count(where={"parentId": parent_id})
        })

        # Tugmaga tegishli ma'lumotlarni saqlash
        await save_messages(messages, menu.id)

        # Ichki tugmalarni qayta ishlash
        await create_submenus(subbuttons, menu.id, creator_id)

        # Yaratilgan tugmalar bo‘yicha hisobot
        summary = f"✅ Tugma yaratildi va bazaga saqlandi!\n\n📌 Tugma nomi: {menu_name}\n📩 Tugmaga kiritilgan ma'lumotlar soni: {len(messages)}\n📂 Ichki tugmalar soni: {len(subbuttons)}\n"
        for sub in subbuttons:
            summary += f"  ├ {sub['name']} - {len(sub.get('messages', []))} ta ma'lumot\n"

        await callback.message.edit_text(summary)
        await state.finish()
    except Exception as e:
        await callback.message.answer("❌ Ma'lumotlarni saqlashda xatolik yuz berdi!")
        print(f"❌ Xatolik: {e}")

async def save_messages(messages, menu_id):
    """Berilgan xabarlarni tegishli `menuId` bilan saqlaydi"""
    if messages:
        await asyncio.gather(*[
            db.menumessage.create({
                "message": json.dumps(msg),
                "menuId": menu_id
            }) for msg in messages
        ])

async def create_submenus(subbuttons, parent_id, creator_id):
    """Ichki tugmalarni rekursiv ravishda yaratadi"""
    for sub in subbuttons:
        sub_menu = await db.menu.create({
            "name": sub["name"],
            "creatorId": creator_id,
            "parentId": parent_id,
            "order": await db.menu.count(where={"parentId": parent_id})
        })

        # Ichki tugmaga tegishli ma'lumotlarni saqlash
        await save_messages(sub.get("messages", []), sub_menu.id)

        # Ichki tugmada yana ichki tugmalar bo‘lsa, rekursiv chaqiramiz
        if sub.get("subbuttons"):
            await create_submenus(sub["subbuttons"], sub_menu.id, creator_id)


#parentId yozildi
# @dp.callback_query_handler(lambda c: c.data == "finish", state=ButtonCreation.add_data)
# async def finish_button_creation(callback: types.CallbackQuery, state: FSMContext):
#     data = await state.get_data()
#     menu_name = data.get("name", "Noma'lum tugma")
#     messages = data.get("messages", [])
#     subbuttons = data.get("subbuttons", [])
#     creator_id = callback.from_user.id
#     parent_id = data.get("parent_id")

#     # Agar tugmaga hech qanday ma'lumot qo'shilmagan bo'lsa
#     if not messages and not any(sub.get("messages") for sub in subbuttons):
#         await callback.message.edit_text(
#             "❌ Siz tugmaga hech qanday ma'lumot kiritmadingiz! Kamida bitta ma'lumot qo‘shing.",
#             reply_markup=get_add_data_btn_finish_buttons()
#         )
#         return
    
#     try:
#         # Asosiy tugmani yaratish
#         menu = await db.menu.create({
#             "name": menu_name,
#             "creatorId": creator_id,
#             "parentId": parent_id,
#             "order": await db.menu.count(where={"parentId": parent_id})
#         })

#         # Tugmaga tegishli ma'lumotlarni saqlash
#         await asyncio.gather(*[
#             db.menumessage.create({
#                 "message": json.dumps(msg),
#                 "menuId": menu.id
#             }) for msg in messages
#         ])

#         # Ichki tugmalarni qayta ishlash (rekursiv funksiya)
#         async def create_submenus(subbuttons, parent_id):
#             for sub in subbuttons:
#                 sub_menu = await db.menu.create({
#                     "name": sub["name"],
#                     "creatorId": creator_id,
#                     "parentId": parent_id,
#                     "order": await db.menu.count(where={"parentId": parent_id})
#                 })

#                 if sub.get("messages"):
#                     await asyncio.gather(*[
#                         db.menumessage.create({
#                             "message": json.dumps(sub_msg),
#                             "menuId": sub_menu.id
#                         }) for sub_msg in sub["messages"]
#                     ])

#                 # Rekursiv chaqiruv - agar yana ichki tugmalar bo‘lsa
#                 if sub.get("subbuttons"):
#                     await create_submenus(sub["subbuttons"], sub_menu.id)

#         await create_submenus(subbuttons, menu.id)

#         # Yaratilgan tugmalar bo‘yicha hisobot
#         summary = f"✅ Tugma yaratildi va bazaga saqlandi!\n\n📌 Tugma nomi: {menu_name}\n📩 Tugmaga kiritilgan ma'lumotlar soni: {len(messages)}\n📂 Ichki tugmalar soni: {len(subbuttons)}\n"
#         for sub in subbuttons:
#             summary += f"  ├ {sub['name']} - {len(sub.get('messages', []))} ta ma'lumot\n"

#         await callback.message.answer(summary)
#         await state.finish()
#     except Exception as e:
#         await callback.message.answer("❌ Ma'lumotlarni saqlashda xatolik yuz berdi!")
#         print(f"❌ Xatolik: {e}")




@dp.callback_query_handler(lambda c: c.data == "cancel", state="*")
async def cancel_process(callback: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await callback.message.edit_text("❌ Jarayon bekor qilindi.")


#     data = await state.get_data()
#     menu_name = data.get("name", "Noma'lum tugma")
#     messages = data.get("messages", [])
#     subbuttons = data.get("subbuttons", [])
#     creator_id = callback.from_user.id

#     if not messages and not any(sub["messages"] for sub in subbuttons):
#         await callback.message.edit_text(
#             "❌ Siz tugmaga hech qanday ma'lumot kiritmadingiz! Kamida bitta ma'lumot qo‘shing.",
#             reply_markup=get_add_data_btn_finish_buttons()
#         )
#         return

#     try:
#         for msg in messages:
#             if msg["type"] not in VALID_MEDIA_TYPES or not msg["message"].get("content"):
#                 await callback.message.answer(f"❌ Noto‘g‘ri media turi yoki bo‘sh content: {msg['type']}!")
#                 return

#         menu = await db.menu.create({
#             "name": menu_name,
#             "creatorId": creator_id,
#             "parentId": None,
#             "order": 0
#         })

#         for msg in messages:
#             await db.menumessage.create({
#                 "type": msg["type"],
#                 "message": json.dumps(msg["message"]),
#                 "menuId": menu.id
#             })

#         for sub in subbuttons:
#             if sub["messages"]:
#                 sub_menu = await db.menu.create({
#                     "name": sub["name"],
#                     "creatorId": creator_id,
#                     "parentId": menu.id,
#                     "order": 0
#                 })
#                 for sub_msg in sub["messages"]:
#                     await db.menumessage.create({
#                         "type": sub_msg["type"],
#                         "message": json.dumps(sub_msg["message"]),
#                         "menuId": sub_menu.id
#                     })

#         summary = f"✅ Tugma yaratildi va bazaga saqlandi!\n\n📌 Tugma nomi: {menu_name}\n📩 Tugmaga kiritilgan ma'lumotlar soni: {len(messages)}\n📂 Ichki tugmalar soni: {len(subbuttons)}\n"
#         for sub in subbuttons:
#             summary += f"  ├ {sub['name']} - {len(sub['messages'])} ta ma'lumot\n"

#         await callback.message.answer(summary)
#         await state.finish()

#     except Exception as e:
#         await callback.message.answer("❌ Ma'lumotlarni saqlashda xatolik yuz berdi!")
#         print(f"❌ Xatolik: {e}")

# SET client_encoding = 'UTF8';