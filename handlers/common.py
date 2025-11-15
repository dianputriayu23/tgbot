from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from datetime import datetime
import re
import logging
from aiogram.exceptions import TelegramBadRequest

from database.db import Database
from keyboards.reply import get_main_menu
from keyboards.inline import (
    get_education_form_kb, get_course_kb, get_settings_kb, get_group_kb
)
from utils.states import Registration

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, db: Database):
    await db.add_or_update_user(message.from_user.id, message.from_user.full_name, message.from_user.username)
    user = await db.get_user(message.from_user.id)
    if user and user[5]:
        await message.answer(f"👋 Привет, {message.from_user.full_name}!\nТвоя группа: <b>{user[5]}</b>. Можешь смотреть расписание.", reply_markup=get_main_menu())
    else:
        await message.answer("Добро пожаловать! Для начала выбери, на какой базе ты учишься:", reply_markup=get_education_form_kb())
        await state.set_state(Registration.choosing_education_form)

@router.message(F.text == "❓ Помощь")
async def cmd_help(message: Message, db: Database):
    users_count_tuple = await db.execute("SELECT COUNT(user_id) FROM users", fetch='one')
    count = users_count_tuple[0] if users_count_tuple else 0
    await message.answer(f"<b>Команды бота:</b>\n🔹 <b>Сегодня/Завтра</b> - показать расписание.\n🔹 <b>Понедельник...Суббота</b> - расписание на выбранный день.\n🔹 <b>Настройки</b> - изменить группу или уведомления.\n\n<i>Всего пользователей в боте: {count}</i>")
    
@router.message(F.text == "⚙️ Настройки")
async def cmd_settings(message: Message, db: Database):
    user = await db.get_user(message.from_user.id)
    if not user or not user[5]: await message.answer("Сначала выбери группу. Введи /start"); return
    notify_l = "✅ Включено" if user[6] else "❌ Выключено"
    notify_c = "✅ Включено" if user[7] else "❌ Выключено"
    notify_n = "✅ Включено" if len(user) > 8 and user[8] else "❌ Выключено"
    await message.answer(f"<b>⚙️ Ваш профиль:</b>\n<b>ID:</b> <code>{user[0]}</code>\n<b>Курс:</b> {user[4]}\n<b>Группа:</b> {user[5]}\n\n<b>Уведомления о парах:</b> {notify_l}\n<b>Уведомления об изменениях:</b> {notify_c}\n<b>Уведомления о новом расписании:</b> {notify_n}", reply_markup=get_settings_kb(user))

@router.callback_query(F.data.startswith("settings:"))
async def cq_settings_actions(callback: CallbackQuery, state: FSMContext, db: Database):
    await callback.answer()
    action = callback.data.split(":")[1]; user = await db.get_user(callback.from_user.id)
    if action == "change_group": await callback.message.edit_text("На какой базе ты учишься?", reply_markup=get_education_form_kb()); await state.set_state(Registration.choosing_education_form)
    elif action == "toggle_lessons": await db.update_user_notifications(user[0], notify_lessons=not user[6])
    elif action == "toggle_changes": await db.update_user_notifications(user[0], notify_changes=not user[7])
    elif action == "toggle_new_schedule": 
        current_value = user[8] if len(user) > 8 else True
        await db.execute("UPDATE users SET notify_new_schedule = ? WHERE user_id = ?", (not current_value, user[0]))
    if "toggle" in action:
        new_user = await db.get_user(user[0])
        notify_l = "✅ Включено" if new_user[6] else "❌ Выключено"
        notify_c = "✅ Включено" if new_user[7] else "❌ Выключено"
        notify_n = "✅ Включено" if len(new_user) > 8 and new_user[8] else "❌ Выключено"
        await callback.message.edit_text(f"<b>⚙️ Ваш профиль:</b>\n<b>ID:</b> <code>{new_user[0]}</code>\n<b>Курс:</b> {new_user[4]}\n<b>Группа:</b> {new_user[5]}\n\n<b>Уведомления о парах:</b> {notify_l}\n<b>Уведомления об изменениях:</b> {notify_c}\n<b>Уведомления о новом расписании:</b> {notify_n}", reply_markup=get_settings_kb(new_user))

