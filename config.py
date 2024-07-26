import secrets
import os
from datetime import timedelta


# Local
# class Config:
#     MONGO_URI = os.getenv('MONGO_URI')
#     MONGO_DBNAME = 'SchoolCare'
#     SECRET_KEY = 'uma bela senha'
#     MAIL_SERVER = 'smtp.gmail.com'
#     MAIL_PORT = 587
#     MAIL_USE_TLS = True
#     MAIL_USERNAME = os.getenv('MAIL_USERNAME')
#     MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
#     PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)


# On render.com
class Config:
    MONGO_URI = os.getenv('MONGO_URI')
    MONGO_DBNAME = 'SchoolWarden'
    SECRET_KEY = os.getenv('SECRET_KEY')
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
