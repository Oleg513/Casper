import os
import logging
import asyncio
from telegram import Bot, Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, ConversationHandler
from dotenv import load_dotenv
import openai
from typing import List

# Завантаження змінних оточення
load_dotenv()

# Налаштування логування
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфігурація API та чати
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CHAT_IDS = [123456789, -987654321]  # Замініть на реальні числові chat ID

# Переконайтеся, що файли існують
PROMPTS_FILE = 'prompts.json'
HEROES_TANKS_FILE = 'heroes_tanks.json'

if not os.path.exists(PROMPTS_FILE):
    logger.error(f"Файл {PROMPTS_FILE} не знайдено.")
if not os.path.exists(HEROES_TANKS_FILE):
    logger.error(f"Файл {HEROES_TANKS_FILE} не знайдено.")

# Налаштування OpenAI
openai.api_key = OPENAI_API_KEY

async def fetch_fact():
    """Отримати цікавий факт від OpenAI GPT-4."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": "Розкажи цікавий факт"}],
            max_tokens=100
        )
        fact = response.choices[0].message['content']
        logger.info("Отримано факт від OpenAI")
        return fact
    except Exception as e:
        logger.error(f"Помилка запиту до OpenAI API: {e}")
        return "Не вдалося отримати факт зараз."

async def send_fact_to_chats(chat_ids: List[int]):
    """Надіслати факт у вказані чати."""
    fact = await fetch_fact()
    for chat_id in chat_ids:
        try:
            await bot.send_message(chat_id=chat_id, text=fact)
            logger.info(f"Повідомлення надіслано до чату {chat_id}")
        except Exception as e:
            logger.error(f"Помилка надсилання до чату {chat_id}: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробник команди /start."""
    try:
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("Bot", callback_data='bot')],
            [InlineKeyboardButton("Привіт", callback_data='privit')]
        ])
        await update.message.reply_text("🔍 Оберіть опцію:", reply_markup=reply_markup)
        logger.info("Користувач ініціював команду /start")
    except telegram.error.BadRequest as e:
        logger.error(f"BadRequest: {e}")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Обробник помилок."""
    logger.error(msg="Виникла помилка:", exc_info=context.error)

async def main():
    """Основна функція для запуску бота."""
    global bot
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Додати обробник команди /start
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    # Додати обробник помилок
    application.add_error_handler(error_handler)

    # Запустити бота
    await application.initialize()
    await application.start()

    # Запустити асинхронну задачу для надсилання фактів кожні 2 години
    async def periodic_fact_sender():
        while True:
            await send_fact_to_chats(CHAT_IDS)
            await asyncio.sleep(2 * 60 * 60)  # Кожні 2 години

    application.create_task(periodic_fact_sender())

    await application.updater.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.critical(f"Несподівана помилка: {e}")
