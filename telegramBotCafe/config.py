import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


TOKEN = os.getenv('TOKEN')
PAY = os.getenv('PORTMONE')
MANAGER = os.getenv('MANAGER')


DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_ADDRESS = os.getenv('DB_ADDRESS')
DB_NAME = os.getenv('DB_NAME')

DATABASE_URL = f'postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_ADDRESS}/{DB_NAME}'
