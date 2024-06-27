import asyncio
import logging
import uuid

import aiofiles
import qrcode
from hypercorn import Config
from hypercorn.asyncio import serve
from quart import Quart, render_template_string, request, url_for

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

    # Save the token with an initial empty session string
    tokens[token] = None

    deep_link = f"https://t.me/{bot_name}?start={token}"
    fallback_url = url_for('authorize', token=token, _external=True)
    qr_code_url = f"{deep_link}\n{fallback_url}"
    qr_code = qrcode.make(qr_code_url)
    qr_code_path = f'static/{token}.png'
    qr_code.save(qr_code_path)

    return await render_template_string('''
        <h1>Authenticate with Telegram</h1>
        <p>You can either scan the QR code with your mobile device or click the button below to authorize using the desktop application.</p>
        <img src="/static/{{ token }}.png" alt="QR Code">
        <br><br>
        <a href="{{ fallback_url }}">
            <button>Authorize with Desktop App</button>
        </a>
    ''', token=token, fallback_url=fallback_url)


@app.route('/authorize/<token>')
async def authorize(token):
    logging.info(f'token for authorization: {token}')

    if token not in tokens:
        return "Invalid or expired token", 400
    # Display a button to start the Telegram bot authorization
    return await render_template_string('''
        <h1>Authorize the Desktop App</h1>
        <p>Click the button below to authorize the app using Telegram.</p>
        <a href="https://t.me/{{ bot_name }}?start={{ token }}">
            <button>Authorize with Telegram</button>
        </a>
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
