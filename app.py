import asyncio
import logging
import uuid
import aiofiles
import qrcode
from hypercorn import Config
from hypercorn.asyncio import serve
from quart import Quart, render_template_string, request

from config import BOT_NAME, NGROK_URL

logging.basicConfig(level=logging.DEBUG)

app = Quart(__name__, static_url_path='/static', static_folder='static')

# Store tokens and session strings
tokens = {}

bot_name = BOT_NAME
ngrok_url = NGROK_URL


@app.route('/')
async def index():
    token = str(uuid.uuid4())

    logging.info(f'token generated: {token}')

    deep_link = f"https://t.me/{bot_name}?start={token}"
    fallback_url = f"{ngrok_url}/authorize/{token}"

    # Generate separate QR codes
    qr_code_deep_link = qrcode.make(deep_link)
    qr_code_fallback_url = qrcode.make(fallback_url)

    # Save the QR codes as images
    qr_code_deep_link.save(f'static/{token}_telegram.png')
    qr_code_fallback_url.save(f'static/{token}_fallback.png')

    # Store the token
    tokens[token] = None

    return await render_template_string('''
        <h1>Authenticate with your mobile device</h1>
        <p>Scan this QR code to open the Telegram bot:</p>
        <img src="/static/{{ token }}_telegram.png">
        <p>Or click the button below to authorize with the desktop app:</p>
        <a href="{{ fallback_url }}"><button>Authorize with Desktop App</button></a>
        <p>If you prefer, you can also scan this QR code to authorize with the desktop app:</p>
        <img src="/static/{{ token }}_fallback.png">
    ''', token=token, fallback_url=fallback_url)


@app.route('/authorize/<token>')
async def authorize(token):
    logging.info(f'token for authorization: {token}')

    if token not in tokens:
        return "Invalid or expired token", 400

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
