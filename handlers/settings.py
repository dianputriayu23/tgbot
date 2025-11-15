import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from database.db import Database
from keyboards.settings import get_settings_keyboard
from keyboards.main import get_main_keyboard
from handlers.start import RegistrationStates, get_education_base_keyboard

logger = logging.getLogger(__name__)

router = Router()


@router.message(F.text == "⚙️ Настройки")
async def show_settings(message: Message, db: Database):
    """Show settings menu"""
    user = db.get_user(message.from_user.id)
    
    if not user:
        await message.answer(
            "❌ Сначала настройте бота с помощью команды /start"
        )
        return
    
    notif_pairs = "✅" if user.get('notifications_pairs', 1) else "❌"
    notif_changes = "✅" if user.get('notifications_changes', 1) else "❌"
    notif_schedule = "✅" if user.get('notifications_schedule', 1) else "❌"
    
    settings_text = (
        "⚙️ <b>Настройки</b>\n\n"
        f"👥 Группа: <b>{user.get('group_name', 'не выбрана')}</b>\n"
        f"📚 Курс: <b>{user.get('course', 'не выбран')}</b>\n\n"
        f"🔔 Уведомления о парах: {notif_pairs}\n"
        f"🔔 Уведомления об изменениях: {notif_changes}\n"
        f"🔔 Уведомления о новом расписании: {notif_schedule}\n"
    )
    
    await message.answer(
        settings_text,
        parse_mode="HTML",
        reply_markup=get_settings_keyboard()
    )


@router.callback_query(F.data == "change_group")
async def change_group(callback: CallbackQuery, state: FSMContext):
    """Start group change process"""
    await callback.message.edit_text(
        "🔄 Смена группы\n\n"
        "Выберите базу образования:",
        reply_markup=get_education_base_keyboard()
    )
    await state.set_state(RegistrationStates.choosing_base)
    await callback.answer()


@router.callback_query(F.data == "toggle_notif_pairs")
async def toggle_notif_pairs(callback: CallbackQuery, db: Database):
    """Toggle notifications about lessons"""
    user = db.get_user(callback.from_user.id)
    current_value = user.get('notifications_pairs', 1)
    new_value = 0 if current_value else 1
    
    db.update_user_notifications(callback.from_user.id, "pairs", new_value)
    
    status = "включены" if new_value else "выключены"
    await callback.answer(f"Уведомления о парах {status}")
    
    # Refresh settings display
    await show_settings_callback(callback, db)


@router.callback_query(F.data == "toggle_notif_changes")
async def toggle_notif_changes(callback: CallbackQuery, db: Database):
    """Toggle notifications about schedule changes"""
    user = db.get_user(callback.from_user.id)
    current_value = user.get('notifications_changes', 1)
    new_value = 0 if current_value else 1
    
    db.update_user_notifications(callback.from_user.id, "changes", new_value)
    
    status = "включены" if new_value else "выключены"
    await callback.answer(f"Уведомления об изменениях {status}")
    
    # Refresh settings display
    await show_settings_callback(callback, db)


@router.callback_query(F.data == "toggle_notif_schedule")
async def toggle_notif_schedule(callback: CallbackQuery, db: Database):
    """Toggle notifications about new schedule"""
    user = db.get_user(callback.from_user.id)
    current_value = user.get('notifications_schedule', 1)
    new_value = 0 if current_value else 1
    
    db.update_user_notifications(callback.from_user.id, "schedule", new_value)
    
    status = "включены" if new_value else "выключены"
    await callback.answer(f"Уведомления о новом расписании {status}")
    
    # Refresh settings display
    await show_settings_callback(callback, db)


@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery):
    """Go back to main menu"""
    await callback.message.delete()
    await callback.message.answer(
        "Главное меню:",
        reply_markup=get_main_keyboard()
    )
    await callback.answer()


async def show_settings_callback(callback: CallbackQuery, db: Database):
    """Show settings menu (for callback)"""
    user = db.get_user(callback.from_user.id)
    
    notif_pairs = "✅" if user.get('notifications_pairs', 1) else "❌"
    notif_changes = "✅" if user.get('notifications_changes', 1) else "❌"
    notif_schedule = "✅" if user.get('notifications_schedule', 1) else "❌"
    
    settings_text = (
        "⚙️ <b>Настройки</b>\n\n"
        f"👥 Группа: <b>{user.get('group_name', 'не выбрана')}</b>\n"
        f"📚 Курс: <b>{user.get('course', 'не выбран')}</b>\n\n"
        f"🔔 Уведомления о парах: {notif_pairs}\n"
        f"🔔 Уведомления об изменениях: {notif_changes}\n"
        f"🔔 Уведомления о новом расписании: {notif_schedule}\n"
    )
    
    await callback.message.edit_text(
        settings_text,
        parse_mode="HTML",
        reply_markup=get_settings_keyboard()
    )
