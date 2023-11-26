import json

from .base import BaseStorage


class CookieStorage(BaseStorage):
    encoder = json.JSONEncoder(separators=(',', ':'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = self.load_data()
        if self.data is None:
            self.init_data()

    def load_data(self):
        data = self.request.get_signed_cookie(self.prefix, default=None)
        if data is None:
            return None
        return json.loads(data, cls=json.JSONDecoder)

    def update_response(self, response):
        super().update_response(response)
        if self.data:
            response.set_signed_cookie(self.prefix,
                                       self.encoder.encode(self.data))
        else:
            response.delete_cookie(self.prefix)
