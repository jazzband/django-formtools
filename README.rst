================
django-formtools
================

.. image:: https://jazzband.co/static/img/badge.svg
    :alt: Jazzband
    :target: https://jazzband.co/

.. image:: https://img.shields.io/pypi/v/django-formtools.svg
    :alt: PyPI version
    :target: https://pypi.org/project/django-formtools/

.. image:: https://img.shields.io/pypi/pyversions/django-formtools.svg
    :alt: Supported Python versions
    :target: https://pypi.org/project/django-formtools/

.. image:: https://github.com/jazzband/django-formtools/workflows/Test/badge.svg
   :target: https://github.com/jazzband/django-formtools/actions
   :alt: GitHub Actions

.. image:: https://codecov.io/gh/jazzband/django-formtools/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/jazzband/django-formtools
   :alt: Test Coverage

Django's "formtools" is a set of high-level abstractions for Django forms.
Currently for form previews and multi-step forms.

This code used to live in Django proper -- in ``django.contrib.formtools``
-- but was separated into a standalone package in Django 1.8 to keep the
framework's core clean.

For a full list of available formtools, see
https://django-formtools.readthedocs.io/

django-formtools can also be found on and installed from the Python
Package Index: https://pypi.python.org/pypi/django-formtools

To get more help:

* Join the #django channel on irc.libera.chat. Lots of helpful people hang out
  there.

* Join the django-users mailing list, or read the archives, at
  https://groups.google.com/group/django-users.

Contributing to django-formtools
--------------------------------

See ``CONTRIBUTING.rst`` for information about contributing patches to
``django-formtools``.

Running tests is as simple as `installing Tox`__ and running it in the root
Git clone directory::

    $ git clone https://github.com/jazzband/django-formtools
    [..]
    $ cd django-formtools
    $ tox
    [..]
      congratulations :)

The previous command will run the tests in different combinations of Python
(if available) and Django versions. To see the full list of combinations use
the ``-l`` option::

    $ tox -l
    ...
    py310-djangoAB
    py310-djangomain

You can run each environment with the ``-e`` option::

    $ tox -e py310-djangoAB  # runs the tests only on Python 3.10 and Django A.B.x

__ https://tox.readthedocs.io/en/latest/install.html
