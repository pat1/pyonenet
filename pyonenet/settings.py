# Django settings for pyonenet project.

import os
from configobj import ConfigObj,flatten_errors
from validate import Validator

import logging
logging.getLogger('django.db.backends').setLevel(logging.ERROR)


import platform
if platform.system() == "Linux":
    config_site_file = '/etc/pyonenet/pyonenet-site.cfg'
    config_user_file = '~/.pyonenet.cfg'
    config_file      = 'pyonenet.cfg'
else:
    config_site_file = 'c:\pyonenet-site_win.cfg'
    config_user_file = '~/.pyonenet_win.cfg'
    config_file      = 'pyonenet_win.cfg'


configspec={}

configspec['django']={}

configspec['django']['DEBUG']="boolean(default=True)"
configspec['django']['TEMPLATE_DEBUG']="boolean(default=True)"
configspec['django']['FILE_UPLOAD_PERMISSIONS']="integer(default=420)"
configspec['django']['SECRET_KEY']="string(default='random-string-of-ascii')"
configspec['django']['SESSION_COOKIE_DOMAIN']="string(default=None)"
configspec['django']['SERVER_EMAIL']="string(default='localhost')"
configspec['django']['EMAIL_HOST']="string(default='localhost')"
configspec['django']['TIME_ZONE']="string(default='Europe/Rome')"
configspec['django']['LANGUAGE_CODE']="string(default='en-us')"
configspec['django']['SITE_ID']="integer(default=1)"
configspec['django']['USE_I18N']="boolean(default=True)"
configspec['django']['LOCALE_PATHS']="list(default=list('locale',))"
configspec['django']['ADMINS']="list(default=list('',))"
configspec['django']['MANAGERS']="list(default=list('',))"
configspec['django']['MEDIA_ROOT']="string(default='%s/media/')" % os.getcwd()
configspec['django']['MEDIA_SITE_ROOT']="string(default='%s/media/')" % os.getcwd()
configspec['django']['MEDIA_URL']="string(default='/django/media/')"
#configspec['django']['ADMIN_MEDIA_PREFIX']="string(default='/django/media/admin/')"
configspec['django']['STATIC_URL']="string(default='/static/')"
configspec['django']['STATIC_ROOT'] = "string(default='%s/static/')" % os.getcwd()
configspec['django']['MEDIA_PREFIX']="string(default='/media/')"
configspec['django']['MEDIA_SITE_PREFIX']="string(default='/media/sito/')"
configspec['django']['SERVE_STATIC']="boolean(default=True)"
configspec['django']['LOGIN_URL']="string(default='/login/')"


configspec['pyonenetweb']={}

configspec['pyonenetweb']['logfile']  = "string(default='/tmp/pyonenetweb.log')"
configspec['pyonenetweb']['errfile']  = "string(default='/tmp/pyonenetweb.err')"
configspec['pyonenetweb']['lockfile'] = "string(default='/tmp/pyonenetweb.lock')"
configspec['pyonenetweb']['user']     = "string(default=None)"
configspec['pyonenetweb']['group']    = "string_list(default=None)"
configspec['pyonenetweb']['port']    = "string(default='8080')"


configspec['database']={}

configspec['database']['DATABASE_USER']="string(default='')"
configspec['database']['DATABASE_PASSWORD']="string(default='')"
configspec['database']['DATABASE_HOST']="string(default='localhost')"
configspec['database']['DATABASE_PORT']="integer(default=3306)"
configspec['database']['DATABASE_ENGINE']="string(default='sqlite3')"
configspec['database']['DATABASE_NAME']="string(default='%s/pyonenet.sqlite3')" % os.getcwd()


config    = ConfigObj (config_site_file,file_error=False,configspec=configspec,interpolation=False)

usrconfig = ConfigObj (os.path.expanduser(config_user_file),file_error=False,interpolation=False)
config.merge(usrconfig)
usrconfig = ConfigObj (config_file,file_error=False, interpolation=False)
config.merge(usrconfig)

val = Validator()
test = config.validate(val,preserve_errors=True)
for entry in flatten_errors(config, test):
    # each entry is a tuple
    section_list, key, error = entry
    if key is not None:
       section_list.append(key)
    else:
        section_list.append('[missing section]')
    section_string = ', '.join(section_list)
    if error == False:
        error = 'Missing value or section.'
    print section_string, ' = ', error
    raise error

