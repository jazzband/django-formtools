============
Form preview
============

.. module:: formtools.preview
    :synopsis: Displays an HTML form, forces a preview, then does something
               with the submission.

Django comes with an optional "form preview" application that helps automate
the following workflow:

    "Display an HTML form, force a preview,
    then do something with the submission."

To force a preview of a form submission, all you have to do is write a short
Python class.

.. note::
    Form preview doesn't work with file uploads.

Overview
=========

Given a :class:`~django.forms.Form` subclass that you define, this
application takes care of the following workflow:

1. Displays the form as HTML on a Web page.

2. Validates the form data when it's submitted via POST.
   a. If it's valid, displays a preview page.
   b. If it's not valid, redisplays the form with error messages.

3. When the "confirmation" form is submitted from the preview page, calls
   a hook that you define -- a :meth:`~FormPreview.done()` method that
   gets passed the valid data.

The framework enforces the required preview by passing a shared-secret hash to
the preview page via hidden form fields. If somebody tweaks the form parameters
on the preview page, the form submission will fail the hash-comparison test.

How to use ``FormPreview``
==========================

1. Point Django at the default FormPreview templates. There are two ways to
   do this:

   * Add ``'formtools'`` to your
     :setting:`INSTALLED_APPS` setting.

     This will work if your :setting:`TEMPLATES` setting includes the
     ``app_directories`` template loader (which is the case by default).

     See the :ref:`template loader docs <template-loaders>` for more.

   * Otherwise, determine the full filesystem path to the
     :file:`formtools/templates` directory and add that directory to your
     :setting:`DIRS <TEMPLATES-DIRS>` option in the :setting:`TEMPLATES`
     setting.

2. Create a :class:`~FormPreview` subclass that
   overrides the ``done()`` method::

       from django.http import HttpResponseRedirect

       from formtools.preview import FormPreview
       from myapp.models import SomeModel

       class SomeModelFormPreview(FormPreview):

           def done(self, request, cleaned_data):
               # Do something with the cleaned_data, then redirect
               # to a "success" page.
               return HttpResponseRedirect('/form/success')

   This method takes an :class:`~django.http.HttpRequest` object and a
   dictionary of the form data after it has been validated and cleaned.
   It should return an :class:`~django.http.HttpResponseRedirect` that
   is the end result of the form being submitted.

3. Change your URLconf to point to an instance of your
   :class:`~FormPreview` subclass::

       from django import forms

       from myapp.forms import SomeModelForm
       from myapp.preview import SomeModelFormPreview

   ...and add the following line to the appropriate model in your URLconf::

       path('post/', SomeModelFormPreview(SomeModelForm)),

   where ``SomeModelForm`` is a Form or ModelForm class for the model.

4. Run the Django server and visit :file:`/post/` in your browser.

``FormPreview`` classes
=======================

.. class:: FormPreview

A :class:`~FormPreview` class is a simple Python class
that represents the preview workflow.
:class:`~FormPreview` classes must subclass
``FormPreview`` and override the ``done()``
method. They can live anywhere in your codebase.

``FormPreview`` templates
=========================

.. attribute:: FormPreview.form_template
.. attribute:: FormPreview.preview_template

By default, the form is rendered via the template :file:`formtools/form.html`,
and the preview page is rendered via the template :file:`formtools/preview.html`.

These values can be overridden for a particular form preview by setting
:attr:`~FormPreview.preview_template` and
:attr:`~FormPreview.form_template` attributes on the
FormPreview subclass. See :file:`formtools/templates` for the default templates.

Required methods
================

.. automethod:: FormPreview.done

Optional methods
================

.. automethod:: FormPreview.get_auto_id

.. automethod:: FormPreview.get_initial

.. automethod:: FormPreview.get_context

.. automethod:: FormPreview.parse_params

.. automethod:: FormPreview.process_preview

.. automethod:: FormPreview.security_hash

.. automethod:: FormPreview.failed_hash
