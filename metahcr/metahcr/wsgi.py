"""
WSGI config for metahcr project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/
"""

# The following paragraph is copied from bitnami's AWS django 1.7.10 instance Project example application
import os, sys
sys.path.append('/opt/bitnami/apps/django/django_projects/metahcr')
os.environ.setdefault("PYTHON_EGG_CACHE", "/opt/bitnami/apps/django/django_projects/metahcr/egg_cache")


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "metahcr.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
