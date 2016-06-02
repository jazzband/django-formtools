================================
Contributing to django-formtools
================================

As an open source project, django-formtools welcomes contributions of many
forms, similar to its origin in the Django framework.

Examples of contributions include:

* Code patches
* Documentation improvements
* Bug reports and patch reviews

Extensive contribution guidelines are available online at:

    https://docs.djangoproject.com/en/dev/internals/contributing/

`File a ticket`__ to suggest changes or send pull requests.

django-formtools uses Github's issue system to keep track of bugs, feature
requests, and pull requests for patches.

Running tests is as simple as `installing Tox`__ and running it in the root
Git clone directory::

    $ git clone https://github.com/django/django-formtools
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
    py35-django-AB
    py35-django-master

You can run each environment with the ``-e`` option::

    $ tox -e py35-django-AB  # runs the tests only on Python 3.5 and Django A.B.x

Optionally you can also specify a country whose tests you want to run::

    $ COUNTRY=us tox

And combine both options::

    $ COUNTRY=us tox -e py35-django-AB

__ https://github.com/django/django-formtools/issues
__ https://tox.readthedocs.io/en/latest/install.html
