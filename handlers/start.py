import logging
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.db import Database
from keyboards.settings import (
    get_education_base_keyboard,
    get_course_keyboard,
    get_group_keyboard
)
from keyboards.main import get_main_keyboard

logger = logging.getLogger(__name__)

router = Router()


class RegistrationStates(StatesGroup):
    choosing_base = State()
    choosing_course = State()
    choosing_group = State()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, db: Database):
    """Handle /start command"""
    user = db.get_user(message.from_user.id)
    
    if user and user.get('group_name'):
        # User already registered
        await message.answer(
            f"👋 С возвращением!\n\n"
            f"Ваша группа: {user['group_name']}\n"
            f"Используйте кнопки ниже для просмотра расписания.",
            reply_markup=get_main_keyboard()
        )
    else:
        # New user - start registration
        db.add_user(message.from_user.id)
        await message.answer(
            "👋 Добро пожаловать в бот расписания ПКЭУ!\n\n"
            "Выберите базу образования:",
            reply_markup=get_education_base_keyboard()
        )
        await state.set_state(RegistrationStates.choosing_base)


@router.callback_query(F.data.startswith("base_"))
async def process_base_selection(callback: CallbackQuery, state: FSMContext):
    """Handle education base selection"""
    base = callback.data.split("_")[1]
    await state.update_data(base=base)
    
    await callback.message.edit_text(
        f"Выбрана база: {base} классов\n\nВыберите курс:",
        reply_markup=get_course_keyboard(base)
    )
    await state.set_state(RegistrationStates.choosing_course)
    await callback.answer()


@router.callback_query(F.data == "back_to_base")
async def back_to_base(callback: CallbackQuery, state: FSMContext):
    """Go back to base selection"""
    await callback.message.edit_text(
        "Выберите базу образования:",
        reply_markup=get_education_base_keyboard()
    )
    await state.set_state(RegistrationStates.choosing_base)
    await callback.answer()


@router.callback_query(F.data.startswith("course_"))
async def process_course_selection(callback: CallbackQuery, state: FSMContext, db: Database):
    """Handle course selection"""
    course = int(callback.data.split("_")[1])
    data = await state.get_data()
    base = data.get("base")
    
    await state.update_data(course=course)
    
    # Get groups for this base and course
    groups = db.get_groups_by_base_and_course(base, course)
    
    if not groups:
        # If no groups in DB, show some default groups based on patterns
        groups = _get_default_groups(base, course)
        # Add groups to database
        for group in groups:
            db.add_group(group, base, course)
    
    if groups:
        await callback.message.edit_text(
            f"Курс: {course}\n\nВыберите группу:",
            reply_markup=get_group_keyboard(groups, base, course)
        )
        await state.set_state(RegistrationStates.choosing_group)
    else:
        await callback.message.edit_text(
            "❌ Группы не найдены. Попробуйте позже.",
            reply_markup=get_education_base_keyboard()
        )
        await state.set_state(RegistrationStates.choosing_base)
    
    await callback.answer()


@router.callback_query(F.data.startswith("back_to_course_"))
async def back_to_course(callback: CallbackQuery, state: FSMContext):
    """Go back to course selection"""
    base = callback.data.split("_")[-1]
    await state.update_data(base=base)
    
    await callback.message.edit_text(
        f"Выбрана база: {base} классов\n\nВыберите курс:",
        reply_markup=get_course_keyboard(base)
    )
    await state.set_state(RegistrationStates.choosing_course)
    await callback.answer()


@router.callback_query(F.data.startswith("group_"))
async def process_group_selection(callback: CallbackQuery, state: FSMContext, db: Database):
    """Handle group selection"""
    group_name = callback.data.split("group_")[1]
    data = await state.get_data()
    base = data.get("base")
    course = data.get("course")
    
    # Save user data
    db.update_user_group(callback.from_user.id, base, course, group_name)
    
    await callback.message.edit_text(
        f"✅ Настройка завершена!\n\n"
        f"Ваша группа: {group_name}\n"
        f"Курс: {course}\n"
        f"База: {base} классов\n\n"
        f"Теперь вы можете просматривать расписание!"
    )
    
    await callback.message.answer(
        "Выберите действие:",
        reply_markup=get_main_keyboard()
    )
    
    await state.clear()
    await callback.answer("✅ Группа сохранена!")


def _get_default_groups(base: str, course: int) -> list:
    """Get default groups based on base and course"""
    groups = []
    
    if base == "9":
        # Base 9 classes - groups like Б1-123, Д1-234, Ю1-345
        prefixes = ["Б", "Д", "Ю", "Ф", "ТД"]
        for prefix in prefixes:
            groups.append(f"{prefix}{course}-24")
    else:
        # Base 11 classes - groups like БУ-25, ТД-25, Ю-25
        current_year = 25  # 2025
        if course == 2:
            current_year = 24  # 2024 for 2nd year
        
        specialties = ["БУ", "ТД", "Ю", "Ф"]
        for spec in specialties:
            groups.append(f"{spec}-{current_year}")
    
    return groups
