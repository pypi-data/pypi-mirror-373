valar for morghulis

# 1. install

```shell
pip install valar
```

# 1. settings

```python
from django.core.management.utils import get_random_secret_key
from pathlib import Path

"""       Compulsory settings       """

DEBUG = True
BASE_DIR = Path(__file__).resolve().parent.parent
BASE_APP = str(BASE_DIR.name)
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
SECRET_KEY = get_random_secret_key()

"""       Valar Options       """

HANDLER_MAPPING = "%s.urls.channel_mapping" % BASE_APP
MONGO_URI = 'mongodb://root:19870120@121.41.111.175:27017/'
MINIO_URL = "s3://admin:password@120.27.8.186:9000"

"""       Minimized compulsory settings       """

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
INSTALLED_APPS = [
    'django.contrib.sessions',
    "corsheaders",
    'channels',
    'valar.apps.ValarConfig',
]
MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
]
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
ROOT_URLCONF = "%s.urls" % BASE_APP
ASGI_APPLICATION = "%s.asgi.application" % BASE_APP

"""       Optional settings       """

ALLOWED_HOSTS = ['*']
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = False
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_AGE = 60 * 60
FILE_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024 * 100
DATA_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024 * 100

```

# 2. asgi

```python
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import re_path
from valar.channels.consumer import ValarConsumer

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': URLRouter([
        re_path(r'(?P<client>\w+)/$', ValarConsumer.as_asgi()),
    ])
})

```

# 3. migrate

no need, valar will auto migration

# 4. root urls

no need, valar will auto set urlpatterns

# 5. how to use valar_channel

5.1 set HANDLER_MAPPING in settings

```python
HANDLER_MAPPING = "%s.urls.channel_mapping" % BASE_APP
```

5.2 create a handler

```python
from valar.channels.sender import ValarSocketSender


def test_handler(sender: ValarSocketSender):
    data = sender.data
    sender.load(data)
```

5.3 register handler in channel_mapping

```python
channel_mapping = {
    'test': test_handler,
}
```