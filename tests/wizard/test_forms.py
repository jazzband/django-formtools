import unittest
from collections import OrderedDict
from importlib import import_module
from unittest.mock import patch

from django import forms, http
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.forms import formset_factory
from django.template.response import TemplateResponse
from django.test import TestCase

from formtools.wizard.storage import NoFileStorageConfigured
from formtools.wizard.storage.cookie import CookieStorage
from formtools.wizard.storage.session import SessionStorage
from formtools.wizard.views import (
    CookieWizardView, SessionWizardView, WizardView,
)


class DummyRequest(http.HttpRequest):
    def __init__(self, POST=None):
        super().__init__()
        self.method = "POST" if POST else "GET"
        if POST is not None:
            self.POST.update(POST)
        self.session = {}
        self._dont_enforce_csrf_checks = True


def get_request(*args, **kwargs):
    request = DummyRequest(*args, **kwargs)
    engine = import_module(settings.SESSION_ENGINE)
    request.session = engine.SessionStore(None)
    return request


class Step1(forms.Form):
    name = forms.CharField()


class Step2(forms.Form):
    name = forms.CharField()


class Step3(forms.Form):
    data = forms.CharField()


class FormWithFileField(forms.Form):
    upload = forms.FileField()


Step3FormSet = formset_factory(Step3)


class CustomKwargsStep1(Step1):
    def __init__(self, test=None, *args, **kwargs):
        self.test = test
        super().__init__(*args, **kwargs)


