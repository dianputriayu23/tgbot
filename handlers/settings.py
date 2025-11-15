"""
Settings handler - manages user settings and notifications
"""
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import Database
from keyboards import (
    get_main_keyboard,
    get_settings_keyboard,
    get_base_selection_keyboard,
    get_course_selection_keyboard,
    get_group_selection_keyboard,
    get_notifications_keyboard
)

logger = logging.getLogger(__name__)

router = Router()


class ChangeGroupStates(StatesGroup):
    """States for changing group"""
    waiting_for_base = State()
    waiting_for_course = State()
    waiting_for_group = State()


def setup_handlers(db: Database):
    """Setup settings handlers with database dependency"""
    
    @router.message(F.text == "⚙️ Настройки")
    async def show_settings(message: Message):
        """Show settings menu"""
        try:
            user = await db.get_user(message.from_user.id)
            
            if not user or not user.get('group_name'):
                await message.answer(
                    "❌ Сначала нужно выбрать группу.\n"
                    "Используйте команду /start для регистрации."
                )
                return
            
            await message.answer(
                "⚙️ Настройки\n\n"
                "Выберите что хотите изменить:",
                reply_markup=get_settings_keyboard()
            )
            
        except Exception as e:
            logger.error(f"Error showing settings: {e}")
            await message.answer(
                "❌ Ошибка при открытии настроек.",
                reply_markup=get_main_keyboard()
            )
    
    @router.message(F.text == "🔔 Уведомления")
    async def show_notifications_settings(message: Message):
        """Show notification settings"""
        try:
            user = await db.get_user(message.from_user.id)
            
            if not user:
                await message.answer("❌ Пользователь не найден.")
                return
            
            enabled = bool(user.get('notifications_enabled', 1))
            
            status = "включены ✅" if enabled else "выключены ❌"
            
            await message.answer(
                f"🔔 Уведомления\n\n"
                f"Текущий статус: {status}\n\n"
                f"Уведомления отправляются каждый вечер с расписанием на следующий день.",
                reply_markup=get_notifications_keyboard(enabled)
            )
            
        except Exception as e:
            logger.error(f"Error showing notification settings: {e}")
            await message.answer(
                "❌ Ошибка при открытии настроек уведомлений.",
                reply_markup=get_settings_keyboard()
            )
    
    @router.callback_query(F.data == "notif_on")
    async def enable_notifications(callback: CallbackQuery):
        """Enable notifications"""
        try:
            await db.set_notifications(callback.from_user.id, True)
            
            await callback.message.edit_text(
                "🔔 Уведомления\n\n"
                "Текущий статус: включены ✅\n\n"
                "Уведомления отправляются каждый вечер с расписанием на следующий день.",
                reply_markup=get_notifications_keyboard(True)
            )
            await callback.answer("✅ Уведомления включены")
            
        except Exception as e:
            logger.error(f"Error enabling notifications: {e}")
            await callback.answer("❌ Ошибка", show_alert=True)
    
    @router.callback_query(F.data == "notif_off")
    async def disable_notifications(callback: CallbackQuery):
        """Disable notifications"""
        try:
            await db.set_notifications(callback.from_user.id, False)
            
            await callback.message.edit_text(
                "🔔 Уведомления\n\n"
                "Текущий статус: выключены ❌\n\n"
                "Уведомления отправляются каждый вечер с расписанием на следующий день.",
                reply_markup=get_notifications_keyboard(False)
            )
            await callback.answer("❌ Уведомления выключены")
            
        except Exception as e:
            logger.error(f"Error disabling notifications: {e}")
            await callback.answer("❌ Ошибка", show_alert=True)
    
    @router.message(F.text == "🔄 Изменить группу")
    async def change_group_start(message: Message, state: FSMContext):
        """Start group change process"""
        try:
            await message.answer(
                "🔄 Изменение группы\n\n"
                "Выберите базу образования:",
                reply_markup=get_base_selection_keyboard()
            )
            await state.set_state(ChangeGroupStates.waiting_for_base)
            
        except Exception as e:
            logger.error(f"Error starting group change: {e}")
            await message.answer(
                "❌ Ошибка при изменении группы.",
                reply_markup=get_settings_keyboard()
            )
    
    @router.callback_query(F.data.startswith("base_"), ChangeGroupStates.waiting_for_base)
    async def process_base_change(callback: CallbackQuery, state: FSMContext):
        """Process base selection for group change"""
        try:
            base = int(callback.data.split("_")[1])
            await state.update_data(base=base)
            
            await callback.message.edit_text(
                f"✅ Выбрана база: {base} классов\n\n"
                f"Выберите курс:",
                reply_markup=get_course_selection_keyboard(base)
            )
            await state.set_state(ChangeGroupStates.waiting_for_course)
            await callback.answer()
            
        except Exception as e:
            logger.error(f"Error in base change: {e}")
            await callback.answer("❌ Ошибка", show_alert=True)
    
    @router.callback_query(F.data.startswith("course_"), ChangeGroupStates.waiting_for_course)
    async def process_course_change(callback: CallbackQuery, state: FSMContext):
        """Process course selection for group change"""
        try:
            course = int(callback.data.split("_")[1])
            data = await state.get_data()
            base = data.get('base')
            
            await state.update_data(course=course)
            
            groups = await db.get_groups(base, course)
            
            if not groups:
                await callback.message.edit_text(
                    f"❌ Для {base} базы, {course} курса нет доступных групп."
                )
                await callback.answer()
                return
            
            await callback.message.edit_text(
                f"✅ Выбран курс: {course}\n\n"
                f"Выберите группу:",
                reply_markup=get_group_selection_keyboard(groups, base, course)
            )
            await state.set_state(ChangeGroupStates.waiting_for_group)
            await callback.answer()
            
        except Exception as e:
            logger.error(f"Error in course change: {e}")
            await callback.answer("❌ Ошибка", show_alert=True)
    
    @router.callback_query(F.data.startswith("group_"), ChangeGroupStates.waiting_for_group)
    async def process_group_change(callback: CallbackQuery, state: FSMContext):
        """Process group selection for group change"""
        try:
            group_name = callback.data.split("group_")[1]
            data = await state.get_data()
            base = data.get('base')
            course = data.get('course')
            
            await db.update_user_group(
                user_id=callback.from_user.id,
                base=base,
                course=course,
                group_name=group_name
            )
            
            await callback.message.edit_text(
                f"✅ Группа успешно изменена!\n\n"
                f"Новая группа: {group_name}\n"
                f"База: {base} классов\n"
                f"Курс: {course}"
            )
            
            await callback.message.answer(
                "Настройки обновлены!",
                reply_markup=get_main_keyboard()
            )
            
            await state.clear()
            await callback.answer()
            
        except Exception as e:
            logger.error(f"Error in group change: {e}")
            await callback.answer("❌ Ошибка", show_alert=True)
    
    @router.message(F.text == "◀️ Назад в меню")
    async def back_to_menu(message: Message, state: FSMContext):
        """Go back to main menu"""
        await state.clear()
        await message.answer(
            "Главное меню:",
            reply_markup=get_main_keyboard()
        )
    
    return router
