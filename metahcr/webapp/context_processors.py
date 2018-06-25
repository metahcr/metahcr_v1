__author__ = 'pcmarks'

"""
TODO: Incomplete

Provide support for handling multiple databases.

This function is part of the definition of TEMPLATE_CONTEXT_PROCESSORS in settings.py

"""
def database_settings(request):
    from django.conf import settings
    return {'database': settings.DATABASES}