import secrets
import os


class Config:
    MONGO_URI = os.getenv('MONGO_URI')
    MONGO_URI = 'mongodb://localhost:27017/SchoolCare'
    MONGO_DBNAME = 'SchoolWarden'
    SECRET_KEY = secrets.token_urlsafe(32)
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
