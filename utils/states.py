from aiogram.fsm.state import State, StatesGroup

class Registration(StatesGroup):
    choosing_education_form = State()
    choosing_course = State()
    choosing_group = State()