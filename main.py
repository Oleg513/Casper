import os
import asyncio
import random
import logging
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Налаштування логування
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Завантаження токену Telegram API
telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
bot = Bot(token=telegram_bot_token)

# Ваш chat_id
CHAT_ID = 579063567  # твій chat_id

# Функція для надсилання повідомлення
async def bot_send_message(message):
    try:
        await bot.send_message(chat_id=CHAT_ID, text=message)
        logger.info(f"Message sent: {message}")
    except Exception as e:
        logger.error(f"Failed to send message: {e}")

# Перевірка тригерних слів
def should_respond(message):
    trigger_words = ["бот", "GPT", "друг"]
    return any(word in message.lower() for word in trigger_words)

# Визначення питання
def is_question(message):
    return "?" in message

# Випадкова відповідь
responses = [
    "Ну що, друзі, як настрій? 😉",
    "Чого мовчите, може вам допомогти?",
    "Питання не терпить зволікань! Де відповідь?",
    "Завжди тут, якщо потрібно щось підказати!"
]

def get_personal_response():
    return random.choice(responses)

# Відстеження часу останнього повідомлення
last_message_time = None

# Перевірка паузи
async def check_inactivity():
    global last_message_time
    while True:
        if last_message_time and (asyncio.get_event_loop().time() - last_message_time > 180):  # 3 хвилини пауза
            await bot_send_message("Що скажеш? Забули про мене? 😉")
            last_message_time = None
        await asyncio.sleep(10)  # Перевірка кожні 10 секунд

# Основний обробник повідомлень
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global last_message_time
    last_message_time = asyncio.get_event_loop().time()
    
    message = update.message.text
    logger.info(f"Received message: {message}")
    
    if should_respond(message):
        response = get_personal_response()
        await bot_send_message(response)
    elif is_question(message) and random.random() > 0.5:  # 50% шанс на відповідь
        await bot_send_message("О, питання на горизонті! Де відповіді, люди?")

# Основна функція запуску бота
def main():
    application = Application.builder().token(telegram_bot_token).build()
    
    # Додаємо обробник для текстових повідомлень
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запускаємо бота
    application.run_polling()

# Запуск основної функції
if __name__ == "__main__":
    main()
