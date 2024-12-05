import os

from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()


API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
BOT_TOKEN = os.getenv('BOT_TOKEN')
BOT_NAME = os.getenv('BOT_NAME')
SECRET_KEY = os.getenv('SECRET_KEY')
SESSION_STRING = None
NGROK_URL = os.getenv('NGROK_URL')
