"""
This is a URLconf to be loaded by tests.py. Add any URLs needed for tests only.
"""

from django.conf.urls import url

from .tests import TestFormPreview
from .forms import TestForm


urlpatterns = [
    url(r'^preview/', TestFormPreview(TestForm)),
]
