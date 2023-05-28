from django.test import TestCase

from formtools.wizard.storage.session import SessionStorage

from .storage import TestStorage, get_request


class TestSessionStorage(TestStorage, TestCase):
    def get_storage(self):
        return SessionStorage

    def test_reset_when_session_data_is_already_deleted(self):
        request = get_request()
        storage = self.get_storage()('wizard1', request)
        request.session.flush()
        storage.reset()
