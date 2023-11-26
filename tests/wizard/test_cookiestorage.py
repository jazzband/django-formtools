from django.core import signing
from django.http import HttpResponse
from django.test import TestCase

from formtools.wizard.storage.cookie import CookieStorage

from .storage import TestStorage, get_request


class TestCookieStorage(TestStorage, TestCase):
    def get_storage(self):
        return CookieStorage

    def test_manipulated_cookie(self):
        request = get_request()
        storage = self.get_storage()('wizard1', request, None)

        cookie_signer = signing.get_cookie_signer(storage.prefix)

        storage.request.COOKIES[storage.prefix] = cookie_signer.sign(
            storage.encoder.encode({'key1': 'value1'})
        )

        self.assertEqual(storage.load_data(), {'key1': 'value1'})

        storage.request.COOKIES[storage.prefix] = 'i_am_manipulated'
        self.assertIsNone(storage.load_data())

    def test_reset_cookie(self):
        request = get_request()
        storage = self.get_storage()('wizard1', request, None)

        storage.data = {'key1': 'value1'}

        response = HttpResponse()
        storage.update_response(response)

        cookie_signer = signing.get_cookie_signer(storage.prefix)
        signed_cookie_data = cookie_signer.sign(storage.encoder.encode(storage.data))
        self.assertEqual(response.cookies[storage.prefix].value, signed_cookie_data)

        storage.init_data()
        storage.update_response(response)
        unsigned_cookie_data = cookie_signer.unsign(response.cookies[storage.prefix].value)
        self.assertJSONEqual(
            unsigned_cookie_data,
            {"step_files": {}, "step": None, "extra_data": {}, "step_data": {}}
        )
