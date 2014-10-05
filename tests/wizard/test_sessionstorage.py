from django.test import TestCase

from django.contrib.auth.tests.utils import skipIfCustomUser
from formtools.wizard.storage.session import SessionStorage

from .storage import TestStorage


@skipIfCustomUser
class TestSessionStorage(TestStorage, TestCase):
    def get_storage(self):
        return SessionStorage
