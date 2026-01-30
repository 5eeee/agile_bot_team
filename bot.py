import asyncio
import logging
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from config import BOT_TOKEN, ADMIN_ID, CHATS, PROJECTS, STATUSES, PRIORITIES, RESOURCE_TYPES, save_chats, load_chats

# ==================== НАСТРОЙКА ЛОГИРОВАНИЯ ====================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== ИНИЦИАЛИЗАЦИЯ БОТА ====================
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# ==================== СОСТОЯНИЯ (FSM) ====================
class DeadlineForm(StatesGroup):
    project = State()
    date = State()
    task = State()
    priority = State()
    responsible = State()
    status = State()

class QuestionForm(StatesGroup):
    project = State()
    question = State()
    priority = State()
    to_who = State()
    context = State()

class DoneForm(StatesGroup):
    project = State()
    task = State()
    status = State()
    link = State()
    check = State()

class IdeaForm(StatesGroup):
    project = State()
    idea = State()
    priority = State()
    benefit = State()

class ResourceForm(StatesGroup):
    project = State()
    resource_type = State()
    description = State()
    link = State()

class ReportForm(StatesGroup):
    period = State()
    projects = State()
    completed = State()
    problems = State()
    plans = State()

# ==================== КЛАВИАТУРЫ ====================
def create_keyboard(items_dict, prefix="item"):
    """Создает клавиатуру из словаря"""
    buttons = []
    for key, value in items_dict.items():
        buttons.append(InlineKeyboardButton(text=value, callback_data=f"{prefix}_{key}"))
    
    # Разбиваем по 2 кнопки в ряд
    rows = []
    for i in range(0, len(buttons), 2):
        rows.append(buttons[i:i+2])
    
    return InlineKeyboardMarkup(inline_keyboard=rows)

def projects_keyboard(prefix="proj"):
    return create_keyboard(PROJECTS, prefix)

def priorities_keyboard(prefix="prio"):
    return create_keyboard(PRIORITIES, prefix)

def statuses_keyboard(prefix="stat"):
    return create_keyboard(STATUSES, prefix)

def resource_types_keyboard(prefix="res"):
    return create_keyboard(RESOURCE_TYPES, prefix)

def period_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📅 За день", callback_data="period_day"),
            InlineKeyboardButton(text="📅 За неделю", callback_data="period_week")
        ],
        [
            InlineKeyboardButton(text="📅 За месяц", callback_data="period_month"),
            InlineKeyboardButton(text="📅 Другой период", callback_data="period_custom")
        ]
    ])
    return keyboard

# ==================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ====================
def send_to_topic(chat_type, text):
    """Отправляет сообщение в указанную тему"""
    thread_id = CHATS[chat_type]
    if thread_id == 0:
        return False, f"❌ Тема для '{chat_type}' не настроена!"
    
    try:
        bot.send_message(
            chat_id=CHATS['chat_id'],
            message_thread_id=thread_id,
            text=text
        )
        return True, f"✅ Сообщение отправлено в тему!"
    except Exception as e:
        logger.error(f"Ошибка отправки: {e}")
        return False, f"❌ Ошибка отправки: {str(e)}"

# ==================== КОМАНДЫ СТАРТА И ПОМОЩИ ====================
@dp.message(Command("start", "help"))
async def cmd_start(message: types.Message):
    text = """
🚀 <b>Agile Team Bot</b> - система управления проектами

<b>📋 ОСНОВНЫЕ КОМАНДЫ:</b>
/deadline - Создать дедлайн
/question - Задать вопрос
/done - Отметить задачу выполненной
/idea - Предложить идею
/resource - Добавить ресурс
/report - Создать отчет

<b>📊 ИНФОРМАЦИЯ:</b>
/projects - Список проектов
/statuses - Список статусов
/priorities - Список приоритетов
/getinfo - Информация о теме

<b>⚙️ НАСТРОЙКА (только админ):</b>
/setall - Настроить все темы разом
/check - Проверить настройки

<b>🎯 КАК РАБОТАТЬ:</b>
1. Выберите команду (например /deadline)
2. Заполните данные через диалог
3. Бот отправит сообщение в нужную тему
"""
    await message.answer(text)

