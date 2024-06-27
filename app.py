import asyncio
import logging
import uuid

import aiofiles
import qrcode
from hypercorn import Config
from hypercorn.asyncio import serve
from quart import Quart, render_template_string, request

from config import BOT_NAME

logging.basicConfig(level=logging.DEBUG)

app = Quart(__name__, static_url_path='/static', static_folder='static')

# Store tokens and session strings
tokens = {}

bot_name = BOT_NAME


@app.route('/')
async def index():
    token = str(uuid.uuid4())

    logging.info(f'token generated: {token}')

    deep_link = f"https://t.me/{bot_name}?start={token}"
    qr_code = qrcode.make(deep_link)
    qr_code.save(f'static/{token}.png')
    return await render_template_string('''
        <h1>Scan this QR code with your mobile device</h1>
        <img src="/static/{{ token }}.png">
    ''', token=token)


@app.route('/authorize/<token>')
async def authorize(token):
    logging.info(f'token for authorization: {token}')

    if token not in tokens:
        return "Invalid or expired token", 400
    # Display a button to start the Telegram bot authorization
    return await render_template_string('''
        <h1>Authorize the Desktop App</h1>
        <p>Click the button below to authorize the app using Telegram.</p>
        <a href="https://t.me/{{ bot_name }}?start={{ token }}">Authorize with Telegram</a>
    ''', bot_name=bot_name, token=token)


@app.route('/callback/<token>', methods=['POST'])
async def callback(token):
    logging.info(f'token for callback: {token}')

    form = await request.form
    session_string = form.get('session')
    if not session_string:
        return "Authorization failed", 400
    tokens[token] = session_string

    # Automatically save the session string to a file
    async with aiofiles.open('session_data.txt', 'w') as f:
        await f.write(session_string)

    return "Authorization successful, you can close this page"


async def main():
    config = Config()
    config.bind = ["0.0.0.0:5000"]
    logging.info("Starting Quart server")
    await serve(app, config)


if __name__ == '__main__':
    asyncio.run(main())
