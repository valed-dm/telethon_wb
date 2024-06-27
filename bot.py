import logging

import requests
from telethon import TelegramClient, events
from telethon.sessions import StringSession

from config import API_HASH, API_ID, BOT_TOKEN

logging.basicConfig(level=logging.DEBUG)

api_id = API_ID
api_hash = API_HASH
bot_token = BOT_TOKEN


async def start_bot():
    # Create a client for handling sessions
    client = TelegramClient(StringSession(), api_id, api_hash)
    await client.connect()

    # Start the bot
    bot = TelegramClient('bot', api_id, api_hash)
    await bot.start(bot_token=bot_token)

    @bot.on(events.NewMessage(pattern='/start'))
    async def start(event):
        raw_text = event.raw_text
        token = None

        # Extract token from the /start command
        if ' ' in raw_text:
            token = raw_text.split(' ', 1)[1].strip()
        elif '\n' in raw_text:
            token = raw_text.split('\n', 1)[1].strip()

        logging.info(f'token received: {token}')

        # Verify that the token is present and not empty
        if not token:
            await event.reply("Invalid start command. No token found.")
            return

        try:
            session_string = client.session.save()
            response = requests.post(f'http://localhost:5000/callback/{token}', data={'session': session_string})
            if response.status_code == 200:
                await event.reply("You have been authenticated! You can now use the desktop app.")
            else:
                await event.reply("Authorization failed, please try again.")
        except Exception as e:
            await event.reply(f"An error occurred: {str(e)}")
            logging.error("An error occurred: %s", str(e))

    await bot.run_until_disconnected()
    await client.disconnect()


if __name__ == '__main__':
    import asyncio

    asyncio.run(start_bot())
