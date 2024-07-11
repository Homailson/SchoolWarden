import secrets


class Config:
    MONGO_URI = '<mongo_uri>'
    MONGO_DBNAME = 'monbo_db_name'
    SECRET_KEY = secrets.token_urlsafe(32)
    MAIL_SERVER = 'smtp.example.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'example@gmail.com'
    MAIL_PASSWORD = '<email_password>'
