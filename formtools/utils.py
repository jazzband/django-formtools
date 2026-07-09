import pickle

from django.core.files.uploadedfile import TemporaryUploadedFile
from django.db.models import QuerySet
from django.utils.crypto import salted_hmac


def sanitise(obj):
    if isinstance(obj, list):
        return [sanitise(o) for o in obj]
    elif isinstance(obj, tuple):
        return tuple([sanitise(o) for o in obj])
    elif isinstance(obj, QuerySet):
        return [sanitise(o) for o in list(obj)]
    try:
        od = obj.__dict__
        nd = {'_class': obj.__class__}
        for key, val in od.items():
            if not key.startswith('_'):
                # ignore Django internal attributes
                nd[key] = sanitise(val)
        return nd
    except Exception:
        pass
    return obj


def form_hmac(form):
    """
    Calculates a security hash for the given Form instance.
    """
    data = []
    for bf in form:
        # Get the value from the form data. If the form allows empty or hasn't
        # changed then don't call clean() to avoid trigger validation errors.
        if form.empty_permitted and not form.has_changed():  # noqa: SIM108
            value = bf.data or ''
        else:
            value = bf.field.clean(bf.data) or ''
        if isinstance(value, str):
            value = value.strip()
        elif isinstance(value, TemporaryUploadedFile):
            value = value.read()
        data.append((bf.name, value))

    sanitised_data = sanitise(data)
    pickled = pickle.dumps(sanitised_data, pickle.HIGHEST_PROTOCOL)
    key_salt = 'django.contrib.formtools'
    return salted_hmac(key_salt, pickled).hexdigest()
