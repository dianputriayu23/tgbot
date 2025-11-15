"""
Start handler - handles /start command and initial setup
"""
import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import Database
from keyboards import (
    get_main_keyboard,
    get_base_selection_keyboard,
    get_course_selection_keyboard,
    get_group_selection_keyboard
)

logger = logging.getLogger(__name__)

router = Router()


class RegistrationStates(StatesGroup):
    """States for user registration process"""
    waiting_for_base = State()
    waiting_for_course = State()
    waiting_for_group = State()


def setup_handlers(db: Database):
    """Setup start handlers with database dependency"""
    
    @router.message(Command("start"))
    async def cmd_start(message: Message, state: FSMContext):
        """Handle /start command"""
        try:
            # Add user to database
            await db.add_user(
                user_id=message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name
            )
            
            # Check if user already has a group
            user = await db.get_user(message.from_user.id)
            
            if user and user.get('group_name'):
                # User already registered
                await message.answer(
                    f"👋 С возвращением, {message.from_user.first_name}!\n\n"
                    f"Ваша группа: {user['group_name']}\n"
                    f"База: {user['base']} классов, {user['course']} курс\n\n"
                    f"Используйте меню для просмотра расписания.",
                    reply_markup=get_main_keyboard()
                )
            else:
                # New user - start registration
                await message.answer(
                    f"👋 Привет, {message.from_user.first_name}!\n\n"
                    f"Я бот для просмотра расписания колледжа.\n\n"
                    f"Давайте настроим вашу группу. Выберите базу образования:",
                    reply_markup=get_base_selection_keyboard()
                )
                await state.set_state(RegistrationStates.waiting_for_base)
                
        except Exception as e:
            logger.error(f"Error in start handler: {e}")
            await message.answer(
                "❌ Произошла ошибка. Попробуйте позже.",
                reply_markup=get_main_keyboard()
            )
    
    @router.callback_query(F.data.startswith("base_"), RegistrationStates.waiting_for_base)
    async def process_base_selection(callback: CallbackQuery, state: FSMContext):
        """Process base selection"""
        try:
            base = int(callback.data.split("_")[1])
            await state.update_data(base=base)
            
            await callback.message.edit_text(
                f"✅ Выбрана база: {base} классов\n\n"
                f"Теперь выберите курс:",
                reply_markup=get_course_selection_keyboard(base)
            )
            await state.set_state(RegistrationStates.waiting_for_course)
            await callback.answer()
            
        except Exception as e:
            logger.error(f"Error in base selection: {e}")
            await callback.answer("❌ Ошибка выбора базы", show_alert=True)
    
    @router.callback_query(F.data == "back_to_base")
    async def back_to_base(callback: CallbackQuery, state: FSMContext):
        """Go back to base selection"""
        await callback.message.edit_text(
            "Выберите базу образования:",
            reply_markup=get_base_selection_keyboard()
        )
        await state.set_state(RegistrationStates.waiting_for_base)
        await callback.answer()
    
    @router.callback_query(F.data.startswith("course_"), RegistrationStates.waiting_for_course)
    async def process_course_selection(callback: CallbackQuery, state: FSMContext):
        """Process course selection"""
        try:
            course = int(callback.data.split("_")[1])
            data = await state.get_data()
            base = data.get('base')
            
            await state.update_data(course=course)
            
            # Get available groups
            groups = await db.get_groups(base, course)
            
            if not groups:
                await callback.message.edit_text(
                    f"❌ Для {base} базы, {course} курса пока нет доступных групп.\n"
                    f"Попробуйте выбрать другой курс или обратитесь к администратору."
                )
                await callback.answer()
                return
            
            await callback.message.edit_text(
                f"✅ Выбран курс: {course}\n\n"
                f"Выберите вашу группу:",
                reply_markup=get_group_selection_keyboard(groups, base, course)
            )
            await state.set_state(RegistrationStates.waiting_for_group)
            await callback.answer()
            
        except Exception as e:
            logger.error(f"Error in course selection: {e}")
            await callback.answer("❌ Ошибка выбора курса", show_alert=True)
    
    @router.callback_query(F.data == "back_to_course")
    async def back_to_course(callback: CallbackQuery, state: FSMContext):
        """Go back to course selection"""
        data = await state.get_data()
        base = data.get('base', 9)
        
        await callback.message.edit_text(
            "Выберите курс:",
            reply_markup=get_course_selection_keyboard(base)
        )
        await state.set_state(RegistrationStates.waiting_for_course)
        await callback.answer()
    
    @router.callback_query(F.data.startswith("group_"), RegistrationStates.waiting_for_group)
    async def process_group_selection(callback: CallbackQuery, state: FSMContext):
        """Process group selection"""
        try:
            group_name = callback.data.split("group_")[1]
            data = await state.get_data()
            base = data.get('base')
            course = data.get('course')
            
            # Update user's group
            await db.update_user_group(
                user_id=callback.from_user.id,
                base=base,
                course=course,
                group_name=group_name
            )
            
            await callback.message.edit_text(
                f"✅ Регистрация завершена!\n\n"
                f"Ваша группа: {group_name}\n"
                f"База: {base} классов\n"
                f"Курс: {course}\n\n"
                f"Теперь вы можете пользоваться ботом!"
            )
            
            await callback.message.answer(
                "Используйте меню для просмотра расписания:",
                reply_markup=get_main_keyboard()
            )
            
            await state.clear()
            await callback.answer()
            
        except Exception as e:
            logger.error(f"Error in group selection: {e}")
            await callback.answer("❌ Ошибка выбора группы", show_alert=True)
    
    return router
