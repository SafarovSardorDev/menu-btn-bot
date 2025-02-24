from aiogram.dispatcher.filters.state import State, StatesGroup

class AddAdminState(StatesGroup):
    waiting_for_admin_id = State()
