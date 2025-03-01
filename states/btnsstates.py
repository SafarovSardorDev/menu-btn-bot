from aiogram.dispatcher.filters.state import State, StatesGroup

class AddAdminState(StatesGroup):
    waiting_for_admin_id = State()

class ButtonCreation(StatesGroup):
    name = State()
    add_data = State()
    confirm_data = State()
    add_subbutton = State()
    confirm = State()

# class NewButtonState(StatesGroup):
#     name = State()  # Tugma nomi
    
#     class AddDataOrSubButton(StatesGroup):  
#         choice = State()  # Ma'lumot yoki ichki tugma tanlash
#         media = State()  # Media (ixtiyoriy)
#         description = State()  # Matn (ixtiyoriy)
#         subbutton_name = State()  # Ichki tugma nomi
#         subbutton_data = State()  # Ichki tugma ma'lumoti
    
#     confirm = State()  # Barcha ma'lumotlarni tasdiqlash

