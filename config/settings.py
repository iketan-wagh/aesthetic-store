"""
Django settings for config project.
"""

from pathlib import Path
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-noma-aesthetic-lifestyle-secret-key-genz-vibe')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')

CSRF_TRUSTED_ORIGINS = [
    origin.strip() for origin in os.environ.get(
        'CSRF_TRUSTED_ORIGINS',
        'https://*.onrender.com,https://*.railway.app,https://*.up.railway.app,http://localhost:8000,http://127.0.0.1:8000'
    ).split(',') if origin.strip()
]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Custom Store Apps
    'core.apps.CoreConfig',
    'accounts.apps.AccountsConfig',
    'products.apps.ProductsConfig',
    'cart.apps.CartConfig',
    'wishlist.apps.WishlistConfig',
    'orders.apps.OrdersConfig',
    'coupons.apps.CouponsConfig',
    'reviews.apps.ReviewsConfig',
    'dashboard.apps.DashboardConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.global_context',
                'cart.context_processors.cart_context',
                'wishlist.context_processors.wishlist_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database Configuration (MySQL / MariaDB / Cloud DB)
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
import pymysql
pymysql.install_as_MySQLdb()

import dj_database_url

DATABASE_URL = os.environ.get('DATABASE_URL') or os.environ.get('MYSQL_URL') or os.environ.get('MYSQL_PUBLIC_URL')
DB_ENGINE = os.environ.get('DB_ENGINE', '').lower()

if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
    if 'mysql' in DATABASE_URL:
        DATABASES['default']['OPTIONS'] = {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        }
elif DB_ENGINE == 'mysql' or os.environ.get('MYSQL_DATABASE') or os.environ.get('MYSQLDATABASE') or os.environ.get('MYSQL_DB'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.environ.get('MYSQLDATABASE') or os.environ.get('MYSQL_DATABASE') or os.environ.get('MYSQL_DB') or os.environ.get('DB_NAME', 'aesthetic_store_db'),
            'USER': os.environ.get('MYSQLUSER') or os.environ.get('MYSQL_USER') or os.environ.get('DB_USER', 'root'),
            'PASSWORD': os.environ.get('MYSQLPASSWORD') or os.environ.get('MYSQL_PASSWORD') or os.environ.get('DB_PASSWORD', ''),
            'HOST': os.environ.get('MYSQLHOST') or os.environ.get('MYSQL_HOST') or os.environ.get('DB_HOST', '127.0.0.1'),
            'PORT': os.environ.get('MYSQLPORT') or os.environ.get('MYSQL_PORT') or os.environ.get('DB_PORT', '3306'),
            'OPTIONS': {
                'charset': 'utf8mb4',
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            },
            'CONN_MAX_AGE': 600,
        }
    }
elif os.environ.get('DB_NAME') or os.environ.get('POSTGRES_DB'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DB_NAME') or os.environ.get('POSTGRES_DB', 'aesthetic_store_db'),
            'USER': os.environ.get('DB_USER') or os.environ.get('POSTGRES_USER', 'postgres'),
            'PASSWORD': os.environ.get('DB_PASSWORD') or os.environ.get('POSTGRES_PASSWORD', ''),
            'HOST': os.environ.get('DB_HOST') or os.environ.get('POSTGRES_HOST', 'localhost'),
            'PORT': os.environ.get('DB_PORT') or os.environ.get('POSTGRES_PORT', '5432'),
            'CONN_MAX_AGE': 600,
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
os.makedirs(MEDIA_ROOT, exist_ok=True)
os.makedirs(MEDIA_ROOT / 'products', exist_ok=True)
os.makedirs(MEDIA_ROOT / 'categories', exist_ok=True)
os.makedirs(MEDIA_ROOT / 'avatars', exist_ok=True)

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Authentication & Redirects
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'accounts:profile'
LOGOUT_REDIRECT_URL = 'core:home'

# Messages Framework
from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.DEBUG: 'debug',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'error',
}

# Cart & Shipping settings
FREE_SHIPPING_THRESHOLD = 999  # INR
DEFAULT_SHIPPING_FEE = 99      # INR

RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID', 'rzp_test_TWVVLy5RVzwlJ9')
RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET', '95X4uuyNvzYuv67VEiBFeE15')

def _clean_env(key, default=''):
    raw = os.environ.get(key, default)
    if raw is None:
        return default
    return str(raw).strip(' \t\n\r"\'')

# Email Configuration
EMAIL_BACKEND = _clean_env('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = _clean_env('EMAIL_HOST', 'smtp.gmail.com')
try:
    EMAIL_PORT = int(_clean_env('EMAIL_PORT', '587'))
except ValueError:
    EMAIL_PORT = 587

_use_tls_env = _clean_env('EMAIL_USE_TLS', 'True').lower()
_use_ssl_env = _clean_env('EMAIL_USE_SSL', 'False').lower()

if EMAIL_PORT == 465 or _use_ssl_env in ('true', '1', 'yes'):
    EMAIL_USE_SSL = True
    EMAIL_USE_TLS = False
    EMAIL_PORT = 465
else:
    EMAIL_USE_TLS = _use_tls_env in ('true', '1', 'yes', 't')
    EMAIL_USE_SSL = False

EMAIL_HOST_USER = _clean_env('EMAIL_HOST_USER', 'ketanwagh714@gmail.com')
EMAIL_HOST_PASSWORD = _clean_env('EMAIL_HOST_PASSWORD', 'dsvrrdfznhtrhuqh').replace(' ', '')
DEFAULT_FROM_EMAIL = _clean_env('DEFAULT_FROM_EMAIL', f'Aesthetic Store <{EMAIL_HOST_USER}>')
EMAIL_TIMEOUT = 10

# Google OAuth2 Credentials (from https://console.cloud.google.com/)
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', '')
