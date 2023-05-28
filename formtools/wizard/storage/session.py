from .base import BaseStorage


class SessionStorage(BaseStorage):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.prefix not in self.request.session:
            self.init_data()

    def _get_data(self):
        self.request.session.modified = True
        return self.request.session[self.prefix]

    def _set_data(self, value):
        self.request.session[self.prefix] = value
        self.request.session.modified = True

    data = property(_get_data, _set_data)

    def reset(self):
        # Handle the possibility that the session data has already been
        # deleted by the Django application (e.g. an explicit session flush,
        # or django.contrib.auth.logout()), in which case there is no
        # need to delete any session data.
        try:
            super(SessionStorage, self).reset()
        except KeyError:  # KeyError: session data already deleted.
            self.init_data()
