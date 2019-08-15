import copy

from django import forms
from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.test.client import RequestFactory

from formtools.wizard.views import CookieWizardView

from .forms import temp_storage
from .models import Poem, Poet

UPLOADED_FILE_NAME = 'tests.py'


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = '__all__'


UserFormSet = forms.models.modelformset_factory(User, form=UserForm, extra=2)
PoemFormSet = forms.models.inlineformset_factory(Poet, Poem, fields="__all__")


class WizardTests:

    def setUp(self):
        self.testuser, created = User.objects.get_or_create(username='testuser1')
        # Get new step data, since we modify it during the tests.
        self.wizard_step_data = copy.deepcopy(self.wizard_step_data)
        self.wizard_step_data[0]['form1-user'] = self.testuser.pk

    def tearDown(self):
        # Ensure that there are no files in the storage which could lead to false
        # results in the next tests. Deleting the whole storage dir is not really
        # an option since the storage is defined on the module level and can't be
        # easily reinitialized. (FIXME: The tests here should use the view classes
        # directly instead of the test client, then the storage issues would go
        # away too.)
        for file in temp_storage.listdir('')[1]:
            temp_storage.delete(file)

    def test_initial_call(self):
        response = self.client.get(self.wizard_url)
        wizard = response.context['wizard']
        self.assertEqual(response.status_code, 200)
        self.assertEqual(wizard['steps'].current, 'form1')
        self.assertEqual(wizard['steps'].step0, 0)
        self.assertEqual(wizard['steps'].step1, 1)
        self.assertEqual(wizard['steps'].last, 'form4')
        self.assertEqual(wizard['steps'].prev, None)
        self.assertEqual(wizard['steps'].next, 'form2')
        self.assertEqual(wizard['steps'].count, 4)

    def test_form_post_error(self):
        response = self.client.post(self.wizard_url, self.wizard_step_1_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['wizard']['steps'].current, 'form1')
        self.assertEqual(response.context['wizard']['form'].errors,
                         {'name': ['This field is required.'],
                          'user': ['This field is required.']})

    def test_form_post_mgmt_data_missing(self):
        wizard_step_data = self.wizard_step_data[0].copy()

        # remove management data
        for key in list(wizard_step_data.keys()):
            if "current_step" in key:
                del wizard_step_data[key]

        response = self.client.post(self.wizard_url, wizard_step_data)
        # view should return HTTP 400 Bad Request
        self.assertEqual(response.status_code, 400)

    def test_form_post_success(self):
        response = self.client.post(self.wizard_url, self.wizard_step_data[0])
        wizard = response.context['wizard']
        self.assertEqual(response.status_code, 200)
        self.assertEqual(wizard['steps'].current, 'form2')
        self.assertEqual(wizard['steps'].step0, 1)
        self.assertEqual(wizard['steps'].prev, 'form1')
        self.assertEqual(wizard['steps'].next, 'form3')

    def test_form_stepback(self):
        response = self.client.get(self.wizard_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['wizard']['steps'].current, 'form1')

        response = self.client.post(self.wizard_url, self.wizard_step_data[0])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['wizard']['steps'].current, 'form2')

        response = self.client.post(self.wizard_url, {
            'wizard_goto_step': response.context['wizard']['steps'].prev})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['wizard']['steps'].current, 'form1')

    def test_template_context(self):
        response = self.client.get(self.wizard_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['wizard']['steps'].current, 'form1')
        self.assertEqual(response.context.get('another_var', None), None)

        response = self.client.post(self.wizard_url, self.wizard_step_data[0])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['wizard']['steps'].current, 'form2')
        self.assertEqual(response.context.get('another_var', None), True)

        # ticket #19025: `form` should be included in context
        form = response.context_data['wizard']['form']
        self.assertEqual(response.context_data['form'], form)

    def test_form_finish(self):
        response = self.client.get(self.wizard_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['wizard']['steps'].current, 'form1')

        response = self.client.post(self.wizard_url, self.wizard_step_data[0])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['wizard']['steps'].current, 'form2')

        post_data = self.wizard_step_data[1]
        with open(__file__, 'rb') as post_file:
            post_data['form2-file1'] = post_file
            response = self.client.post(self.wizard_url, post_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['wizard']['steps'].current, 'form3')

        # Check that the file got uploaded properly.
        with open(__file__, 'rb') as f, temp_storage.open(UPLOADED_FILE_NAME) as f2:
            self.assertEqual(f.read(), f2.read())

        response = self.client.post(self.wizard_url, self.wizard_step_data[2])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['wizard']['steps'].current, 'form4')

        response = self.client.post(self.wizard_url, self.wizard_step_data[3])
        self.assertEqual(response.status_code, 200)

        # After the wizard is done no files should exist anymore.
        self.assertFalse(temp_storage.exists(UPLOADED_FILE_NAME))

        all_data = response.context['form_list']
        del all_data[1]['file1']
        self.assertEqual(all_data, [
            {'name': 'Pony', 'thirsty': True, 'user': self.testuser},
            {'address1': '123 Main St', 'address2': 'Djangoland'},
            {'random_crap': 'blah blah'},
            [{'random_crap': 'blah blah'},
             {'random_crap': 'blah blah'}]])

    def test_cleaned_data(self):
        response = self.client.get(self.wizard_url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(self.wizard_url, self.wizard_step_data[0])
        self.assertEqual(response.status_code, 200)

        post_data = self.wizard_step_data[1]
        with open(__file__, 'rb') as post_file:
            post_data['form2-file1'] = post_file
            response = self.client.post(self.wizard_url, post_data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(temp_storage.exists(UPLOADED_FILE_NAME))

        response = self.client.post(self.wizard_url, self.wizard_step_data[2])
        self.assertEqual(response.status_code, 200)

        response = self.client.post(self.wizard_url, self.wizard_step_data[3])
        self.assertEqual(response.status_code, 200)

        all_data = response.context['all_cleaned_data']
        self.assertEqual(all_data['file1'].name, UPLOADED_FILE_NAME)
        self.assertTrue(all_data['file1'].closed)
        self.assertFalse(temp_storage.exists(UPLOADED_FILE_NAME))
        del all_data['file1']
        self.assertEqual(all_data, {
            'name': 'Pony', 'thirsty': True, 'user': self.testuser,
            'address1': '123 Main St', 'address2': 'Djangoland',
            'random_crap': 'blah blah', 'formset-form4': [
                {'random_crap': 'blah blah'},
                {'random_crap': 'blah blah'}]})

    def test_manipulated_data(self):
        response = self.client.get(self.wizard_url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(self.wizard_url, self.wizard_step_data[0])
        self.assertEqual(response.status_code, 200)

        post_data = self.wizard_step_data[1]
        with open(__file__, 'rb') as post_file:
            post_data['form2-file1'] = post_file
            response = self.client.post(self.wizard_url, post_data)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(self.wizard_url, self.wizard_step_data[2])
        self.assertEqual(response.status_code, 200)
        self.client.cookies.pop('sessionid', None)
        self.client.cookies.pop('wizard_cookie_contact_wizard', None)

        response = self.client.post(self.wizard_url, self.wizard_step_data[3])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['wizard']['steps'].current, 'form1')

    def test_form_refresh(self):
        response = self.client.get(self.wizard_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['wizard']['steps'].current, 'form1')

        response = self.client.post(self.wizard_url, self.wizard_step_data[0])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['wizard']['steps'].current, 'form2')

        response = self.client.post(self.wizard_url, self.wizard_step_data[0])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['wizard']['steps'].current, 'form2')

        post_data = self.wizard_step_data[1]
        with open(__file__, 'rb') as post_file:
            post_data['form2-file1'] = post_file
            response = self.client.post(self.wizard_url, post_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['wizard']['steps'].current, 'form3')

        response = self.client.post(self.wizard_url, self.wizard_step_data[2])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['wizard']['steps'].current, 'form4')

        response = self.client.post(self.wizard_url, self.wizard_step_data[0])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['wizard']['steps'].current, 'form2')

        response = self.client.post(self.wizard_url, self.wizard_step_data[3])
        self.assertEqual(response.status_code, 200)


