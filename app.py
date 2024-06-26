import uuid
import qrcode
from flask import Flask, render_template_string, request
from config import BOT_NAME

app = Flask(__name__, static_url_path='/static', static_folder='static')

# Store tokens and session strings
tokens = {}

bot_name = BOT_NAME


@app.route('/')
def index():
    token = str(uuid.uuid4())

    print('token generated: {}'.format(token))

    deep_link = f"https://t.me/{bot_name}?start={token}"
    qr_code = qrcode.make(deep_link)
    qr_code.save(f'static/{token}.png')
    return render_template_string('''
        <h1>Scan this QR code with your mobile device</h1>
        <img src="/static/{{ token }}.png">
    ''', token=token)


@app.route('/authorize/<token>')
def authorize(token):

    print('token for authorization {}'.format(token))

    if token not in tokens:
        return "Invalid or expired token", 400
    # Display a button to start the Telegram bot authorization
    return render_template_string('''
        <h1>Authorize the Desktop App</h1>
        <p>Click the button below to authorize the app using Telegram.</p>
        <a href="https://t.me/{{ bot_name }}?start={{ token }}">Authorize with Telegram</a>
    ''', bot_name=bot_name, token=token)


@app.route('/callback/<token>', methods=['POST'])
def callback(token):

    print('token for callback: {}'.format(token))

    session_string = request.form.get('session')
    if not session_string:
        return "Authorization failed", 400
    tokens[token] = session_string

    # Automatically save the session string to a file
    with open('session_data.txt', 'w') as f:
        f.write(session_string)

    return "Authorization successful, you can close this page"


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