# ==================== КОМАНДЫ НАСТРОЙКИ ====================
@dp.message(Command("getinfo"))
async def cmd_getinfo(message: types.Message):
    """Получить информацию о текущей теме"""
    chat_id = message.chat.id
    chat_title = message.chat.title or "Личные сообщения"
    thread_id = message.message_thread_id if hasattr(message, 'message_thread_id') else "Нет (не форум)"
    
    text = f"""
📊 <b>ИНФОРМАЦИЯ О ТЕКУЩЕЙ ТЕМЕ:</b>

• <b>Название:</b> {chat_title}
• <b>ID чата:</b> <code>{chat_id}</code>
• <b>ID темы:</b> <code>{thread_id}</code>
"""
    await message.answer(text)

@dp.message(Command("setall"))
async def cmd_setall(message: types.Message):
    """Настроить все темы одной командой"""
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ Только для администратора")
        return
    
    # Настраиваем все темы согласно твоим данным
    CHATS.update({
        'chat_id': -1003761419747,
        'deadlines': 4,
        'questions': 8,
        'done': 10,
        'ideas': 15,
        'resources': 6,
        'reports': 19,
        'main': 2
    })
    
    if save_chats(CHATS):
        text = """
✅ <b>Все темы настроены!</b>

• 📅 Дедлайны: <code>ID 4</code>
• ❓ Вопросы: <code>ID 8</code>
• ✅ Готово: <code>ID 10</code>
• 💡 Идеи: <code>ID 15</code>
• 🗃 Ресурсы: <code>ID 6</code>
• 📊 Отчеты: <code>ID 19</code>
• 📌 Главный: <code>ID 2</code>

Теперь можно тестировать команды!
"""
        await message.answer(text)
    else:
        await message.answer("❌ Ошибка сохранения настроек")

@dp.message(Command("check"))
async def cmd_check(message: types.Message):
    """Проверить текущие настройки"""
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ Только для администратора")
        return
    
    chat_names = {
        'deadlines': '📅 Дедлайны',
        'questions': '❓ Вопросы',
        'done': '✅ Готово',
        'ideas': '💡 Идеи',
        'resources': '🗃 Ресурсы',
        'reports': '📊 Отчеты',
        'main': '📌 Главный'
    }
    
    text = f"""
📊 <b>ТЕКУЩИЕ НАСТРОЙКИ:</b>

• ID форума: <code>{CHATS['chat_id']}</code>

<b>Настроенные темы:</b>
"""
    for key, name in chat_names.items():
        thread_id = CHATS[key]
        status = "✅" if thread_id != 0 else "❌"
        text += f"{status} <b>{name}</b>: <code>{thread_id or 'Не настроено'}</code>\n"
    
    await message.answer(text)

# ==================== КОМАНДА /DEADLINE ====================
@dp.message(Command("deadline"))
async def cmd_deadline(message: types.Message, state: FSMContext):
    """Создать дедлайн"""
    if CHATS['deadlines'] == 0:
        await message.answer("❌ Тема для дедлайнов не настроена. Используйте /setall")
        return
    
    await state.set_state(DeadlineForm.project)
    await message.answer("📅 <b>СОЗДАНИЕ ДЕДЛАЙНА</b>\n\nВыберите проект:", 
                        reply_markup=projects_keyboard("deadline"))

@dp.callback_query(lambda c: c.data.startswith('deadline_'), DeadlineForm.project)
async def deadline_project(callback: types.CallbackQuery, state: FSMContext):
    key = callback.data.replace('deadline_', '')
    if key in PROJECTS:
        await state.update_data(project=PROJECTS[key])
        await callback.answer()
        await state.set_state(DeadlineForm.date)
        await callback.message.answer("📅 Введите дату в формате <b>ДД.ММ</b> (например: 30.04):")

@dp.message(DeadlineForm.date)
async def deadline_date(message: types.Message, state: FSMContext):
    await state.update_data(date=message.text)
    await state.set_state(DeadlineForm.task)
    await message.answer("✍️ Введите описание задачи:")

@dp.message(DeadlineForm.task)
async def deadline_task(message: types.Message, state: FSMContext):
    await state.update_data(task=message.text)
    await state.set_state(DeadlineForm.priority)
    await message.answer("🎯 Выберите приоритет:", reply_markup=priorities_keyboard("deadline_prio"))

@dp.callback_query(lambda c: c.data.startswith('deadline_prio_'), DeadlineForm.priority)
async def deadline_priority(callback: types.CallbackQuery, state: FSMContext):
    key = callback.data.replace('deadline_prio_', '')
    if key in PRIORITIES:
        await state.update_data(priority=PRIORITIES[key])
        await callback.answer()
        await state.set_state(DeadlineForm.responsible)
        await callback.message.answer("👤 Укажите ответственного (@username или Имя_Фамилия):")

