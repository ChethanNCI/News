"""
Django settings for news project.
"""

from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv
import os
import hvac
from django.core.exceptions import ImproperlyConfigured 
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv()

# --- SONARQUBE CONSTANTS ---
SELF = "'self'"
JSDELIVR = "https://cdn.jsdelivr.net"
FONTAWESOME_KIT = "https://kit.fontawesome.com"
NONE = "'none'"

def get_vault_client():
    vault_url = os.getenv('VAULT_ADDR', 'https://vault.demo.internal:8200')
    # verify=False because you are using self-signed certs (based on your curl -k)
    client = hvac.Client(url=vault_url, verify=False)
    
    token = os.getenv('VAULT_TOKEN')
    if token:
        client.token = token
    else:
        try:
            # Kubernetes Auth Method
            with open('/var/run/secrets/kubernetes.io/serviceaccount/token', 'r') as f:
                jwt = f.read()
            client.auth.kubernetes.login(role="newstrends-role", jwt=jwt)
        except Exception as e:
            if os.getenv('DEBUG') == 'True':
                return None
            raise ImproperlyConfigured(f"Vault authentication failed: {e}")
    return client

def get_secret(client, path, key):
    if not client:
        return "django-insecure-dev-fallback"
    try:
        response = client.secrets.kv.v2.read_secret_version(
            mount_point='kv', 
            path=path
        )
        # KV v2 stores data inside ['data']['data']
        return response['data']['data'][key]
    except Exception as e:
        if os.getenv('DEBUG') == 'True':
            return f"fallback-{key}"
        raise ImproperlyConfigured(f"Could not fetch {key} from Vault path {path}: {e}")

# Initialize Vault and fetch secrets
vault_client = get_vault_client()
SECRET_KEY = get_secret(vault_client, 'DJANGO_SECRET_KEY', 'DJANGO_SECRET_KEY')
NEWS_API_KEY = get_secret(vault_client, 'newsapi', 'API_KEY')

DEBUG = os.getenv('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'csp',
    'base',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'csp.middleware.CSPMiddleware', 
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'news.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'news.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "base" / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ALLOWED_ORIGINS = ["http://localhost:8000"]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
}

# --- CONTENT SECURITY POLICY ---
CONTENT_SECURITY_POLICY = {
    'DIRECTIVES': {
        'default-src': (SELF,),
        'script-src': (SELF, JSDELIVR, FONTAWESOME_KIT),
        'style-src': (SELF, JSDELIVR, "https://kit-free.fontawesome.com"),
        'img-src': (SELF, "https:", "data:"),
        'font-src': (SELF, JSDELIVR, FONTAWESOME_KIT),
        'connect-src': (SELF,),
        'media-src': (SELF,),
        'object-src': (NONE,),
        'frame-src': (SELF,),
        'frame-ancestors': (NONE,),
        'base-uri': (SELF,),
        'manifest-src': (SELF,),
        'worker-src': (SELF,),
        'child-src': (SELF,),
        'prefetch-src': (SELF,),
    }
}

AUTH_USER_MODEL = 'base.CustomUser'
LOGIN_REDIRECT_URL = 'home' # Changed from '/' to a named URL or valid path