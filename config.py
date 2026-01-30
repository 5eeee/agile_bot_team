import os
import json
from dotenv import load_dotenv

load_dotenv()

# ==================== БАЗОВЫЕ НАСТРОЙКИ ====================
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_ID', 0))

# Файл для хранения настроек чатов
CHATS_FILE = 'chats.json'

# ==================== ХЭШТЕГИ ПРОЕКТОВ ====================
PROJECTS = {
    'bm': '#Boost_Marine',
    'moto': '#Boost_Moto', 
    'print': '#Revolution_Print',
    'ai': '#Agile_Business_AI',
    'games': '#Pavel_Game',
    'denis': '#Denis_Crimea',
    'platform': '#Agile_Business_Platform'
}

# ==================== СТАТУСЫ ====================
STATUSES = {
    'doing': '#Делаю',
    'waiting': '#Жду', 
    'done': '#Готово',
    'review': '#Проверка',
    'blocked': '#Препятствие'
}

# ==================== ПРИОРИТЕТЫ ====================
PRIORITIES = {
    'critical': '#Критический',
    'high': '#Высокий',
    'medium': '#Средний', 
    'low': '#Низкий'
}

# ==================== ТИПЫ РЕСУРСОВ ====================
RESOURCE_TYPES = {
    'doc': '📄 Документ',
    'link': '🔗 Ссылка',
    'access': '🔑 Доступ',
    'file': '📎 Файл',
    'design': '🎨 Дизайн',
    'code': '💻 Код'
}

# ==================== ФУНКЦИИ ДЛЯ РАБОТЫ С ЧАТАМИ ====================
def load_chats():
    """Загружает настройки чатов из файла"""
    default_chats = {
        'chat_id': -1003761419747,  # ID вашего форума
        'deadlines': 4,    # Тема Дедлайны
        'questions': 8,    # Тема Вопросы
        'done': 10,        # Тема Готово / Демо
        'ideas': 15,       # Тема Идеи и предложения
        'resources': 6,    # Тема Ресурсы и документы
        'reports': 19,     # Тема Отчеты
        'main': 2          # Тема Главный чат
    }
    
    try:
        if os.path.exists(CHATS_FILE):
            with open(CHATS_FILE, 'r', encoding='utf-8') as f:
                saved = json.load(f)
                for key in default_chats:
                    if key in saved:
                        default_chats[key] = saved[key]
    except Exception as e:
        print(f"⚠️ Ошибка загрузки chats.json: {e}")
    
    return default_chats

def save_chats(chats_dict):
    """Сохраняет настройки чатов в файл"""
    try:
        with open(CHATS_FILE, 'w', encoding='utf-8') as f:
            json.dump(chats_dict, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"❌ Ошибка сохранения chats.json: {e}")
        return False

# Загружаем при старте
CHATS = load_chats()

# Проверка токена
if not BOT_TOKEN:
    print("❌ ОШИБКА: BOT_TOKEN не найден в .env файле!")
    exit(1)