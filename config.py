import os


class Config:
    SECRET_KEY = 'uma-chave-secreta-muito-segura'
    MONGO_URI = os.getenv('MONGO_URI')
