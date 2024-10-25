import os
import json
import logging
from enum import Enum, auto
from langdetect import detect
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)
import aiohttp
from dotenv import load_dotenv
from typing import List

# Завантаження змінних оточення
load_dotenv()

# Налаштування логування
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Визначення станів за допомогою Enum для кращої організації
class States(Enum):
    MAIN_MENU = auto()
    CHARACTERS_MENU = auto()
    GUIDES_MENU = auto()
    TOURNAMENTS_MENU = auto()
    UPDATES_MENU = auto()
    BEGINNER_MENU = auto()
    NEWS_MENU = auto()
    HELP_MENU = auto()
    QUIZZES_MENU = auto()
    SEARCH_PERFORMING = auto()
    SEARCH_HERO_GUIDES = auto()

# Налаштування OpenAI API
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
API_URL = "https://api.openai.com/v1/chat/completions"

# Завантаження даних з файлів
def load_json_data(file_path: str):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            if not data:
                raise ValueError("JSON файл порожній.")
            return data
    except FileNotFoundError:
        logger.error(f"Файл {file_path} не знайдено.")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Некоректний JSON в файлі {file_path}: {e}")
        return {}
    except Exception as e:
        logger.error(f"Не вдалося завантажити файл {file_path}: {e}")
        return {}

prompts_data = load_json_data('prompts.json')
heroes_data = load_json_data('heroes_tanks.json')
prompts_list = prompts_data.get('prompts', [])

# Словник для зберігання вибраних героїв (може бути корисним для різних користувачів)
selected_heroes = {}

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.info("Користувач ініціював команду /start")
    buttons = [
        [KeyboardButton("🧙‍♂️ Персонажі"), KeyboardButton("📚 Гайди"), KeyboardButton("🏆 Турніри")],
        [KeyboardButton("🔄 Оновлення"), KeyboardButton("🆓 Початківець"), KeyboardButton("🔍 Пошук")],
        [KeyboardButton("📰 Новини"), KeyboardButton("💡 Допомога"), KeyboardButton("🎮 Вікторини")]
    ]
    reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=False)
    await update.message.reply_text("🔍 Оберіть опцію:", reply_markup=reply_markup)
    return States.MAIN_MENU

# Обробка вибору з головного меню
async def main_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_input = update.message.text
    logger.info(f"Вибір з головного меню: {user_input}")
    
    if user_input == "🧙‍♂️ Персонажі":
        buttons = [
            [KeyboardButton("📝 Деталі про героїв"), KeyboardButton("🧩 Вгадай героя")],
            [KeyboardButton("⚔️ Порівняння героїв"), KeyboardButton("🎯 Контргерої")],
            [KeyboardButton("🗂 Список героїв"), KeyboardButton("🔙 Назад")]
        ]
        reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=False)
        await update.message.reply_text("🧙‍♂️ Оберіть опцію:", reply_markup=reply_markup)
        return States.CHARACTERS_MENU
    elif user_input == "📚 Гайди":
        buttons = [
            [KeyboardButton("📝 Стратегії для кожного класу"), KeyboardButton("💡 Інтерактивні рекомендації")],
            [KeyboardButton("🎥 Відео-гайди"), KeyboardButton("🔙 Назад")]
        ]
        reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=False)
        await update.message.reply_text("📚 Оберіть опцію:", reply_markup=reply_markup)
        return States.GUIDES_MENU
    elif user_input == "🏆 Турніри":
        buttons = [
            [KeyboardButton("📅 Майбутні турніри"), KeyboardButton("📝 Участь у турнірі")],
            [KeyboardButton("📊 Огляд турнірів"), KeyboardButton("🔙 Назад")]
        ]
        reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=False)
        await update.message.reply_text("🏆 Оберіть опцію:", reply_markup=reply_markup)
        return States.TOURNAMENTS_MENU
    elif user_input == "🔄 Оновлення":
        buttons = [
            [KeyboardButton("📝 Останні оновлення гри"), KeyboardButton("🔔 Сповіщення про оновлення")],
            [KeyboardButton("🎤 Інтерв'ю з розробниками"), KeyboardButton("🔙 Назад")]
        ]
        reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=False)
        await update.message.reply_text("🔄 Оберіть опцію:", reply_markup=reply_markup)
        return States.UPDATES_MENU
    elif user_input == "🆓 Початківець":
        buttons = [
            [KeyboardButton("📘 Гайди для новачків"), KeyboardButton("🎯 Інтерактивні навчальні завдання")],
            [KeyboardButton("📈 Поради для прогресу"), KeyboardButton("🔙 Назад")]
        ]
        reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=False)
        await update.message.reply_text("🆓 Оберіть опцію:", reply_markup=reply_markup)
        return States.BEGINNER_MENU
    elif user_input == "🔍 Пошук":
        buttons = [
            [KeyboardButton("🔍 Пошук героїв та гайдів"), KeyboardButton("🎙️ Голосовий пошук")],
            [KeyboardButton("📝 Історія пошуку"), KeyboardButton("🔙 Назад")]
        ]
        reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=False)
        await update.message.reply_text("🔍 Оберіть опцію:", reply_markup=reply_markup)
        return States.NEWS_MENU  # Можливо, варто створити окремий стан для пошуку
    elif user_input == "📰 Новини":
        buttons = [
            [KeyboardButton("📝 Останні новини гри"), KeyboardButton("📊 Аналіз патчів")],
            [KeyboardButton("🎉 Події спільноти"), KeyboardButton("🔙 Назад")]
        ]
        reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=False)
        await update.message.reply_text("📰 Оберіть опцію:", reply_markup=reply_markup)
        return States.NEWS_MENU
    elif user_input == "💡 Допомога":
        buttons = [
            [KeyboardButton("❓ FAQ"), KeyboardButton("💬 Живий чат підтримки")],
            [KeyboardButton("🐞 Повідомлення про помилки"), KeyboardButton("🔙 Назад")]
        ]
        reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=False)
        await update.message.reply_text("💡 Оберіть опцію:", reply_markup=reply_markup)
        return States.HELP_MENU
    elif user_input == "🎮 Вікторини":
        buttons = [
            [KeyboardButton("🧠 Вгадай цитату"), KeyboardButton("💥 Вгадай здібність")],
            [KeyboardButton("📚 Тест на знання"), KeyboardButton("🔙 Назад")]
        ]
        reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=False)
        await update.message.reply_text("🎮 Оберіть опцію:", reply_markup=reply_markup)
        return States.QUIZZES_MENU
    else:
        await update.message.reply_text("⚠️ Не вдалося обробити ваш запит.")
        return ConversationHandler.END

