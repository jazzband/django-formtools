"""
This is a URLconf to be loaded by tests.py. Add any URLs needed for tests only.
"""

from django.conf.urls import url

from .forms import TestForm
from .tests import TestFormPreview

urlpatterns = [
    url(r'^preview/', TestFormPreview(TestForm)),
]
