import django

__version__ = '2.2'

if django.VERSION <= (3, 2):
    default_app_config = 'formtools.apps.FormToolsConfig'