@router.callback_query(F.data == "register_start")
async def cq_register_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer(); await callback.message.edit_text("На какой базе ты учишься?", reply_markup=get_education_form_kb()); await state.set_state(Registration.choosing_education_form)

@router.callback_query(Registration.choosing_education_form, F.data.startswith("register:form:"))
async def cq_choose_course(callback: CallbackQuery, state: FSMContext):
    await callback.answer(); form = callback.data.split(":")[2]; await state.update_data(education_form=form)
    await callback.message.edit_text("Отлично! Теперь выбери свой курс:", reply_markup=get_course_kb(form)); await state.set_state(Registration.choosing_course)

@router.callback_query(Registration.choosing_course, F.data.startswith("register:course:"))
async def cq_choose_group(callback: CallbackQuery, state: FSMContext, db: Database):
    await callback.answer()
    try:
        course = int(callback.data.split(":")[2]); user_data = await state.get_data(); education_form = user_data['education_form']; await state.update_data(course=course)
        all_groups = await db.get_all_groups()
        if not all_groups: 
            await callback.message.edit_text("😕 Группы в базе данных пока не найдены. Бот обрабатывает расписание. Попробуйте через минуту.", reply_markup=None)
            return

        current_year_short = datetime.now().year % 100
        final_groups = []
        for group in all_groups:
            match = re.search(r'(\d{2})', group)
            if not match: continue
            
            # Логика определения курса
            year_from_group = int(match.group(1))
            group_course = current_year_short - year_from_group + (1 if datetime.now().month >= 9 else 0)

            is_9_classes_format = bool(re.search(r'^[А-Яа-я]+[1-9]', group))
            is_11_classes_format = bool(re.search(r'^[А-Яа-я]+-', group))
            
            if education_form == '9_classes' and is_9_classes_format and group_course == course: final_groups.append(group)
            elif education_form == '11_classes' and is_11_classes_format and group_course == course: final_groups.append(group)

        if not final_groups: 
            await callback.message.edit_text("Не удалось найти группы для этого курса. Возможно, в расписании их нет.", reply_markup=get_course_kb(education_form))
            return
        
        await callback.message.edit_text("Отлично! Теперь выбери свою группу:", reply_markup=get_group_kb(sorted(final_groups), education_form))
        await state.set_state(Registration.choosing_group)
    except TelegramBadRequest as e:
        if "message is not modified" in str(e): logging.warning("Попытка изменить сообщение на идентичное. Игнорирую."); return
        else: logging.error(f"Ошибка Telegram API при выборе группы: {e}", exc_info=True)
    except Exception as e:
        logging.error(f"Общая ошибка при выборе группы: {e}", exc_info=True)
        try: await callback.message.edit_text("Произошла ошибка, попробуйте снова. /start")
        except: pass

@router.callback_query(Registration.choosing_group, F.data.startswith("register:group:"))
async def cq_finish_registration(callback: CallbackQuery, state: FSMContext, db: Database):
    await callback.answer(); group_name = callback.data.split(":")[2]; user_data = await state.get_data()
    await db.update_user_profile(user_id=callback.from_user.id, education_form=user_data.get('education_form', 'N/A'), course=user_data.get('course', 0), group_name=group_name)
    await state.clear(); await callback.message.delete(); await callback.message.answer(f"Отлично! Твоя группа <b>{group_name}</b> сохранена.", reply_markup=get_main_menu())

@router.callback_query(F.data.startswith("register:course_back:"))
async def cq_back_to_course(callback: CallbackQuery, state: FSMContext):
    await callback.answer(); form = callback.data.split(":")[2]; await state.update_data(education_form=form)
    await callback.message.edit_text("Выбери свой курс:", reply_markup=get_course_kb(form)); await state.set_state(Registration.choosing_course)