# Функція для виконання запиту до OpenAI API
async def handle_gpt_query(update: Update, context: ContextTypes.DEFAULT_TYPE, user_input: str) -> None:
    try:
        data = {
            "model": "gpt-4",
            "messages": [{"role": "user", "content": user_input}],
            "max_tokens": 1200
        }
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        # Логування запиту
        logger.info(f"Відправляємо запит до OpenAI API з повідомленням: {user_input}")
        async with aiohttp.ClientSession() as session:
            async with session.post(API_URL, headers=headers, json=data) as response:
                if response.status == 200:
                    response_data = await response.json()
                    reply_text = response_data['choices'][0]['message']['content']
                    # Логування відповіді
                    logger.info(f"Отримана відповідь від OpenAI API: {reply_text}")
                    # Відправляємо відповідь з Markdown форматуванням
                    await update.message.reply_text(f"{reply_text}", parse_mode='Markdown')
                else:
                    error_text = await response.text()
                    logger.error(f"API Error: {response.status} - {error_text}")
                    await update.message.reply_text("⚠️ Сталася помилка при зверненні до API. Спробуйте ще раз.")
    except Exception as e:
        logger.error(f"Невідома помилка: {e}")
        await update.message.reply_text("⚠️ Вибачте, сталася невідома помилка. Спробуйте знову.")

# Функції для обробки підменю Персонажів
async def handle_characters_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_input = update.message.text
    logger.info(f"Вибір в Персонажах: {user_input}")
    
    if user_input == "📝 Деталі про героїв":
        await send_character_details(update, context)
        return States.CHARACTERS_MENU
    elif user_input == "🧩 Вгадай героя":
        await start_quiz_quote(update, context)
        return States.CHARACTERS_MENU
    elif user_input == "⚔️ Порівняння героїв":
        await send_character_comparison(update, context)
        return States.CHARACTERS_MENU
    elif user_input == "🎯 Контргерої":
        await send_counter_strategies(update, context)
        return States.CHARACTERS_MENU
    elif user_input == "🗂 Список героїв":
        await select_hero_class(update, context)
        return States.CHARACTERS_MENU
    elif user_input == "🔙 Назад":
        await start(update, context)
        return States.MAIN_MENU
    else:
        await update.message.reply_text("⚠️ Не вдалося обробити ваш запит.")
        return States.CHARACTERS_MENU

# Функція для відправки деталей про героїв
async def send_character_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Приклад: Ви можете додати більше деталей або форматувати їх краще
    character_details = "📖 **Деталі про героя:**\n\n" \
                        "<b>Ім'я:</b> Джонсон\n" \
                        "<b>Клас:</b> Танки\n" \
                        "<b>Основні навички:</b> Навичка 1, Навичка 2, Навичка 3\n\n" \
                        "🔗 Детальніше: https://example.com/johnson-details"  # Замініть на фактичне посилання
    await update.message.reply_text(character_details, parse_mode='HTML', disable_web_page_preview=True)
    # Повернення до меню персонажів не потрібно, стан вже встановлений

