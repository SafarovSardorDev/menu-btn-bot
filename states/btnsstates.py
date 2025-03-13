from aiogram.dispatcher.filters.state import State, StatesGroup

class AddAdminState(StatesGroup):
    waiting_for_admin_id = State()

class ButtonCreation(StatesGroup):
    name = State()           # Yangi tugma nomini kiritish
    add_data = State()       # Tugmaga matn yoki media qo'shish
    add_subbutton = State()  # Ichki tugma nomini kiritish
    add_sub_data = State()
    active_subbutton = State()


