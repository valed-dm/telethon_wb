from threading import Thread
from app import app
import asyncio
from bot import start_bot


# Function to run Flask app
def run_flask():
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)


# Function to run the Telegram bot
def run_telegram_bot():
    asyncio.run(start_bot())


if __name__ == '__main__':
    # Start Flask app in a separate thread
    flask_thread = Thread(target=run_flask)
    flask_thread.start()

    # Start Telegram bot in the main thread
    run_telegram_bot()
