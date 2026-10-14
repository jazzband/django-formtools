================================
Contributing to django-formtools
================================

django-formtools is a `Django Commons <https://github.com/django-commons>`_
project. By contributing you agree to abide by the `Code of Conduct
<https://github.com/django-commons/django-formtools/CODE_OF_CONDUCT.md>`_.

Bugs and feature requests are tracked in the `GitHub issues
<https://github.com/django-commons/django-formtools/issues>`_.

Development setup
-----------------

Clone the repository and install the package in editable mode, together with
the test requirements, in a virtual environment::

    $ git clone https://github.com/django-commons/django-formtools
    $ cd django-formtools
    $ python -m venv .venv
    $ source .venv/bin/activate
    $ pip install -e . -r tests/requirements.txt

Then install the `pre-commit <https://pre-commit.com>`_ hooks::

    $ pip install pre-commit
    $ pre-commit install

Running the tests
-----------------

To run the tests against the current environment, use::

    $ make test

This runs ruff and isort, then the test suite (deprecation warnings are turned
into errors) and prints a coverage report.

To run the tests against all supported combinations of Python (if available)
and Django versions, `install Tox`__ and run it in the root directory::

    $ tox

To see the full list of combinations use the ``-l`` option::

    $ tox -l
    ...
    py312-django52
    py312-djangomain

You can run each environment with the ``-e`` option::

    $ tox -e py312-django52  # runs the tests only on Python 3.12 and Django 5.2.x

__ https://tox.wiki/en/latest/installation.html

Code style
----------

The code is checked with `ruff <https://docs.astral.sh/ruff/>`_ and
`isort <https://pycqa.github.io/isort/>`_ (configured in ``pyproject.toml``),
and the pre-commit hooks also run codespell and validate ``pyproject.toml``.
Before pushing, run::

    $ pre-commit run --all-files

Documentation
-------------

The documentation lives in the ``docs/`` directory and is written with
`Sphinx <https://www.sphinx-doc.org>`_. To build it locally::

    $ pip install sphinx -r docs/requirements.txt
    $ make docs

The documentation is published on `Read the Docs
<https://django-formtools.readthedocs.io/>`_, which fails the build on any
Sphinx warning.

Translations
------------

Translations are managed on `Transifex
<https://app.transifex.com/django/django-formtools/>`_. Please contribute
translations there rather than editing the ``.po`` files directly: they are
overwritten when maintainers pull translations with ``make translations``.

Pull requests
-------------

- Create a branch from ``master``.
- Keep each pull request focused on a single change.
- Add or update tests covering the change.
- Add an entry to the "Unreleased" section of ``docs/changelog.rst``.

Releasing
---------

For maintainers:

1. Set the release version and date in ``docs/changelog.rst`` and commit.
2. Tag the commit with the version number (e.g. ``2.6``) and push the tag::

       $ git tag 2.6
       $ git push origin 2.6

The version number is derived from the tag by ``setuptools_scm``, and GitHub
Actions builds the package and publishes it to PyPI.
