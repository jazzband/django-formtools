"""
This is a URLconf to be loaded by tests.py. Add any URLs needed for tests only.
"""

from django.urls import path

from .forms import TestForm
from .tests import TestFormPreview

urlpatterns = [
    path('preview/', TestFormPreview(TestForm)),
]
