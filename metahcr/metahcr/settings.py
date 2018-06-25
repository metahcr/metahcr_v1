"""
 Copyright (C) 2018 Shell Global Solutions International B.V.
"""

# This applications location
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Application settings

VIEW_STYLE = 'public'

# This list determines the legal category values for attributes. The list will appear as a dropdown
# field in Attribute maintenance.
# Note that the first entry in the pair is the value used in the database and the second
# element is for display purposes.
# KEEP THIS LIST UPDATED!!
CATEGORY_CHOICES = [
    ('all', 'all',),
    ('biological_analysis', 'biological analysis',),
    ('hydrocarbon_resource', 'hydrocarbon resource',),
    ('organism', 'organism',),
    ('investigation', 'investigation',),
    ('sample', 'sample',),
    ('sequencing', 'sequencing',),
    ('single_gene_analysis', 'single gene analysis'),
    ('metagenome_analysis', 'metagenome analysis'),
    ]

PARAMETERS = {
    'ncbi_sra_url': "http://www.ncbi.nlm.nih.gov/Traces/sra/sra.cgi?study=",
    'gold_card_url': "http://genomesonline.org/cgi-bin/GOLD/bin/GOLDCards.cgi?goldstamp=",
    'pubmed_url': "http://www.ncbi.nlm.nih.gov/pubmed?term=",
    'google_maps_api_key': "ABQIAAAA1TyLSx92G_fVhECJR9we5RT2yXp_ZAY8_ufC3CFXhHIE1NvwkxQbrOL2SFl9yfFRds9q7K3C4zWWOQ",
    'ncbi_taxonomy_url': "http://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?id="
}

# The email address that is to be used when making Entrez requests, e.g., getting Taxonomic data for an organism.
ENTREZ_EMAIL = ''

LOGIN_URL = '/login'

# Django settings for the metahcr project.

DEBUG = True

TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Peter C. Marks', 'retepskram@aol.com'),
)

ENTITY_MANAGERS = [
    {'name': 'metahcr_public_v34', 'connection': 'metahcr_public_v34'},
    ]
MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'metahcr_public_v34',                      # Or path to database file if using sqlite3.
        'USER': 'metahcradmin',
        'PASSWORD': 'user01',
        'HOST': 'localhost',      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '5432',                      # Set to empty string for default.
    },
}


# Amazon S3 storage of uploaded files
#TODO: Move AWS_ values to enivronment variables

AWS_ACCESS_KEY_ID = 'setme'
AWS_SECRET_ACCESS_KEY = 'setme'
AWS_STORAGE_BUCKET_NAME =  'webappuploadstest'

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['*']

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/New_York'

# Setting this to true to stop runtime "received a naive datetime" message- Basically
# ignoring time zones for now?
# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = '/tmp'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # "C:/Users/pcmarks/IdeaProjects/metahcr_v3/metahcr/static",
   os.path.join(BASE_DIR, "static"),
    #    "/Users/pcmarks/Documents/IdeaProjects/metahcr/admin",
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    #    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '7t*k@#z4r&c52o(b=(zcj2p)7#0^$o5k_i8bd@(9*hv#%!^#g4'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    ('django.template.loaders.cached.Loader',(
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
        #     'django.template.loaders.eggs.Loader',
    )),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.debug',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.core.context_processors.request',
    'webapp.context_processors.database_settings',     # TODO: Incomplete
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Uncomment the next line to use the Django Debugger
    # 'debug_toolbar.middleware.DebugToolbarMiddleware',
)

ROOT_URLCONF = 'metahcr.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'metahcr.wsgi.application'

import os
TEMPLATE_DIRS = (os.path.join(os.path.dirname(__file__), '..', 'templates').replace('\\', '/'),)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'webapp',
    # Uncomment the next line to use the Django Debugger
    # 'debug_toolbar',
    # 'south',
)

# This was added to suppress warnings when this app moved from django 1.6 to django 1.7
TEST_RUNNER = 'django.test.simple.DjangoTestSuiteRunner'

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
            },
        }
}