@override_settings(ROOT_URLCONF='tests.wizard.wizardtests.urls')
class SessionWizardTests(WizardTests, TestCase):
    wizard_url = '/wiz_session/'
    wizard_step_1_data = {
        'session_contact_wizard-current_step': 'form1',
    }
    wizard_step_data = (
        {
            'form1-name': 'Pony',
            'form1-thirsty': '2',
            'session_contact_wizard-current_step': 'form1',
        },
        {
            'form2-address1': '123 Main St',
            'form2-address2': 'Djangoland',
            'session_contact_wizard-current_step': 'form2',
        },
        {
            'form3-random_crap': 'blah blah',
            'session_contact_wizard-current_step': 'form3',
        },
        {
            'form4-INITIAL_FORMS': '0',
            'form4-TOTAL_FORMS': '2',
            'form4-MAX_NUM_FORMS': '0',
            'form4-0-random_crap': 'blah blah',
            'form4-1-random_crap': 'blah blah',
            'session_contact_wizard-current_step': 'form4',
        }
    )


@override_settings(ROOT_URLCONF='tests.wizard.wizardtests.urls')
class CookieWizardTests(WizardTests, TestCase):
    wizard_url = '/wiz_cookie/'
    wizard_step_1_data = {
        'cookie_contact_wizard-current_step': 'form1',
    }
    wizard_step_data = (
        {
            'form1-name': 'Pony',
            'form1-thirsty': '2',
            'cookie_contact_wizard-current_step': 'form1',
        },
        {
            'form2-address1': '123 Main St',
            'form2-address2': 'Djangoland',
            'cookie_contact_wizard-current_step': 'form2',
        },
        {
            'form3-random_crap': 'blah blah',
            'cookie_contact_wizard-current_step': 'form3',
        },
        {
            'form4-INITIAL_FORMS': '0',
            'form4-TOTAL_FORMS': '2',
            'form4-MAX_NUM_FORMS': '0',
            'form4-0-random_crap': 'blah blah',
            'form4-1-random_crap': 'blah blah',
            'cookie_contact_wizard-current_step': 'form4',
        }
    )


