====================
The "form tools" app
====================

.. module:: formtools
    :synopsis: A set of high-level abstractions for Django forms
               (:mod:`django.forms`)..

django-formtools is a collection of assorted utilities that are useful for
specific form use cases.

Currently there are two tools: a helper for form previews and a form wizard
view.

.. toctree::

   preview
   wizard
   changelog

Installation
============

To install django-formtools use your favorite packaging tool, e.g.pip::

    pip install django-formtools

Or download the source distribution from PyPI_ at
https://pypi.python.org/pypi/django-formtools, decompress the file and
run ``python setup.py install`` in the unpacked directory.

Then add ``'formtools'`` to your :setting:`INSTALLED_APPS` setting::

    INSTALLED_APPS = (
        # ...
        'formtools',
    )

.. note::

  Adding ``'formtools'`` to your ``INSTALLED_APPS`` setting is required
  for translations and templates to work. Using django-formtools without
  adding it to your ``INSTALLED_APPS`` setting is not recommended.

.. _PyPI: https://pypi.python.org/

Internationalization
====================

Formtools has its own catalog of translations, in the directory
``formtools/locale``, and it's not loaded automatically like Django's
general catalog in ``django/conf/locale``. If you want formtools's
texts to be translated, like the templates, you must include
:mod:`formtools` in the :setting:`INSTALLED_APPS` setting, so
the internationalization system can find the catalog, as explained in
:ref:`django:how-django-discovers-translations`.

Releases
========

New releases of django-formtools should always be compatible with the latest
stable release of Django. If a new version of Django contains backwards
incompatible changes that affect formtools, a new release of formtools will
be issued shortly after the release of the new Django version.
Version numbers follow the appropriate Python standards, e.g. PEPs 386_ and
440_.

.. _386: http://www.python.org/dev/peps/pep-0386/
.. _440: http://www.python.org/dev/peps/pep-0440/

How to migrate
==============

If you've used the old ``django.contrib.formtools`` package follow these
two easy steps to update your code:

1. Install the third-party ``django-formtools`` package.

2. Change your app's import statements to reference the new packages.

   For example, change this::

       from django.contrib.formtools.wizard.views import WizardView

   ...to this::

       from formtools.wizard.views import WizardView

The code in the new package is the same (it was copied directly from Django),
so you don't have to worry about backwards compatibility in terms of
functionality. Only the imports have changed.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
