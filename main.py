import os
import asyncio
import logging
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Налаштування токену та ID чатів
telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
bot = Bot(token=telegram_bot_token)

# Вкажи ID для чату та свій особистий chat_id
CHAT_ID = -123456789  # Замініть на реальний ID групового чату
PERSONAL_CHAT_ID = 579063567  # Ваш особистий ID

# Налаштування логування
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Функція для надсилання повідомлення
async def send_message(chat_id, message):
    logger.info(f"Спроба надсилання повідомлення до {chat_id}: {message}")
    try:
        await bot.send_message(chat_id=chat_id, text=message)
        logger.info(f"Повідомлення успішно надіслано до {chat_id}.")
    except Exception as e:
        logger.error(f"Не вдалося надіслати повідомлення до {chat_id}: {e}")

# Обробник команди /get_chat_id
async def get_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await update.message.reply_text(f"Ваш CHAT_ID: {chat_id}")

# Функція для перевірки прав бота
async def check_bot_permissions():
    try:
        member = await bot.get_chat_member(chat_id=CHAT_ID, user_id=bot.id)
        if member.status in ['administrator', 'member']:
            logger.info("Бот має необхідні права в групі.")
        else:
            logger.warning("Бот не має необхідних прав в групі.")
    except Exception as e:
        logger.error(f"Помилка при перевірці прав бота: {e}")

# Функція для автоматичної розсилки
async def automatic_broadcast():
    # Затримка в 1 хвилину перед початком розсилки
    await asyncio.sleep(60)
    while True:
        # Повідомлення в груповий чат
        await send_message(CHAT_ID, "Це автоматичне повідомлення для групового чату.")
        
        # Особисте повідомлення
        await send_message(PERSONAL_CHAT_ID, "Це автоматичне особисте повідомлення.")
        
        # Затримка в 30 секунд між повідомленнями
        await asyncio.sleep(30)

# Основна функція запуску
async def main():
    application = ApplicationBuilder().token(telegram_bot_token).build()

    # Додаємо обробник команди /get_chat_id
    application.add_handler(CommandHandler("get_chat_id", get_chat_id))

    # Перевіряємо права бота
    await check_bot_permissions()

    # Запускаємо автоматичну розсилку в окремому завданні
    asyncio.create_task(automatic_broadcast())

    # Запускаємо бота
    await application.run_polling()

# Запуск бота
if __name__ == "__main__":
        asyncio.run(main())
    