@dp.message(DeadlineForm.responsible)
async def deadline_responsible(message: types.Message, state: FSMContext):
    await state.update_data(responsible=message.text)
    await state.set_state(DeadlineForm.status)
    await message.answer("🔄 Выберите статус:", reply_markup=statuses_keyboard("deadline_stat"))

@dp.callback_query(lambda c: c.data.startswith('deadline_stat_'), DeadlineForm.status)
async def deadline_status(callback: types.CallbackQuery, state: FSMContext):
    key = callback.data.replace('deadline_stat_', '')
    if key in STATUSES:
        await state.update_data(status=STATUSES[key])
        await callback.answer()
        
        data = await state.get_data()
        
        # Формируем сообщение
        text = f"""
📅 <b>ДЕДЛАЙН:</b> {data['date']} - {data['task']}
{data['project']} {data['priority']} {data['status']}
👤 <b>Ответственный:</b> {data['responsible']}
📝 <b>Создано через бота</b>
"""
        
        # Отправляем в тему дедлайнов
        try:
            await bot.send_message(
                chat_id=CHATS['chat_id'],
                message_thread_id=CHATS['deadlines'],
                text=text
            )
            await callback.message.answer("✅ Дедлайн создан и отправлен в тему 'Дедлайны'!")
        except Exception as e:
            logger.error(f"Ошибка: {e}")
            await callback.message.answer("❌ Ошибка отправки. Проверьте настройки командой /check")
        
        await state.clear()

# ==================== КОМАНДА /QUESTION ====================
@dp.message(Command("question"))
async def cmd_question(message: types.Message, state: FSMContext):
    """Задать вопрос"""
    if CHATS['questions'] == 0:
        await message.answer("❌ Тема для вопросов не настроена. Используйте /setall")
        return
    
    await state.set_state(QuestionForm.project)
    await message.answer("❓ <b>ЗАДАТЬ ВОПРОС</b>\n\nВыберите проект:", 
                        reply_markup=projects_keyboard("question"))

@dp.callback_query(lambda c: c.data.startswith('question_'), QuestionForm.project)
async def question_project(callback: types.CallbackQuery, state: FSMContext):
    key = callback.data.replace('question_', '')
    if key in PROJECTS:
        await state.update_data(project=PROJECTS[key])
        await callback.answer()
        await state.set_state(QuestionForm.question)
        await callback.message.answer("❓ Введите ваш вопрос:")

@dp.message(QuestionForm.question)
async def question_text(message: types.Message, state: FSMContext):
    await state.update_data(question=message.text)
    await state.set_state(QuestionForm.priority)
    await message.answer("🎯 Выберите приоритет вопроса:", reply_markup=priorities_keyboard("question_prio"))

@dp.callback_query(lambda c: c.data.startswith('question_prio_'), QuestionForm.priority)
async def question_priority(callback: types.CallbackQuery, state: FSMContext):
    key = callback.data.replace('question_prio_', '')
    if key in PRIORITIES:
        await state.update_data(priority=PRIORITIES[key])
        await callback.answer()
        await state.set_state(QuestionForm.to_who)
        await callback.message.answer("👤 Кому адресован вопрос? (@username или Имя_Фамилия):")

@dp.message(QuestionForm.to_who)
async def question_to_who(message: types.Message, state: FSMContext):
    await state.update_data(to_who=message.text)
    await state.set_state(QuestionForm.context)
    await message.answer("📋 Дополнительный контекст (если нужно, или напишите 'нет'):")

@dp.message(QuestionForm.context)
async def question_context(message: types.Message, state: FSMContext):
    context = message.text if message.text.lower() != 'нет' else 'не указан'
    await state.update_data(context=context)
    data = await state.get_data()
    
    text = f"""
❓ <b>ВОПРОС:</b> {data['question']}
{data['project']} {data['priority']} #Жду
👤 <b>Кому:</b> {data['to_who']}
📝 <b>Контекст:</b> {data.get('context', 'не указан')}
🔔 <b>Создан через бота</b>
"""
    
    try:
        await bot.send_message(
            chat_id=CHATS['chat_id'],
            message_thread_id=CHATS['questions'],
            text=text
        )
        await message.answer("✅ Вопрос отправлен в тему 'Вопросы'!")
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        await message.answer("❌ Ошибка отправки.")
    
    await state.clear()

