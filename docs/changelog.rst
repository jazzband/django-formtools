Changelog
=========

This page details the changes in the various ``django-formtools`` releases.

2.3 (2021-04-18)
----------------

- Dropped testing for Django 1.11, 2.0 and 2.1.

- Added support for Django 3.1 and Python 3.9.

- Added support for Django 3.2.

- Dropped support for Django 3.0.

- Dropped support for Python 3.5.

2.2 (2019-12-05)
----------------

- Dropped testing for Django 1.8, 1.9, 1.10.

- Dropped support for Python 2.

- Added support for Django 2.1, 2.2, 3.0, and Python 3.7.

- Updated translations from Transifex.

2.1 (2017-10-04)
----------------

- Added testing for Django 1.11 (no code changes were required).

- Added support for Django 2.0.

- Dropped testing for Python 3.3 (now end-of-life) on Django 1.8.

2.0 (2017-01-07)
----------------

- Added the ``request`` parameter to :meth:`FormPreview.parse_params()
  <formtools.preview.FormPreview.parse_params>`.

- Added support for Django 1.10.

- Dropped support for Django 1.7 and Python 3.2 on Django 1.8.

1.0 (2015-03-25)
----------------

- Added the ``request`` parameter to :meth:`WizardView.get_prefix()
  <formtools.wizard.views.WizardView.get_prefix>`.

  This was originally reported and fixed in the main Django repository:

    https://code.djangoproject.com/ticket/19981

- A :doc:`form wizard </wizard>` using the
  :class:`~formtools.wizard.views.CookieWizardView` will now ignore an invalid
  cookie, and the wizard will restart from the first step. An invalid cookie
  can occur in cases of intentional manipulation, but also after a secret key
  change. Previously, this would raise ``WizardViewCookieModified``, a
  ``SuspiciousOperation``, causing an exception for any user with an invalid
  cookie upon every request to the wizard, until the cookie is removed.

  This was originally reported and fixed in the main Django repository:

    https://code.djangoproject.com/ticket/22638

- Added missing form element to default wizard form template
  ``formtools/wizard/wizard_form.html``.
