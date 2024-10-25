import os
import asyncio
import random
from datetime import datetime
import openai
from telegram import Bot

# Завантажуємо ключі з змінних середовища
openai.api_key = os.getenv("OPENAI_API_KEY")
telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
bot = Bot(token=telegram_bot_token)

# Функція для надсилання повідомлення через Telegram
async def bot_send_message(chat_id, message):
    await bot.send_message(chat_id=chat_id, text=message)

# Функція для перевірки, чи повідомлення містить тригерні слова
def should_respond(message):
    trigger_words = ["бот", "GPT", "друг"]
    return any(word in message.lower() for word in trigger_words)

# Логіка для визначення, чи є повідомлення питанням
def is_question(message):
    return "?" in message

# Функція вибору випадкової відповіді з набору
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

# Перевірка паузи в активності користувачів
async def check_inactivity(chat_id):
    global last_message_time
    while True:
        if last_message_time and (asyncio.get_event_loop().time() - last_message_time > 180):  # Пауза в 3 хвилини
            await bot_send_message(chat_id, "Що скажеш? Забули про мене? 😉")
            last_message_time = None
        await asyncio.sleep(10)  # Перевірка кожні 10 секунд

# Основний обробник повідомлень
async def handle_message(chat_id, message):
    global last_message_time
    last_message_time = asyncio.get_event_loop().time()  # Оновлення часу останнього повідомлення
    
    if should_respond(message):
        response = get_personal_response()
        await bot_send_message(chat_id, response)
    elif is_question(message) and random.random() > 0.5:  # 50% шанс на відповідь
        await bot_send_message(chat_id, "О, питання на горизонті! Де відповіді, люди?")

# Основна функція запуску бота
async def main(chat_id):
    asyncio.create_task(check_inactivity(chat_id))
    await start_message_listener(chat_id, handle_message)  # Імітуємо функцію прослуховування повідомлень

# Імітація прослуховування повідомлень (для тестування)
async def start_message_listener(chat_id, callback):
    test_messages = [
        "Привіт, бот!",
        "Чого мовчите, люди?",
        "Ой, у мене питання?",
        "Хтось тут ще є?",
        "Ти де, друг?",
    ]
    for msg in test_messages:
        await callback(chat_id, msg)
        await asyncio.sleep(2)

# Запускаємо основну функцію
chat_id = "YOUR_CHAT_ID"  # Вкажи тут свій ідентифікатор чату для тестування
asyncio.run(main(chat_id))
