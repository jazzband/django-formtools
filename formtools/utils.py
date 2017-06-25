from __future__ import unicode_literals

# Do not try cPickle here (see #18340)
import pickle

from django.db.models import QuerySet
from django.utils import six
from django.utils.crypto import salted_hmac


def sanitise(obj):
    if type(obj) == list:
        return [sanitise(o) for o in obj]
    elif type(obj) == tuple:
        return tuple([sanitise(o) for o in obj])
    elif type(obj) == QuerySet:
        return [sanitise(o) for o in list(obj)]
    try:
        od = obj.__dict__
        print(obj.__class__)
        nd = {'_class': obj.__class__}
        # this is a django object, ignore all _ fields
        for key, val in od.items():
            if not key.startswith('_'):
                nd[key] = sanitise(val)
        return nd
    except:
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
        if form.empty_permitted and not form.has_changed():
            value = bf.data or ''
        else:
            value = bf.field.clean(bf.data) or ''
        if isinstance(value, six.string_types):
            value = value.strip()
        data.append((bf.name, value))

    sandata = sanitise(data)
    pickled = pickle.dumps(sandata, pickle.HIGHEST_PROTOCOL)
    key_salt = 'django.contrib.formtools'
    return salted_hmac(key_salt, pickled).hexdigest()