class TestModel(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        app_label = 'formtools'


class TestModelForm(forms.ModelForm):
    class Meta:
        model = TestModel
        fields = '__all__'


TestModelFormSet = forms.models.modelformset_factory(TestModel, form=TestModelForm, extra=2, fields='__all__')


class TestWizard(WizardView):
    storage_name = 'formtools.wizard.storage.session.SessionStorage'

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        return response, self

    def get_form_kwargs(self, step, *args, **kwargs):
        kwargs = super().get_form_kwargs(step, *args, **kwargs)
        if step == 'kwargs_test':
            kwargs['test'] = True
        return kwargs


test_instance = User()


class TestWizardWithInitAttrs(TestWizard):
    form_list = [Step1, Step2]
    condition_dict = {'step2': False}
    initial_dict = {'start': {'name': 'value1'}}
    instance_dict = {'start': test_instance}


class TestWizardWithCustomGetFormList(TestWizard):

    form_list = [Step1]

    def get_form_list(self):
        return {'start': Step1, 'step2': Step2}


class FormTests(TestCase):
    def test_init(self):
        request = get_request()
        testform = TestWizard.as_view([Step1, Step2])
        response, instance = testform(request)
        self.assertIsInstance(response, TemplateResponse)
        context = response.context_data
        self.assertEqual(set(context.keys()), {'form', 'view', 'wizard'})
        self.assertIsInstance(context['form'], Step1)
        self.assertIsInstance(context['view'], TestWizard)
        self.assertEqual(
            set(context['wizard'].keys()),
            {'form', 'steps', 'management_form'},
        )
        self.assertIsInstance(instance.storage, SessionStorage)

    def test_form_init(self):
        # get_initkwargs() is used by as_view() to build kwargs
        with patch.object(TestWizard, 'get_initkwargs') as mock:
            TestWizard.as_view()
            mock.assert_called_once()

        # just forms: automatic step names are generated
        kwargs = TestWizard.get_initkwargs([Step1, Step2])
        self.assertEqual(kwargs['form_list'], {'0': Step1, '1': Step2})
        self.assertEqual(kwargs['initial_dict'], {})
        self.assertEqual(kwargs['instance_dict'], {})
        self.assertEqual(kwargs['condition_dict'], {})

        # tuples with step names; optional initial_dict, instance_dict & condition_dict
        kwargs = TestWizard.get_initkwargs(
            [('start', Step1), ('step2', Step2)],
            initial_dict={'start': {'name': 'value1'}},
            instance_dict={'start': test_instance},
            condition_dict={'step2': False},
        )
        self.assertEqual(kwargs['form_list'], {'start': Step1, 'step2': Step2})
        self.assertEqual(kwargs['initial_dict'], {'start': {'name': 'value1'}})
        self.assertEqual(kwargs['instance_dict'], {'start': test_instance})
        self.assertEqual(kwargs['condition_dict'], {'step2': False})

        # forms and formsets work; name tuples optional and can be mixed with just forms
        kwargs = TestWizard.get_initkwargs([Step1, Step2, ('finish', Step3FormSet)])
        self.assertEqual(
            kwargs['form_list'],
            {'0': Step1, '1': Step2, 'finish': Step3FormSet}
        )
        self.assertEqual(kwargs['initial_dict'], {})
        self.assertEqual(kwargs['instance_dict'], {})
        self.assertEqual(kwargs['condition_dict'], {})

        # all kwargs are defined on the class
        kwargs = TestWizardWithInitAttrs.get_initkwargs()
        self.assertEqual(kwargs['form_list'], {'0': Step1, '1': Step2})
        self.assertEqual(kwargs['initial_dict'], {'start': {'name': 'value1'}})
        self.assertEqual(kwargs['instance_dict'], {'start': test_instance})
        self.assertEqual(kwargs['condition_dict'], {'step2': False})

        # FileFields require additional storage in subclass of WizardView
        with self.assertRaises(NoFileStorageConfigured) as cm:
            TestWizard.get_initkwargs([FormWithFileField])
        self.assertEqual(
            str(cm.exception),
            "You need to define 'file_storage' in your wizard view in order to "
            "handle file uploads."
        )

    def test_first_step(self):
        request = get_request()
        testform = TestWizard.as_view([Step1, Step2])
        response, instance = testform(request)
        self.assertEqual(instance.steps.current, '0')

        testform = TestWizard.as_view([('start', Step1), ('step2', Step2)])
        response, instance = testform(request)
        self.assertEqual(instance.steps.current, 'start')

    def test_persistence(self):
        testform = TestWizard.as_view([('start', Step1), ('step2', Step2)])
        request = get_request({'test_wizard-current_step': 'start', 'name': 'data1'})
        response, instance = testform(request)
        self.assertEqual(instance.steps.current, 'start')

        instance.storage.current_step = 'step2'

        testform2 = TestWizard.as_view([('start', Step1), ('step2', Step2)])
        request.POST = {'test_wizard-current_step': 'step2'}
        response, instance = testform2(request)
        self.assertEqual(instance.steps.current, 'step2')

    def test_form_condition(self):
        request = get_request()
        testform = TestWizard.as_view(
            [('start', Step1), ('step2', Step2), ('step3', Step3)],
            condition_dict={'step2': True}
        )
        response, instance = testform(request)
        self.assertEqual(instance.get_next_step(), 'step2')

        testform = TestWizard.as_view(
            [('start', Step1), ('step2', Step2), ('step3', Step3)],
            condition_dict={'step2': False}
        )
        response, instance = testform(request)
        self.assertEqual(instance.get_next_step(), 'step3')

        testform = TestWizardWithInitAttrs.as_view(
            [('start', Step1), ('step2', Step2), ('step3', Step3)]
        )
        response, instance = testform(request)
        self.assertEqual(instance.get_next_step(), 'step3')

    @unittest.skip('https://github.com/jazzband/django-formtools/issues/220')
    def test_form_condition_callable(self):
        def step2_is_enabled(wizard):
            cleaned_data = wizard.get_cleaned_data_for_step('start')
            if cleaned_data:
                return cleaned_data.get('name') == 'yes'

        testform = TestWizard.as_view(
            [('start', Step1), ('step2', Step2), ('step3', Step3)],
            condition_dict={'step2': step2_is_enabled}
        )
        request = get_request({'test_wizard-current_step': 'step1', 'start-name': 'yes'})
        response, instance = testform(request)
        # being on step2 when giving name "yes"
        self.assertEqual(instance.get_prev_step(), 'start')
        self.assertEqual(instance.steps.current, 'step2')
        self.assertEqual(instance.get_next_step(), 'step3')
        self.assertEqual(instance.get_step_index(), 1)

        request = get_request({'test_wizard-current_step': 'start', 'start-name': 'no'})
        response, instance = testform(request)
        # step2 being skipped and no more steps to go when giving name "no"
        self.assertEqual(instance.get_prev_step(), 'start')
        self.assertEqual(instance.steps.current, 'step3')
        self.assertEqual(instance.get_next_step(), None)
        # index is still 1, because step2 is not in list returned by get_form_list()
        self.assertEqual(instance.get_step_index(), 1)

    def test_form_condition_unstable(self):
        request = get_request()
        testform = TestWizard.as_view(
            [('start', Step1), ('step2', Step2), ('step3', Step3)],
            condition_dict={'step2': True}
        )
        response, instance = testform(request)
        self.assertEqual(instance.get_step_index('step2'), 1)
        self.assertEqual(instance.get_next_step('step2'), 'step3')
        instance.condition_dict['step2'] = False
        self.assertEqual(instance.get_step_index('step2'), None)
        self.assertEqual(instance.get_next_step('step2'), 'start')

    def test_form_kwargs(self):
        request = get_request()
        testform = TestWizard.as_view([
            ('start', Step1),
            ('kwargs_test', CustomKwargsStep1),
        ])
        response, instance = testform(request)
        self.assertEqual(instance.get_form_kwargs('start'), {})
        self.assertEqual(instance.get_form_kwargs('kwargs_test'), {'test': True})
        self.assertEqual(instance.get_form('kwargs_test').test, True)

    def test_form_prefix(self):
        request = get_request()
        testform = TestWizard.as_view([('start', Step1), ('step2', Step2)])
        response, instance = testform(request)
        self.assertEqual(instance.get_form_prefix(), 'start')
        self.assertEqual(instance.get_form_prefix('another'), 'another')

    def test_form_initial(self):
        request = get_request()
        testform = TestWizard.as_view(
            [('start', Step1), ('step2', Step2)],
            initial_dict={'start': {'name': 'value1'}}
        )
        response, instance = testform(request)
        self.assertEqual(instance.get_form_initial('start'), {'name': 'value1'})
        self.assertEqual(instance.get_form_initial('step2'), {})

        testform = TestWizardWithInitAttrs.as_view(
            [('start', Step1), ('step2', Step2)]
        )
        response, instance = testform(request)

        self.assertEqual(instance.get_form_initial('start'), {'name': 'value1'})
        self.assertEqual(instance.get_form_initial('step2'), {})

    def test_form_instance(self):
        # instance_dict can provide instances for forms
        request = get_request()
        model_instance = TestModel(name='test object')
        testform = TestWizard.as_view(
            [('start', TestModelForm), ('step2', Step2)],
            instance_dict={'start': model_instance}
        )
        response, instance = testform(request)
        self.assertEqual(instance.get_form_instance('start'), model_instance)
        self.assertIsNone(instance.get_form_instance('non_exist_instance'))

        # instance_dict defined in class
        testform = TestWizardWithInitAttrs.as_view(
            [('start', TestModelForm), ('step2', Step2)]
        )
        response, instance = testform(request)
        self.assertEqual(instance.get_form_instance('start'), test_instance)
        self.assertIsNone(instance.get_form_instance('non_exist_instance'))

    def test_formset_instance(self):
        # instance_dict can provide querysets for formsets
        request = get_request()
        model_instance1, _ = TestModel.objects.get_or_create(name='test object 1')
        model_instance2, _ = TestModel.objects.get_or_create(name='test object 2')
        testform = TestWizard.as_view(
            [('start', TestModelFormSet), ('step2', Step2)],
            instance_dict={'start': TestModel.objects.all()}
        )
        response, instance = testform(request)
        self.assertEqual(
            list(instance.get_form_instance('start')),
            [model_instance1, model_instance2],
        )
        self.assertIsNone(instance.get_form_instance('non_exist_instance'))
        # number of forms in formset correspond to queryset
        form = instance.get_form()
        self.assertIsInstance(form, TestModelFormSet)
        self.assertEqual(form.initial_form_count(), 2)

    def test_done(self):
        # validate WizardView.done() is not implemented on base class
        request = get_request()
        testform = TestWizard.as_view([('start', Step1), ('step2', Step2)])
        response, instance = testform(request)
        self.assertRaises(NotImplementedError, instance.done, None)

    def test_goto_step_kwargs(self):
        """Any extra kwarg given to render_goto_step is added to response context."""
        request = get_request()
        testform = TestWizard.as_view([('start', Step1), ('step2', Step2)])
        _, instance = testform(request)
        response = instance.render_goto_step('start', context_var='Foo')
        self.assertIn('context_var', response.context_data.keys())

    def test_revalidation(self):
        request = get_request()
        testform = TestWizard.as_view([('start', Step1), ('step2', Step2)])
        response, instance = testform(request)
        instance.render_done(None)
        self.assertEqual(instance.storage.current_step, 'start')

    def test_form_list_type(self):
        # validate WizardView.done() is called with a `list` of forms (not odict_values)
        request = get_request({'test_wizard-current_step': 'start', 'start-name': 'foo'})
        testform = TestWizard.as_view([('start', Step1)])
        with patch.object(TestWizard, 'done') as mock:
            _, _ = testform(request)
        mock.assert_called_once()
        args, kwargs = mock.call_args_list[0]
        self.assertIsInstance(args[0], list)  # form_list
        self.assertIsInstance(kwargs['form_dict'], OrderedDict)

    def test_get_form_list_default(self):
        request = get_request()
        testform = TestWizard.as_view([('start', Step1)])
        response, instance = testform(request)

        form_list = instance.get_form_list()
        self.assertEqual(form_list, {'start': Step1})
        with self.assertRaises(KeyError):
            instance.get_form('step2')

    def test_get_form_list_custom(self):
        request = get_request()
        testform = TestWizardWithCustomGetFormList.as_view([('start', Step1)])
        response, instance = testform(request)

        form_list = instance.get_form_list()
        self.assertEqual(form_list, {'start': Step1, 'step2': Step2})
        self.assertIsInstance(instance.get_form('step2'), Step2)


class SessionFormTests(TestCase):
    def test_init(self):
        request = get_request()
        testform = SessionWizardView.as_view([('start', Step1)])
        response = testform(request)
        self.assertIsInstance(response, TemplateResponse)
        instance = response.context_data['view']
        self.assertIsInstance(instance.storage, SessionStorage)


class CookieFormTests(TestCase):
    def test_init(self):
        request = get_request()
        testform = CookieWizardView.as_view([('start', Step1)])
        response = testform(request)
        self.assertIsInstance(response, TemplateResponse)
        instance = response.context_data['view']
        self.assertIsInstance(instance.storage, CookieStorage)
