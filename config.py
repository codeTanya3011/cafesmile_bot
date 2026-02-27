import os
from pathlib import Path 
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


TOKEN = os.getenv('TOKEN')
PAY = os.getenv('PORTMONE')
MANAGER = os.getenv('MANAGER')


MEDIA_PATH = Path(os.getenv("MEDIA_PATH", "./media")).resolve()


DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_ADDRESS = os.getenv('DB_ADDRESS')
DB_NAME = os.getenv('DB_NAME')


DB_URL = os.getenv("DB_URL")