# Функція для відправки порівняння героїв
async def send_character_comparison(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    comparison = "⚔️ **Порівняння героїв:**\n\n" \
                 "<b>Джонсон:</b> HP: 2000, Атака: 150, Захист: 300\n" \
                 "<b>Фрідом:</b> HP: 1800, Атака: 170, Захист: 250\n\n" \
                 "🔗 Детальніше: https://example.com/comparison"
    await update.message.reply_text(comparison, parse_mode='HTML', disable_web_page_preview=True)
    # Повернення до меню персонажів не потрібно, стан вже встановлений

# Функція для відправки стратегій контргероїв
async def send_counter_strategies(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    strategies = "🎯 **Контргерої:**\n\n" \
                 "• Для контратаки Джонсон використовуйте Муну.\n" \
                 "• Для Фрідома найкраще підійдуть Анні.\n\n" \
                 "🔗 Детальніше: https://example.com/counter-strategies"
    await update.message.reply_text(strategies, parse_mode='HTML', disable_web_page_preview=True)
    # Повернення до меню персонажів не потрібно, стан вже встановлений

# Функція для вибору класу героя перед вибором конкретного героя
async def select_hero_class(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    classes = ["Танк", "Борець", "Маг", "Стрілець", "Асасин", "Підтримка"]
    buttons = []
    for i in range(0, len(classes), 3):
        row = classes[i:i + 3]
        buttons.append([KeyboardButton(cls) for cls in row])
    buttons.append([KeyboardButton("🔙 Назад")])
    reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=False)
    await update.message.reply_text("🗂 **Оберіть клас героя:**", parse_mode='Markdown', reply_markup=reply_markup)
    return States.CHARACTERS_MENU

# Функція для обробки вибору класу героя
async def handle_characters_class_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    selected_class = update.message.text.strip()
    classes = ["Танк", "Борець", "Маг", "Стрілець", "Асасин", "Підтримка"]
    if selected_class in classes:
        heroes = get_characters_by_class(selected_class)
        if heroes:
            buttons = []
            for i in range(0, len(heroes), 4):
                row = heroes[i:i + 4]
                buttons.append([KeyboardButton(hero) for hero in row])
            buttons.append([KeyboardButton("🔙 Назад")])
            reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=False)
            await update.message.reply_text(f"🗂 **Список героїв класу {selected_class}:**", parse_mode='Markdown', reply_markup=reply_markup)
            return States.CHARACTERS_MENU
        else:
            await update.message.reply_text(f"⚠️ Немає героїв у класі {selected_class}.")
            await select_hero_class(update, context)
            return States.CHARACTERS_MENU
    elif selected_class == "🔙 Назад":
        await handle_characters_sub_selection(update, context, "🗂 Список героїв")
        return States.CHARACTERS_MENU
    else:
        await update.message.reply_text("⚠️ Вибрана опція не відповідає жодному класу.")
        await select_hero_class(update, context)
        return States.CHARACTERS_MENU

# Функція для отримання списку героїв за класом
def get_characters_by_class(hero_class: str) -> List[str]:
    return [
        hero["name"] for hero in heroes_data.get('heroes', [])
        if hero_class.lower() in hero.get("role", "").lower()
    ]

# Функція для відправки повного списку героїв (без фільтрації по класу)
async def handle_characters_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    selected_hero = update.message.text.strip()
    if selected_hero in [hero["name"] for hero in heroes_data.get('heroes', [])]:
        hero_info = get_hero_info(selected_hero)
        if hero_info:
            hero_details = (
                f"📖 **Деталі про героя {selected_hero}:**\n\n"
                f"<b>Клас:</b> {hero_info.get('class', 'Невідомо')}\n"
                f"<b>Роль:</b> {hero_info.get('role', 'Невідомо')}\n"
                f"<b>HP:</b> {hero_info.get('hp', 'Невідомо')}\n"
                f"<b>Атака:</b> {hero_info.get('attack', 'Невідомо')}\n"
                f"<b>Захист:</b> {hero_info.get('defense', 'Невідомо')}\n\n"
                f"🔗 Детальніше: {hero_info.get('details_link', 'Немає посилання')}"
            )
            await update.message.reply_text(hero_details, parse_mode='HTML', disable_web_page_preview=True)
            # Повернення до вибору класу героїв
            await select_hero_class(update, context)
            return States.CHARACTERS_MENU
        else:
            await update.message.reply_text("⚠️ Не вдалося знайти інформацію про цього героя.")
            return States.CHARACTERS_MENU
    elif selected_hero == "🔙 Назад":
        await select_hero_class(update, context)
        return States.CHARACTERS_MENU
    else:
        await update.message.reply_text("⚠️ Вибрана опція не відповідає жодному герою.")
        await select_hero_class(update, context)
        return States.CHARACTERS_MENU

# Функції для обробки підменю Гайдів
async def handle_guides_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_input = update.message.text
    logger.info(f"Вибір в Гайдах: {user_input}")
    
    if user_input == "📝 Стратегії для кожного класу":
        await send_class_strategies(update, context)
        return States.GUIDES_MENU
    elif user_input == "💡 Інтерактивні рекомендації":
        await send_interactive_recommendations(update, context)
        return States.GUIDES_MENU
    elif user_input == "🎥 Відео-гайди":
        await send_video_guides(update, context)
        return States.GUIDES_MENU
    elif user_input == "🔙 Назад":
        await start(update, context)
        return States.MAIN_MENU
    else:
        await update.message.reply_text("⚠️ Не вдалося обробити ваш запит.")
        return States.GUIDES_MENU

# Функція для відправки стратегій для кожного класу
async def send_class_strategies(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    strategies = "📝 **Стратегії для кожного класу:**\n\n" \
                "<b>Танки:</b> Фокусуйтеся на захисті та ініціюванні боїв.\n" \
                "<b>Бійці:</b> Атакуйте ворогів та утримуйте позиції.\n" \
                "<b>Маги:</b> Використовуйте високий урон та контроль.\n" \
                "<b>Стрілеці:</b> Забезпечуйте постійну підтримку з дистанції.\n" \
                "<b>Асасини:</b> Завдавайте швидкий урон та зникайте.\n" \
                "<b>Підтримка:</b> Допомагайте союзникам та контролюйте поле бою.\n\n" \
                "🔗 Детальніше: https://example.com/class-strategies"
    await update.message.reply_text(strategies, parse_mode='HTML', disable_web_page_preview=True)
    # Повернення до меню гайдів не потрібно, стан вже встановлений

# Функція для відправки інтерактивних рекомендацій
async def send_interactive_recommendations(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    classes = ["Танк", "Борець", "Маг", "Стрілець", "Асасин", "Підтримка"]
    buttons = []
    for i in range(0, len(classes), 3):
        row = classes[i:i + 3]
        buttons.append([KeyboardButton(cls) for cls in row])
    buttons.append([KeyboardButton("🔙 Назад")])
    reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=False)
    await update.message.reply_text("💡 **Оберіть клас, щоб отримати рекомендації гайдів:**", parse_mode='Markdown', reply_markup=reply_markup)
    return States.GUIDES_MENU

# Обробка вибору класу для інтерактивних рекомендацій
async def handle_interactive_recommendations(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    selected_class = update.message.text.strip()
    classes = ["Танк", "Борець", "Маг", "Стрілець", "Асасин", "Підтримка"]
    if selected_class in classes:
        recommendations = f"💡 **Рекомендації гайдів для класу {selected_class}:**\n\n" \
                           f"• [Гайд для {selected_class} 1](https://example.com/guide-{selected_class.lower()}-1)\n" \
                           f"• [Гайд для {selected_class} 2](https://example.com/guide-{selected_class.lower()}-2)\n\n" \
                           f"🔗 Детальніше: https://example.com/recommendations-{selected_class.lower()}"
        await update.message.reply_text(recommendations, parse_mode='Markdown', disable_web_page_preview=True)
        # Повернення до інтерактивних рекомендацій
        buttons = []
        for i in range(0, len(classes), 3):
            row = classes[i:i + 3]
            buttons.append([KeyboardButton(cls) for cls in row])
        buttons.append([KeyboardButton("🔙 Назад")])
        reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=False)
        await update.message.reply_text("💡 **Оберіть клас, щоб отримати рекомендації гайдів:**", parse_mode='Markdown', reply_markup=reply_markup)
        return States.GUIDES_MENU
    elif selected_class == "🔙 Назад":
        buttons = [
            [KeyboardButton("📝 Стратегії для кожного класу"), KeyboardButton("💡 Інтерактивні рекомендації")],
            [KeyboardButton("🎥 Відео-гайди"), KeyboardButton("🔙 Назад")]
        ]
        reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=False)
        await update.message.reply_text("📚 Оберіть опцію:", reply_markup=reply_markup)
        return States.GUIDES_MENU
    else:
        await update.message.reply_text("⚠️ Вибрана опція не відповідає жодному класу.")
        return States.GUIDES_MENU

# Функція для відправки відео-гайдів
async def send_video_guides(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    video_guides = "🎥 **Відео-гайди:**\n\n" \
                  "• [Гайд для новачків](https://youtube.com/guide1)\n" \
                  "• [Стратегії гри](https://youtube.com/guide2)\n" \
                  "• [Поради від професіоналів](https://youtube.com/guide3)\n\n" \
                  "🔗 Детальніше: https://example.com/video-guides"
    await update.message.reply_text(video_guides, parse_mode='Markdown', disable_web_page_preview=True)
    # Повернення до меню гайдів не потрібно, стан вже встановлений

# Функції для обробки підменю Турнірів
async def handle_tournaments_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_input = update.message.text
    logger.info(f"Вибір в Турнірах: {user_input}")
    
    if user_input == "📅 Майбутні турніри":
        await send_upcoming_tournaments(update, context)
        return States.TOURNAMENTS_MENU
    elif user_input == "📝 Участь у турнірі":
        await send_tournament_participation(update, context)
        return States.TOURNAMENTS_MENU
    elif user_input == "📊 Огляд турнірів":
        await send_tournaments_overview(update, context)
        return States.TOURNAMENTS_MENU
    elif user_input == "🔙 Назад":
        await start(update, context)
        return States.MAIN_MENU
    else:
        await update.message.reply_text("⚠️ Не вдалося обробити ваш запит.")
        return States.TOURNAMENTS_MENU

# Функція для відправки інформації про майбутні турніри
async def send_upcoming_tournaments(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    upcoming = "📅 **Майбутні турніри:**\n\n" \
               "• **Турнір Spring Clash**\n" \
               "  🗓 Дата: 25 квітня 2024\n" \
               "  🏆 Призи: $5000\n" \
               "  🔗 Реєстрація: https://example.com/spring-clash\n\n" \
               "• **Літній Кубок**\n" \
               "  🗓 Дата: 15 липня 2024\n" \
               "  🏆 Призи: $7000\n" \
               "  🔗 Реєстрація: https://example.com/summer-cup"
    await update.message.reply_text(upcoming, parse_mode='Markdown', disable_web_page_preview=True)
    # Повернення до меню турнірів не потрібно, стан вже встановлений

# Функція для відправки інформації про участь у турнірі
async def send_tournament_participation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    participation = "📝 **Участь у турнірі:**\n\n" \
                    "Щоб взяти участь у турнірі, виконайте наступні кроки:\n" \
                    "1. Перейдіть за посиланням реєстрації.\n" \
                    "2. Заповніть необхідні дані.\n" \
                    "3. Дочекайтесь підтвердження вашої участі.\n\n" \
                    "🔗 Реєстрація: https://example.com/participate-tournament"
    await update.message.reply_text(participation, parse_mode='Markdown', disable_web_page_preview=True)
    # Повернення до меню турнірів не потрібно, стан вже встановлений

# Функція для відправки огляду турнірів
async def send_tournaments_overview(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    overview = "📊 **Огляд турнірів:**\n\n" \
               "• **Spring Clash:** Відбувся 20 березня 2024. Переможці отримали $5000.\n" \
               "• **Winter Showdown:** Відбувся 10 січня 2024. Переможці отримали $3000.\n\n" \
               "🔗 Детальніше: https://example.com/tournaments-overview"
    await update.message.reply_text(overview, parse_mode='Markdown', disable_web_page_preview=True)
    # Повернення до меню турнірів не потрібно, стан вже встановлений

# Функції для обробки підменю Оновлень
async def handle_updates_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_input = update.message.text
    logger.info(f"Вибір в Оновленнях: {user_input}")
    
    if user_input == "📝 Останні оновлення гри":
        await send_latest_updates(update, context)
        return States.UPDATES_MENU
    elif user_input == "🔔 Сповіщення про оновлення":
        await send_update_notifications(update, context)
        return States.UPDATES_MENU
    elif user_input == "🎤 Інтерв'ю з розробниками":
        await send_developer_interviews(update, context)
        return States.UPDATES_MENU
    elif user_input == "🔙 Назад":
        await start(update, context)
        return States.MAIN_MENU
    else:
        await update.message.reply_text("⚠️ Не вдалося обробити ваш запит.")
        return States.UPDATES_MENU

# Функція для відправки останніх оновлень гри
async def send_latest_updates(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    latest = "📝 **Останні оновлення гри:**\n\n" \
             "• **Версія 1.2.3:** Додано нового героя - Артеміус.\n" \
             "• **Баланс:** Змінено характеристики деяких героїв для покращення балансу гри.\n" \
             "• **Нові карти:** Введено карту 'Замок Вогню'.\n\n" \
             "🔗 Детальніше: https://example.com/latest-updates"
    await update.message.reply_text(latest, parse_mode='HTML', disable_web_page_preview=True)
    # Повернення до меню оновлень не потрібно, стан вже встановлений

# Функція для відправки сповіщень про оновлення
async def send_update_notifications(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    notifications = "🔔 **Сповіщення про оновлення:**\n\n" \
                    "Підпишіться, щоб отримувати сповіщення про найновіші оновлення гри та спеціальні події.\n\n" \
                    "🔗 Підписка: https://example.com/subscribe-updates"
    await update.message.reply_text(notifications, parse_mode='Markdown', disable_web_page_preview=True)
    # Повернення до меню оновлень не потрібно, стан вже встановлений

# Функція для відправки інтерв'ю з розробниками
async def send_developer_interviews(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    interviews = "🎤 **Інтерв'ю з розробниками:**\n\n" \
                 "• **Інтерв'ю з головним розробником:** Дізнайтесь про майбутні плани та оновлення.\n" \
                 "• **Інтерв'ю з дизайнером:** Обговорення нових механік та дизайну карт.\n\n" \
                 "🔗 Детальніше: https://example.com/developer-interviews"
    await update.message.reply_text(interviews, parse_mode='Markdown', disable_web_page_preview=True)
    # Повернення до меню оновлень не потрібно, стан вже встановлений

# Функції для обробки підменю Допомоги
async def handle_help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_input = update.message.text
    logger.info(f"Вибір в Допомозі: {user_input}")
    
    if user_input == "❓ FAQ":
        await send_faq(update, context)
        return States.HELP_MENU
    elif user_input == "💬 Живий чат підтримки":
        await send_live_support(update, context)
        return States.HELP_MENU
    elif user_input == "🐞 Повідомлення про помилки":
        await send_bug_report(update, context)
        return States.HELP_MENU
    elif user_input == "🔙 Назад":
        await start(update, context)
        return States.MAIN_MENU
    else:
        await update.message.reply_text("⚠️ Не вдалося обробити ваш запит.")
        return States.HELP_MENU

# Функція для відправки FAQ
async def send_faq(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    faq = "❓ **FAQ:**\n\n" \
          "• **Як зареєструватися?** Перейдіть за посиланням реєстрації.\n" \
          "• **Як обрати героя?** Вивчіть характеристики героїв у розділі Персонажі.\n" \
          "• **Що робити при багах?** Використовуйте форму повідомлення про помилки.\n\n" \
          "🔗 Детальніше: https://example.com/faq"
    await update.message.reply_text(faq, parse_mode='HTML', disable_web_page_preview=True)
    # Повернення до меню допомоги не потрібно, стан вже встановлений

# Функція для відправки посилання на живий чат підтримки
async def send_live_support(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    live_support = "💬 **Живий чат підтримки:**\n\n" \
                   "Якщо у вас виникли проблеми або запитання, зверніться до нашої підтримки:\n\n" \
                   "🔗 [Підтримка](https://t.me/your_support_chat)"
    await update.message.reply_text(live_support, parse_mode='HTML', disable_web_page_preview=True)
    # Повернення до меню допомоги не потрібно, стан вже встановлений

# Функція для відправки форми повідомлення про помилки
async def send_bug_report(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    bug_report = "🐞 **Повідомлення про помилки:**\n\n" \
                 "Якщо ви знайшли баг або маєте пропозиції, будь ласка, заповніть наступну форму:\n\n" \
                 "🔗 [Повідомити про помилку](https://example.com/report-bug)"
    await update.message.reply_text(bug_report, parse_mode='HTML', disable_web_page_preview=True)
    # Повернення до меню допомоги не потрібно, стан вже встановлений

# Функції для обробки підменю Новин
async def handle_news_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_input = update.message.text
    logger.info(f"Вибір в Новинах: {user_input}")
    
    if user_input == "📝 Останні новини гри":
        await send_latest_game_news(update, context)
        return States.NEWS_MENU
    elif user_input == "📊 Аналіз патчів":
        await send_patch_analysis(update, context)
        return States.NEWS_MENU
    elif user_input == "🎉 Події спільноти":
        await send_community_events(update, context)
        return States.NEWS_MENU
    elif user_input == "🔙 Назад":
        await start(update, context)
        return States.MAIN_MENU
    else:
        # Перевірка, чи користувач не натиснув кнопку пошуку
        if user_input in ["🔍 Пошук героїв та гайдів", "🎙️ Голосовий пошук", "📝 Історія пошуку"]:
            return await handle_search_menu(update, context)
        else:
            await update.message.reply_text("⚠️ Не вдалося обробити ваш запит.")
            return States.NEWS_MENU

# Функція для відправки останніх новин гри
async def send_latest_game_news(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    news = "📝 **Останні новини гри:**\n\n" \
           "• **Новий герой Артеміус** був доданий до гри.\n" \
           "• Запроваджено нову карту 'Замок Вогню'.\n" \
           "• Виправлено кілька багів та покращено баланс.\n\n" \
           "🔗 Детальніше: https://example.com/latest-news"
    await update.message.reply_text(news, parse_mode='HTML', disable_web_page_preview=True)
    # Повернення до меню новин не потрібно, стан вже встановлений

# Функція для відправки аналізу патчів
async def send_patch_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    analysis = "📊 **Аналіз патчів:**\n\n" \
               "• **Патч 1.2.3:** Зміни у балансі героїв.\n" \
               "• **Патч 1.2.4:** Оптимізація механік гри.\n\n" \
               "🔗 Детальніше: https://example.com/patch-analysis"
    await update.message.reply_text(analysis, parse_mode='HTML', disable_web_page_preview=True)
    # Повернення до меню патчів не потрібно, стан вже встановлений

# Функція для відправки подій спільноти
async def send_community_events(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    events = "🎉 **Події спільноти:**\n\n" \
             "• **Спільний матч**: Збирайтесь з друзями та беріть участь у спільних матчах.\n" \
             "• **Фан-арт конкурс**: Створюйте та діляйтесь своїм фан-артом для шансів виграти призи.\n\n" \
             "🔗 Детальніше: https://example.com/community-events"
    await update.message.reply_text(events, parse_mode='HTML', disable_web_page_preview=True)
    # Повернення до меню подій спільноти не потрібно, стан вже встановлений

# Функції для обробки підменю Початківця
async def handle_beginner_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_input = update.message.text
    logger.info(f"Вибір в Початківці: {user_input}")
    
    if user_input == "📘 Гайди для новачків":
        await send_beginner_guides(update, context)
        return States.BEGINNER_MENU
    elif user_input == "🎯 Інтерактивні навчальні завдання":
        await send_interactive_tasks(update, context)
        return States.BEGINNER_MENU
    elif user_input == "📈 Поради для прогресу":
        await send_progress_tips(update, context)
        return States.BEGINNER_MENU
    elif user_input == "🔙 Назад":
        await start(update, context)
        return States.MAIN_MENU
    else:
        await update.message.reply_text("⚠️ Не вдалося обробити ваш запит.")
        return States.BEGINNER_MENU

# Функції для відправки гайдів для новачків
async def send_beginner_guides(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    guides = "📘 **Гайди для новачків:**\n\n" \
             "• [Повний гайд для новачків](https://example.com/beginner-guide)\n" \
             "• [Основи гри та механіки](https://example.com/basics-guide)\n\n" \
             "🔗 Детальніше: https://example.com/beginner-guides"
    await update.message.reply_text(guides, parse_mode='Markdown', disable_web_page_preview=True)
    # Повернення до меню початківця не потрібно, стан вже встановлений

# Функція для відправки інтерактивних навчальних завдань
async def send_interactive_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    tasks = "🎯 **Інтерактивні навчальні завдання:**\n\n" \
            "Виконайте наступні завдання, щоб покращити свої навички:\n" \
            "1. **Завдання 1:** Оптимізуйте свій баланс.\n" \
            "2. **Завдання 2:** Підвищте ефективність своєї стратегії.\n\n" \
            "🔗 Детальніше: https://example.com/interactive-tasks"
    await update.message.reply_text(tasks, parse_mode='Markdown', disable_web_page_preview=True)
    # Повернення до меню початківця не потрібно, стан вже встановлений

# Функція для відправки порад для прогресу
async def send_progress_tips(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    tips = "📈 **Поради для прогресу:**\n\n" \
           "• Практикуйтеся регулярно.\n" \
           "• Аналізуйте свої матчі.\n" \
           "• Вивчайте стратегії професіоналів.\n\n" \
           "🔗 Детальніше: https://example.com/progress-tips"
    await update.message.reply_text(tips, parse_mode='Markdown', disable_web_page_preview=True)
    # Повернення до меню початківця не потрібно, стан вже встановлений

# Функції для обробки підменю Вікторин
async def handle_quizzes_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_input = update.message.text
    logger.info(f"Вибір в Вікторинах: {user_input}")
    
    if user_input == "🧠 Вгадай цитату":
        await start_quiz_quote(update, context)
        return States.QUIZZES_MENU
    elif user_input == "💥 Вгадай здібність":
        await start_quiz_ability(update, context)
        return States.QUIZZES_MENU
    elif user_input == "📚 Тест на знання":
        await start_quiz_test(update, context)
        return States.QUIZZES_MENU
    elif user_input == "🔙 Назад":
        await start(update, context)
        return States.MAIN_MENU
    else:
        await update.message.reply_text("⚠️ Не вдалося обробити ваш запит.")
        return States.QUIZZES_MENU

# Функція для відправки вікторини "Вгадай цитату"
async def start_quiz_quote(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    question = "🧠 **Вгадай героя за цією цитатою:**\n\n" \
               "\"Я завжди на боці переможців.\""
    options = ["Джонсон", "Фрідом", "Лукас", "Аліса"]
    buttons = [[KeyboardButton(option) for option in options], [KeyboardButton("🔙 Назад")]]
    reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=False)
    await update.message.reply_text(question, parse_mode='Markdown', reply_markup=reply_markup)
    return States.QUIZZES_MENU

# Функція для обробки відповідей вікторини "Вгадай цитату"
async def handle_quizzes_quote(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_answer = update.message.text
    correct_answer = "Джонсон"
    if user_answer == correct_answer:
        await update.message.reply_text("🎉 Вірно! Це Джонсон.")
    else:
        await update.message.reply_text(f"❌ Невірно. Правильна відповідь: {correct_answer}")
    # Повернення до меню Вікторин
    buttons = [
        [KeyboardButton("🧠 Вгадай цитату"), KeyboardButton("💥 Вгадай здібність")],
        [KeyboardButton("📚 Тест на знання"), KeyboardButton("🔙 Назад")]
    ]
    reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=False)
    await update.message.reply_text("🎮 Оберіть опцію:", parse_mode='Markdown', reply_markup=reply_markup)
    return States.QUIZZES_MENU

# Функція для старту вікторини "Вгадай здібність"
async def start_quiz_ability(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    question = "💥 **Вгадай здібність героя:**\n\n" \
               "Яка здібність дозволяє герою створювати бар'єри для захисту?"
    options = ["Бар'єр", "Замок", "Блокування", "Щит"]
    buttons = [[KeyboardButton(option) for option in options], [KeyboardButton("🔙 Назад")]]
    reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=False)
    await update.message.reply_text(question, parse_mode='Markdown', reply_markup=reply_markup)
    return States.QUIZZES_MENU

# Функція для обробки відповідей вікторини "Вгадай здібність"
async def handle_quizzes_ability(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_answer = update.message.text
    correct_answer = "Щит"
    if user_answer == correct_answer:
        await update.message.reply_text("🎉 Вірно! Це Щит.")
    else:
        await update.message.reply_text(f"❌ Невірно. Правильна відповідь: {correct_answer}")
    # Повернення до меню Вікторин
    buttons = [
        [KeyboardButton("🧠 Вгадай цитату"), KeyboardButton("💥 Вгадай здібність")],
        [KeyboardButton("📚 Тест на знання"), KeyboardButton("🔙 Назад")]
    ]
    reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=False)
    await update.message.reply_text("🎮 Оберіть опцію:", parse_mode='Markdown', reply_markup=reply_markup)
    return States.QUIZZES_MENU

# Функція для старту тесту на знання
async def start_quiz_test(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    question = "📚 **Тест на знання:**\n\n" \
               "Який герой має здібність 'Прокляття Нескінченності'?"
    options = ["Герой 1", "Герой 2", "Герой 3", "Герой 4"]
    buttons = [[KeyboardButton(option) for option in options], [KeyboardButton("🔙 Назад")]]
    reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=False)
    await update.message.reply_text(question, parse_mode='Markdown', reply_markup=reply_markup)
    return States.QUIZZES_MENU

# Функція для обробки відповідей тесту на знання
async def handle_quizzes_test(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_answer = update.message.text
    correct_answer = "Герой 3"
    if user_answer == correct_answer:
        await update.message.reply_text("🎉 Вірно! Це Герой 3.")
    else:
        await update.message.reply_text(f"❌ Невірно. Правильна відповідь: {correct_answer}")
    # Повернення до меню Вікторин
    buttons = [
        [KeyboardButton("🧠 Вгадай цитату"), KeyboardButton("💥 Вгадай здібність")],
        [KeyboardButton("📚 Тест на знання"), KeyboardButton("🔙 Назад")]
    ]
    reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=False)
    await update.message.reply_text("🎮 Оберіть опцію:", parse_mode='Markdown', reply_markup=reply_markup)
    return States.QUIZZES_MENU

# Функції для обробки пошуку
async def handle_search_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_input = update.message.text
    logger.info(f"Вибір в Пошуку: {user_input}")
    
    if user_input == "🔍 Пошук героїв та гайдів":
        return await perform_search(update, context)
    elif user_input == "🎙️ Голосовий пошук":
        await perform_voice_search(update, context)
        return States.NEWS_MENU
    elif user_input == "📝 Історія пошуку":
        await show_search_history(update, context)
        return States.NEWS_MENU
    elif user_input == "🔙 Назад":
        await start(update, context)
        return States.MAIN_MENU
    else:
        await update.message.reply_text("⚠️ Не вдалося обробити ваш запит.")
        return States.NEWS_MENU

# Функція для виконання пошуку
async def perform_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("🔍 Введіть ваш запит для пошуку:")
    context.user_data['state'] = States.SEARCH_PERFORMING
    return States.SEARCH_PERFORMING

# Функція для виконання голосового пошуку
async def perform_voice_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("🎙️ Голосовий пошук наразі не підтримується.")
    return States.NEWS_MENU

# Функція для показу історії пошуку
async def show_search_history(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    history = context.user_data.get('search_history', [])
    if history:
        history_text = "📝 **Історія пошуку:**\n\n" + "\n".join([f"{idx+1}. {query}" for idx, query in enumerate(history)])
    else:
        history_text = "📝 **Історія пошуку порожня.**"
    await update.message.reply_text(history_text, parse_mode='Markdown')
    return States.NEWS_MENU

# Функція для обробки виконання пошуку
async def handle_search_performing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.message.text.strip()
    if query:
        # Зберігаємо запит у історію пошуку
        if 'search_history' not in context.user_data:
            context.user_data['search_history'] = []
        context.user_data['search_history'].append(query)
        
        # Виконуємо пошук героїв
        matching_heroes = [
            hero["name"] for hero in heroes_data.get('heroes', [])
            if query.lower() in hero["name"].lower()
        ]
        
        if matching_heroes:
            buttons = []
            for i in range(0, len(matching_heroes), 4):
                row = matching_heroes[i:i + 4]
                buttons.append([KeyboardButton(hero) for hero in row])
            buttons.append([KeyboardButton("🔙 Назад")])
            reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=False)
            await update.message.reply_text(f"🔍 **Результати пошуку для '{query}':**", parse_mode='Markdown', reply_markup=reply_markup)
            return States.SEARCH_HERO_GUIDES
        else:
            await update.message.reply_text(f"🔍 Немає героїв або гайдів, що відповідають '{query}'.")
            await start(update, context)
            return States.MAIN_MENU
    else:
        await update.message.reply_text("Будь ласка, введіть коректний запит для пошуку.")
        return States.SEARCH_PERFORMING

# Функція для обробки вибору героя з результатів пошуку
async def handle_search_hero_guides(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    selected_hero = update.message.text.strip()
    if selected_hero in [hero["name"] for hero in heroes_data.get('heroes', [])]:
        hero_info = get_hero_info(selected_hero)
        if hero_info:
            hero_details = (
                f"📖 **Деталі про героя {selected_hero}:**\n\n"
                f"<b>Клас:</b> {hero_info.get('class', 'Невідомо')}\n"
                f"<b>Роль:</b> {hero_info.get('role', 'Невідомо')}\n"
                f"<b>HP:</b> {hero_info.get('hp', 'Невідомо')}\n"
                f"<b>Атака:</b> {hero_info.get('attack', 'Невідомо')}\n"
                f"<b>Захист:</b> {hero_info.get('defense', 'Невідомо')}\n\n"
                f"🔗 Детальніше: {hero_info.get('details_link', 'Немає посилання')}"
            )
            await update.message.reply_text(hero_details, parse_mode='HTML', disable_web_page_preview=True)
            # Повернення до пошуку
            buttons = [
                [KeyboardButton("🔍 Пошук героїв та гайдів"), KeyboardButton("🎙️ Голосовий пошук")],
                [KeyboardButton("📝 Історія пошуку"), KeyboardButton("🔙 Назад")]
            ]
            reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=False)
            await update.message.reply_text("🔍 Оберіть опцію:", reply_markup=reply_markup)
            return States.NEWS_MENU
        else:
            await update.message.reply_text("⚠️ Не вдалося знайти інформацію про цього героя.")
            return States.NEWS_MENU
    elif selected_hero == "🔙 Назад":
        await start(update, context)
        return States.MAIN_MENU
    else:
        await update.message.reply_text("⚠️ Вибрана опція не відповідає жодному герою.")
        await start(update, context)
        return States.MAIN_MENU

# Функція для отримання інформації про героя
def get_hero_info(hero_name: str) -> dict:
    return next((hero for hero in heroes_data.get('heroes', []) if hero['name'] == hero_name), None)

# Основна функція запуску бота
if __name__ == '__main__':
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    if not TELEGRAM_BOT_TOKEN:
        logger.error("❌ Не встановлено TELEGRAM_BOT_TOKEN в змінних оточення.")
        exit(1)
    if not OPENAI_API_KEY:
        logger.error("❌ Не встановлено OPENAI_API_KEY в змінних оточення.")
        exit(1)

    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Визначення ConversationHandler з усіма необхідними станами
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            States.MAIN_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu_handler)],
            States.CHARACTERS_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_characters_menu)],
            States.GUIDES_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_guides_menu)],
            States.TOURNAMENTS_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_tournaments_menu)],
            States.UPDATES_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_updates_menu)],
            States.BEGINNER_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_beginner_menu)],
            States.NEWS_MENU: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_news_menu),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_search_menu)
            ],
            States.SEARCH_PERFORMING: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_search_performing)],
            States.SEARCH_HERO_GUIDES: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_search_hero_guides)],
            States.HELP_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_help_menu)],
            States.QUIZZES_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_quizzes_menu)],
            # Додайте інші стани тут за потребою
        },
        fallbacks=[CommandHandler('start', start)]
    )

    # Додавання ConversationHandler до бота
    application.add_handler(conv_handler)

    logger.info("🔄 Бот запущено.")
    application.run_polling()
