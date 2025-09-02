ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ".tox/test.sqlite3",
    }
}
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
DEBUG = True
INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.admin",
    "rosetta",
    "testproject",
    "csu",
]
LANGUAGES = [
    ("en", "EN"),
    ("ro", "RO"),
]
LOCALE_PATHS = ["src/csu/locale"]
LOGIN_REDIRECT_URL = "/"
LOGIN_URL = "/admin/login/"
MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]
PHONENUMBER_DB_FORMAT = "NATIONAL"
PHONENUMBER_DEFAULT_REGION = "RO"
PRODUCER_SLEEP_SECONDS = None
REST_FRAMEWORK = {}
ROOT_URLCONF = "testproject.urls"
SECRET_KEY = __name__
STATIC_URL = "/static/"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "OPTIONS": {
            "debug": DEBUG,
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]
TIME_ZONE = "Europe/Bucharest"
USE_I18N = True
USE_TZ = True
API_TOKEN = None