@override_settings(ROOT_URLCONF='tests.wizard.wizardtests.urls')
class WizardTestKwargs(TestCase):
    wizard_url = '/wiz_other_template/'
    wizard_step_1_data = {
        'cookie_contact_wizard-current_step': 'form1',
    }
    wizard_step_data = (
        {
            'form1-name': 'Pony',
            'form1-thirsty': '2',
            'cookie_contact_wizard-current_step': 'form1',
        },
        {
            'form2-address1': '123 Main St',
            'form2-address2': 'Djangoland',
            'cookie_contact_wizard-current_step': 'form2',
        },
        {
            'form3-random_crap': 'blah blah',
            'cookie_contact_wizard-current_step': 'form3',
        },
        {
            'form4-INITIAL_FORMS': '0',
            'form4-TOTAL_FORMS': '2',
            'form4-MAX_NUM_FORMS': '0',
            'form4-0-random_crap': 'blah blah',
            'form4-1-random_crap': 'blah blah',
            'cookie_contact_wizard-current_step': 'form4',
        }
    )

    def setUp(self):
        self.testuser, created = User.objects.get_or_create(username='testuser1')
        self.wizard_step_data[0]['form1-user'] = self.testuser.pk

    def test_template(self):
        response = self.client.get(self.wizard_url)
        self.assertTemplateUsed(response, 'other_wizard_form.html')


