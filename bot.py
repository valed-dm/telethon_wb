import logging

import httpx
from telethon import TelegramClient, events
from telethon.errors import UserIsBlockedError
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
        sender = await event.get_sender()
        sender_info = {
            'first_name': sender.first_name,
            'last_name': sender.last_name,
            'username': sender.username
        }
        raw_text = event.raw_text
        token = None

        # Extract token from the /start command
        if ' ' in raw_text:
            token = raw_text.split(' ', 1)[1].strip()
        elif '\n' in raw_text:
            token = raw_text.split('\n', 1)[1].strip()

        # Ignore if the start command doesn't contain a token
        if not token:
            if raw_text == '/start':
                logging.info("Received a plain /start command without token, ignoring.")
                return
            await event.reply("Invalid start command. No token found.")
            return

        try:
            session_string = client.session.save()
            async with httpx.AsyncClient() as cl:
                response = await cl.post(
                    f'http://localhost:5000/callback/{token}',
                    data={'session': session_string, **sender_info}
                )
                if response.status_code == 200:
                    await event.reply("You have been authenticated! You can now use the desktop app.")
                else:
                    await event.reply("Authorization failed, please try again.")
        except UserIsBlockedError:
            logging.error(f"User has blocked the bot: {event.chat_id}")
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            try:
                await event.reply(f"An error occurred: {str(e)}")
            except UserIsBlockedError:
                logging.error(f"User has blocked the bot: {event.chat_id}")

    await bot.run_until_disconnected()
    await client.disconnect()


if __name__ == '__main__':
    import asyncio

    asyncio.run(start_bot())
