import os
import logging
import asyncio
from telegram import Bot
from dotenv import load_dotenv
import openai
from typing import List

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CHAT_IDS = [123456789, -987654321]  # Replace with actual numeric chat IDs

bot = Bot(token=TELEGRAM_BOT_TOKEN)
openai.api_key = OPENAI_API_KEY

async def fetch_fact():
    """Fetch an interesting fact from OpenAI GPT-4."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": "Розкажи цікавий факт"}],
            max_tokens=100
        )
        fact = response.choices[0].message['content']
        logger.info("Fetched fact from OpenAI")
        return fact
    except Exception as e:
        logger.error(f"Error fetching fact from OpenAI API: {e}")
        return "Не вдалося отримати факт зараз."

async def send_fact_to_chats(chat_ids: List[int]):
    """Send the fact to specified chats."""
    fact = await fetch_fact()
    for chat_id in chat_ids:
        try:
            await bot.send_message(chat_id=chat_id, text=fact)
            logger.info(f"Message sent to chat {chat_id}")
        except Exception as e:
            logger.error(f"Error sending to chat {chat_id}: {e}")

async def main():
    while True:
        await send_fact_to_chats(CHAT_IDS)
        await asyncio.sleep(2 * 60 * 60)  # Every 2 hours

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.critical(f"Unexpected error: {e}")