# ==================== КОМАНДА /DONE ====================
@dp.message(Command("done"))
async def cmd_done(message: types.Message, state: FSMContext):
    """Отметить задачу как выполненную"""
    if CHATS['done'] == 0:
        await message.answer("❌ Тема для готовых задач не настроена. Используйте /setall")
        return
    
    await state.set_state(DoneForm.project)
    await message.answer("✅ <b>ЗАДАЧА ВЫПОЛНЕНА</b>\n\nВыберите проект:", 
                        reply_markup=projects_keyboard("done"))

@dp.callback_query(lambda c: c.data.startswith('done_'), DoneForm.project)
async def done_project(callback: types.CallbackQuery, state: FSMContext):
    key = callback.data.replace('done_', '')
    if key in PROJECTS:
        await state.update_data(project=PROJECTS[key])
        await callback.answer()
        await state.set_state(DoneForm.task)
        await callback.message.answer("✅ Что именно сделано?")

@dp.message(DoneForm.task)
async def done_task(message: types.Message, state: FSMContext):
    await state.update_data(task=message.text)
    await state.set_state(DoneForm.status)
    
    # Клавиатура только для статусов Готово/Проверка
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="#Готово", callback_data="done_stat_done"),
            InlineKeyboardButton(text="#Проверка", callback_data="done_stat_review")
        ]
    ])
    
    await message.answer("🔄 Выберите статус:", reply_markup=keyboard)

@dp.callback_query(lambda c: c.data.startswith('done_stat_'), DoneForm.status)
async def done_status(callback: types.CallbackQuery, state: FSMContext):
    key = callback.data.replace('done_stat_', '')
    if key in ['done', 'review']:
        await state.update_data(status=STATUSES[key])
        await callback.answer()
        await state.set_state(DoneForm.link)
        await callback.message.answer("🔗 Ссылка на результат (если есть, или напишите 'нет'):")

@dp.message(DoneForm.link)
async def done_link(message: types.Message, state: FSMContext):
    link = message.text if message.text.lower() != 'нет' else 'не указана'
    await state.update_data(link=link)
    await state.set_state(DoneForm.check)
    await message.answer("🔍 Что конкретно проверять? (опишите кратко):")

@dp.message(DoneForm.check)
async def done_check(message: types.Message, state: FSMContext):
    await state.update_data(check=message.text)
    data = await state.get_data()
    
    text = f"""
✅ <b>ГОТОВО:</b> {data['task']}
{data['project']} {data['status']}
🔗 <b>Ссылка:</b> {data.get('link', 'не указана')}
🔍 <b>Проверить:</b> {data.get('check', 'не указано')}
🎯 <b>Отправлено через бота</b>
"""
    
    try:
        await bot.send_message(
            chat_id=CHATS['chat_id'],
            message_thread_id=CHATS['done'],
            text=text
        )
        await message.answer("✅ Задача отмечена как выполненная!")
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        await message.answer("❌ Ошибка отправки.")
    
    await state.clear()

# ==================== КОМАНДА /IDEA ====================
@dp.message(Command("idea"))
async def cmd_idea(message: types.Message, state: FSMContext):
    """Предложить идею"""
    if CHATS['ideas'] == 0:
        await message.answer("❌ Тема для идей не настроена. Используйте /setall")
        return
    
    await state.set_state(IdeaForm.project)
    await message.answer("💡 <b>ПРЕДЛОЖЕНИЕ ИДЕИ</b>\n\nВыберите проект:", 
                        reply_markup=projects_keyboard("idea"))

@dp.callback_query(lambda c: c.data.startswith('idea_'), IdeaForm.project)
async def idea_project(callback: types.CallbackQuery, state: FSMContext):
    key = callback.data.replace('idea_', '')
    if key in PROJECTS:
        await state.update_data(project=PROJECTS[key])
        await callback.answer()
        await state.set_state(IdeaForm.idea)
        await callback.message.answer("💡 Опишите вашу идею:")

@dp.message(IdeaForm.idea)
async def idea_text(message: types.Message, state: FSMContext):
    await state.update_data(idea=message.text)
    await state.set_state(IdeaForm.priority)
    await message.answer("🎯 Выберите приоритет:", reply_markup=priorities_keyboard("idea_prio"))