class WizardTestGenericViewInterface(TestCase):
    def test_get_context_data_inheritance(self):
        class TestWizard(CookieWizardView):
            """
            A subclass that implements ``get_context_data`` using the standard
            protocol for generic views (accept only **kwargs).

            See ticket #17148.
            """
            def get_context_data(self, **kwargs):
                context = super().get_context_data(**kwargs)
                context['test_key'] = 'test_value'
                return context

        factory = RequestFactory()
        view = TestWizard.as_view([forms.Form])

        response = view(factory.get('/'))
        self.assertEqual(response.context_data['test_key'], 'test_value')

    def test_get_context_data_with_mixin(self):
        class AnotherMixin:
            def get_context_data(self, **kwargs):
                context = super().get_context_data(**kwargs)
                context['another_key'] = 'another_value'
                return context

        class TestWizard(AnotherMixin, CookieWizardView):
            """
            A subclass that implements ``get_context_data`` using the standard
            protocol for generic views (accept only **kwargs).

            See ticket #17148.
            """
            def get_context_data(self, **kwargs):
                context = super().get_context_data(**kwargs)
                context['test_key'] = 'test_value'
                return context

        factory = RequestFactory()

        view = TestWizard.as_view([forms.Form])

        response = view(factory.get('/'))
        self.assertEqual(response.context_data['test_key'], 'test_value')
        self.assertEqual(response.context_data['another_key'], 'another_value')


class WizardTestPrefix(TestCase):
    def test_get_prefix(self):
        class TestWizard(CookieWizardView):
            def get_prefix(self, request, *args, **kwargs):
                return 'sample_prefix'

        factory = RequestFactory()
        view = TestWizard.as_view([forms.Form])

        response = view(factory.get('/'))
        prefix = response.context_data['wizard']['management_form'].prefix
        self.assertEqual(prefix, 'sample_prefix')

    def test_get_prefix_using_request_object(self):
        class TestWizard(CookieWizardView):
            def get_prefix(self, request, *args, **kwargs):
                return request.prefix_value

        factory = RequestFactory()
        view = TestWizard.as_view([forms.Form])

        request = factory.get('/')
        request.prefix_value = 'text_prefix'

        response = view(request)
        prefix = response.context_data['wizard']['management_form'].prefix
        self.assertEqual(prefix, 'text_prefix')


class WizardFormKwargsOverrideTests(TestCase):
    def setUp(self):
        super().setUp()
        self.rf = RequestFactory()

        # Create two users so we can filter by is_staff when handing our
        # wizard a queryset keyword argument.
        self.normal_user = User.objects.create(username='test1', email='normal@example.com')
        self.staff_user = User.objects.create(username='test2', email='staff@example.com', is_staff=True)

    def test_instance_is_maintained(self):
        self.assertEqual(2, User.objects.count())
        queryset = User.objects.get(pk=self.staff_user.pk)

        class InstanceOverrideWizard(CookieWizardView):
            def get_form_kwargs(self, step):
                return {'instance': queryset}

        view = InstanceOverrideWizard.as_view([UserForm])
        response = view(self.rf.get('/'))

        form = response.context_data['wizard']['form']

        self.assertNotEqual(form.instance.pk, None)
        self.assertEqual(form.instance.pk, self.staff_user.pk)
        self.assertEqual('staff@example.com', form.initial.get('email', None))

    def test_queryset_is_maintained(self):
        queryset = User.objects.filter(pk=self.staff_user.pk)

        class QuerySetOverrideWizard(CookieWizardView):
            def get_form_kwargs(self, step):
                return {'queryset': queryset}

        view = QuerySetOverrideWizard.as_view([UserFormSet])
        response = view(self.rf.get('/'))

        formset = response.context_data['wizard']['form']

        self.assertNotEqual(formset.queryset, None)
        self.assertEqual(formset.initial_form_count(), 1)
        self.assertEqual(['staff@example.com'], list(formset.queryset.values_list('email', flat=True)))


class WizardInlineFormSetTests(TestCase):
    def setUp(self):
        self.rf = RequestFactory()
        self.poet = Poet.objects.create(name='test')
        self.poem = self.poet.poem_set.create(name='test poem')

    def test_set_instance(self):
        # Regression test for #21259
        poet = self.poet

        class InlineFormSetWizard(CookieWizardView):
            instance = None

            def get_form_instance(self, step):
                if self.instance is None:
                    self.instance = poet
                return self.instance

        view = InlineFormSetWizard.as_view([PoemFormSet])
        response = view(self.rf.get('/'))
        formset = response.context_data['wizard']['form']
        self.assertEqual(formset.instance, self.poet)
