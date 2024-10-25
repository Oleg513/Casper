import os
import asyncio
import logging
from telegram import Bot

# Налаштування токену та ID чатів
telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
bot = Bot(token=telegram_bot_token)

# Вкажи ID для чату та свій особистий chat_id
CHAT_ID = 123456789  # ID групового чату
PERSONAL_CHAT_ID = 579063567  # Твій особистий ID

# Налаштування логування
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Функція для надсилання повідомлення
async def send_message(chat_id, message):
    try:
        await bot.send_message(chat_id=chat_id, text=message)
        logger.info(f"Message sent to {chat_id}: {message}")
    except Exception as e:
        logger.error(f"Failed to send message to {chat_id}: {e}")

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
    # Запускаємо функцію розсилки
    await automatic_broadcast()

# Запуск бота
if __name__ == "__main__":
    asyncio.run(main())