@dp.callback_query(lambda c: c.data.startswith('idea_prio_'), IdeaForm.priority)
async def idea_priority(callback: types.CallbackQuery, state: FSMContext):
    key = callback.data.replace('idea_prio_', '')
    if key in PRIORITIES:
        await state.update_data(priority=PRIORITIES[key])
        await callback.answer()
        await state.set_state(IdeaForm.benefit)
        await callback.message.answer("📈 Какая польза от этой идеи? (опишите кратко):")

@dp.message(IdeaForm.benefit)
async def idea_benefit(message: types.Message, state: FSMContext):
    await state.update_data(benefit=message.text)
    data = await state.get_data()
    
    text = f"""
💡 <b>ИДЕЯ:</b> {data['idea']}
{data['project']} {data['priority']}
📈 <b>Польза:</b> {data.get('benefit', 'не указана')}
🎯 <b>Предложено через бота</b>
"""
    
    try:
        await bot.send_message(
            chat_id=CHATS['chat_id'],
            message_thread_id=CHATS['ideas'],
            text=text
        )
        await message.answer("✅ Идея предложена в тему 'Идеи и предложения'!")
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        await message.answer("❌ Ошибка отправки.")
    
    await state.clear()

# ==================== КОМАНДА /RESOURCE ====================
@dp.message(Command("resource"))
async def cmd_resource(message: types.Message, state: FSMContext):
    """Добавить ресурс"""
    if CHATS['resources'] == 0:
        await message.answer("❌ Тема для ресурсов не настроена. Используйте /setall")
        return
    
    await state.set_state(ResourceForm.project)
    await message.answer("🗃 <b>ДОБАВЛЕНИЕ РЕСУРСА</b>\n\nВыберите проект:", 
                        reply_markup=projects_keyboard("resource"))

@dp.callback_query(lambda c: c.data.startswith('resource_'), ResourceForm.project)
async def resource_project(callback: types.CallbackQuery, state: FSMContext):
    key = callback.data.replace('resource_', '')
    if key in PROJECTS:
        await state.update_data(project=PROJECTS[key])
        await callback.answer()
        await state.set_state(ResourceForm.resource_type)
        await callback.message.answer("📎 Выберите тип ресурса:", reply_markup=resource_types_keyboard("res_type"))

@dp.callback_query(lambda c: c.data.startswith('res_type_'), ResourceForm.resource_type)
async def resource_type_handler(callback: types.CallbackQuery, state: FSMContext):
    key = callback.data.replace('res_type_', '')
    if key in RESOURCE_TYPES:
        await state.update_data(resource_type=RESOURCE_TYPES[key])
        await callback.answer()
        await state.set_state(ResourceForm.description)
        await callback.message.answer("📝 Опишите ресурс (что это, для чего):")

@dp.message(ResourceForm.description)
async def resource_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(ResourceForm.link)
    await message.answer("🔗 Ссылка на ресурс (если есть, или напишите 'нет'):")

@dp.message(ResourceForm.link)
async def resource_link(message: types.Message, state: FSMContext):
    link = message.text if message.text.lower() != 'нет' else 'не указана'
    await state.update_data(link=link)
    data = await state.get_data()
    
    text = f"""
🗃 <b>РЕСУРС:</b> {data['resource_type']}
{data['project']}
📝 <b>Описание:</b> {data.get('description', 'не указано')}
🔗 <b>Ссылка:</b> {data.get('link', 'не указана')}
🎯 <b>Добавлено через бота</b>
"""
    
    try:
        await bot.send_message(
            chat_id=CHATS['chat_id'],
            message_thread_id=CHATS['resources'],
            text=text
        )
        await message.answer("✅ Ресурс добавлен в тему 'Ресурсы и документы'!")
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        await message.answer("❌ Ошибка отправки.")
    
    await state.clear()

# ==================== КОМАНДА /REPORT ====================
@dp.message(Command("report"))
async def cmd_report(message: types.Message, state: FSMContext):
    """Создать отчет"""
    if CHATS['reports'] == 0:
        await message.answer("❌ Тема для отчетов не настроена. Используйте /setall")
        return
    
    await state.set_state(ReportForm.period)
    await message.answer("📊 <b>СОЗДАНИЕ ОТЧЕТА</b>\n\nВыберите период:", reply_markup=period_keyboard())