# section django
DEBUG                   = config['django']['DEBUG']
FILE_UPLOAD_PERMISSIONS = config['django']['FILE_UPLOAD_PERMISSIONS']
SECRET_KEY              = config['django']['SECRET_KEY']
SESSION_COOKIE_DOMAIN   = config['django']['SESSION_COOKIE_DOMAIN']
SERVER_EMAIL            = config['django']['SERVER_EMAIL']
EMAIL_HOST              = config['django']['EMAIL_HOST']
TIME_ZONE               = config['django']['TIME_ZONE']
LANGUAGE_CODE           = config['django']['LANGUAGE_CODE']
SITE_ID                 = config['django']['SITE_ID']
USE_I18N                = config['django']['USE_I18N']
LOCALE_PATHS            = config['django']['LOCALE_PATHS']
ADMINS                  = config['django']['ADMINS']
MANAGERS                = config['django']['MANAGERS']
MEDIA_ROOT              = config['django']['MEDIA_ROOT']
MEDIA_SITE_ROOT         = config['django']['MEDIA_SITE_ROOT']
MEDIA_URL               = config['django']['MEDIA_URL']
#ADMIN_MEDIA_PREFIX      = config['django']['ADMIN_MEDIA_PREFIX']
STATIC_URL              = config['django']['STATIC_URL']
STATIC_ROOT             = config['django']['STATIC_ROOT']
MEDIA_PREFIX            = config['django']['MEDIA_PREFIX']
SITE_MEDIA_PREFIX       = config['django']['SITE_MEDIA_PREFIX']
SERVE_STATIC            = config['django']['SERVE_STATIC']
LOGIN_URL               = config['django']['LOGIN_URL']

# section pyonenetweb
logfileweb              = config['pyonenetweb']['logfile']
errfileweb              = config['pyonenetweb']['errfile']
lockfileweb             = config['pyonenetweb']['lockfile']
userweb                 = config['pyonenetweb']['user']
groupweb                = config['pyonenetweb']['group']
port                    = config['pyonenetweb']['port']


# section database
DATABASE_USER     = config['database']['DATABASE_USER']
DATABASE_PASSWORD = config['database']['DATABASE_PASSWORD']
DATABASE_HOST     = config['database']['DATABASE_HOST']
DATABASE_PORT     = config['database']['DATABASE_PORT']
DATABASE_ENGINE   = config['database']['DATABASE_ENGINE']
DATABASE_NAME     = config['database']['DATABASE_NAME']

if (DATABASE_ENGINE == "mysql"):
    # alternative SETTINGS starting from django 1.2
    # addend Isolation level
    # changed from autoradio where works
    #        'OPTIONS': {"init_command": "SET SESSION TRANSACTION ISOLATION LEVEL SERIALIZABLE"},
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.'+DATABASE_ENGINE,
            'OPTIONS': {'init_command': 'SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED',
                        'connect_timeout':60}, 
            'NAME':    DATABASE_NAME,
            'USER':    DATABASE_USER,
            'PASSWORD':DATABASE_PASSWORD,
            'HOST':    DATABASE_HOST,
            'PORT':    DATABASE_PORT,
            }
        }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.'+DATABASE_ENGINE,
            'NAME':    DATABASE_NAME,
            'USER':    DATABASE_USER,
            'PASSWORD':DATABASE_PASSWORD,
            'HOST':    DATABASE_HOST,
            'PORT':    DATABASE_PORT,
            }
        }


USE_TZ=False


TEMPLATES= [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS'  : [],
        'APP_DIRS' : True,
        'OPTIONS': {
            # List of callables that know how to import templates from various sources.
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
#                'django.core.context_processors.request',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
            'debug' : config['django']['TEMPLATE_DEBUG']
        }
    }
]



MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.admindocs.middleware.XViewMiddleware',
#    'django.middleware.transaction.TransactionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'pyonenet.urls'

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.admin',
    'django.contrib.staticfiles',
    'pyonenet.onenet',
    'pyonenet.oncron',
]


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'loggers': {
        'django.db.backends': {
            'level': 'INFO',
            'propagate': True
            },
#        'django': {
#            'level': 'DEBUG',
#            'propagate': True
#            },
        }
    }

ALLOWED_HOSTS = ["*"]

# if you have extension installed on your system you can add this lines
# so you can have an image of your DB

#import platform
#platform=platform.system()
#
#if platform == "Linux":
#    INSTALLED_APPS.append('django_extensions')
