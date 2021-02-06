import django
from pkg_resources import DistributionNotFound, get_distribution

try:
    __version__ = get_distribution("django-formtools").version
except DistributionNotFound:
    # package is not installed
    __version__ = None

if django.VERSION <= (3, 2):
    default_app_config = 'formtools.apps.FormToolsConfig'