@dp.callback_query(lambda c: c.data.startswith('period_'), ReportForm.period)
async def report_period_handler(callback: types.CallbackQuery, state: FSMContext):
    period_type = callback.data.replace('period_', '')
    today = datetime.now().strftime("%d.%m.%Y")
    
    periods = {
        'day': f"За день {today}",
        'week': f"За неделю {today}",
        'month': f"За месяц {datetime.now().strftime('%m.%Y')}",
        'custom': "Другой период"
    }
    
    if period_type == 'custom':
        await callback.message.answer("📅 Введите период отчета (например: 'За неделю 24-30.04'):")
        await state.set_state(ReportForm.period)
    else:
        await state.update_data(period=periods[period_type])
        await callback.answer()
        await state.set_state(ReportForm.projects)
        await callback.message.answer("🎯 Над какими проектами работали? (перечислите через запятую):")

@dp.message(ReportForm.period)
async def report_period_custom(message: types.Message, state: FSMContext):
    await state.update_data(period=message.text)
    await state.set_state(ReportForm.projects)
    await message.answer("🎯 Над какими проектами работали? (перечислите через запятую):")

@dp.message(ReportForm.projects)
async def report_projects(message: types.Message, state: FSMContext):
    await state.update_data(projects=message.text)
    await state.set_state(ReportForm.completed)
    await message.answer("✅ Что сделано за этот период? (перечислите задачи):")

@dp.message(ReportForm.completed)
async def report_completed(message: types.Message, state: FSMContext):
    await state.update_data(completed=message.text)
    await state.set_state(ReportForm.problems)
    await message.answer("⚠️ Были ли проблемы или блокеры? (если нет, напишите 'нет'):")

@dp.message(ReportForm.problems)
async def report_problems(message: types.Message, state: FSMContext):
    problems = message.text if message.text.lower() != 'нет' else 'нет проблем'
    await state.update_data(problems=problems)
    await state.set_state(ReportForm.plans)
    await message.answer("📅 Планы на следующий период:")

@dp.message(ReportForm.plans)
async def report_plans(message: types.Message, state: FSMContext):
    await state.update_data(plans=message.text)
    data = await state.get_data()
    
    text = f"""
📊 <b>ОТЧЕТ:</b> {data['period']}

🎯 <b>Проекты:</b> {data.get('projects', 'не указано')}

✅ <b>Сделано:</b>
{data.get('completed', 'не указано')}

⚠️ <b>Проблемы:</b> {data.get('problems', 'нет проблем')}

📅 <b>Планы:</b> {data.get('plans', 'не указано')}

📝 <b>Отчет создан через бота</b>
"""
    
    try:
        await bot.send_message(
            chat_id=CHATS['chat_id'],
            message_thread_id=CHATS['reports'],
            text=text
        )
        await message.answer("✅ Отчет создан в теме 'Отчеты'!")
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        await message.answer("❌ Ошибка отправки.")
    
    await state.clear()

# ==================== ИНФОРМАЦИОННЫЕ КОМАНДЫ ====================
@dp.message(Command("projects"))
async def cmd_projects(message: types.Message):
    text = "📊 <b>ПРОЕКТЫ:</b>\n\n" + "\n".join([f"• {name}" for name in PROJECTS.values()])
    await message.answer(text)

@dp.message(Command("statuses"))
async def cmd_statuses(message: types.Message):
    text = "🔄 <b>СТАТУСЫ:</b>\n\n" + "\n".join([f"• {name}" for name in STATUSES.values()])
    await message.answer(text)

@dp.message(Command("priorities"))
async def cmd_priorities(message: types.Message):
    text = "🎯 <b>ПРИОРИТЕТЫ:</b>\n\n" + "\n".join([f"• {name}" for name in PRIORITIES.values()])
    await message.answer(text)

# ==================== ОБРАБОТКА НЕИЗВЕСТНЫХ КОМАНД ====================
@dp.message()
async def handle_unknown(message: types.Message):
    """Обработка неизвестных команд"""
    if message.text.startswith('/'):
        await message.answer(
            "❌ <b>Неизвестная команда</b>\n\n"
            "Используйте /help для просмотра доступных команд"
        )

# ==================== ЗАПУСК БОТА ====================
async def main():
    logger.info("🤖 Бот запускается...")
    logger.info(f"Админ ID: {ADMIN_ID}")
    
    # Проверяем настройки
    configured = sum(1 for key in ['deadlines', 'questions', 'done', 'ideas', 'resources', 'reports', 'main'] if CHATS[key] != 0)
    logger.info(f"Настроено тем: {configured}/7")
    
    if configured == 0:
        logger.info("⚠️ Темы не настроены. Используйте команду /setall")
    else:
        logger.info("✅ Темы настроены, бот готов к работе")
    
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())