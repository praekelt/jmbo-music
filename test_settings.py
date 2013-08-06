from foundry.settings import *


DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.spatialite',
        'NAME': 'test_music.db',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

JMBO_MUSIC = {
    'lastfm_api_key': 'c91d15b736995c4dac4e8b2b8cdbdb98 ',
    'lastfm_api_secret': '3aa997f9cf9e655f44a35c79fb67544f',
}
