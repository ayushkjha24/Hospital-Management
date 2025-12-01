class Config:
    SECRET_KEY = 'ayushkjha24'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = 'supersecretkey'
    JWT_ACCESS_TOKEN_EXPIRES = 3600   # 1 hour
    JWT_REFRESH_TOKEN_EXPIRES = 86400 # 1 day
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']

    PROPAGATE_EXCEPTIONS = True

    # NEW-STYLE CELERY CONFIG KEYS
    broker_url = "redis://localhost:6379/0"
    result_backend = "redis://localhost:6379/1"

    # Optional recommended new keys:
    task_serializer = "json"
    accept_content = ["json"]
    result_serializer = "json"
    timezone = "UTC"
    enable_utc = True

    # Redis (for caching)
    REDIS_URL = "redis://localhost:6379/0"

    # Mail config
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = "<YOUR EMAIL>"
    MAIL_PASSWORD = "<APP SPECIFIC PASSWORD>"
    MAIL_DEFAULT_SENDER = "<YOUR EMAIL>"
