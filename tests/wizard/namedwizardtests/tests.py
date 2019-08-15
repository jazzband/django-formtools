import copy

from django.contrib.auth.models import User
from django.http import QueryDict
from django.test import TestCase, override_settings
from django.urls import reverse

from formtools.wizard.views import (
    NamedUrlCookieWizardView, NamedUrlSessionWizardView,
)

from ..test_forms import Step1, Step2, get_request
from .forms import temp_storage

UPLOADED_FILE_NAME = 'tests.py'


class NamedWizardTests:

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
        response = self.client.get(reverse('%s_start' % self.wizard_urlname))
        self.assertEqual(response.status_code, 302)
        response = self.client.get(response.url)
        self.assertEqual(response.status_code, 200)
        wizard = response.context['wizard']
        self.assertEqual(wizard['steps'].current, 'form1')
        self.assertEqual(wizard['steps'].step0, 0)
        self.assertEqual(wizard['steps'].step1, 1)
        self.assertEqual(wizard['steps'].last, 'form4')
        self.assertEqual(wizard['steps'].prev, None)
        self.assertEqual(wizard['steps'].next, 'form2')
        self.assertEqual(wizard['steps'].count, 4)
        self.assertEqual(wizard['url_name'], self.wizard_urlname)

    def test_initial_call_with_params(self):
        get_params = {'getvar1': 'getval1', 'getvar2': 'getval2'}
        response = self.client.get(reverse('%s_start' % self.wizard_urlname),
                                   get_params)
        self.assertEqual(response.status_code, 302)

        # Test for proper redirect GET parameters
        location = response.url
        self.assertNotEqual(location.find('?'), -1)
        querydict = QueryDict(location[location.find('?') + 1:])
        self.assertEqual(dict(querydict.items()), get_params)

    def test_form_post_error(self):
        response = self.client.post(
            reverse(self.wizard_urlname, kwargs={'step': 'form1'}),
            self.wizard_step_1_data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['wizard']['steps'].current, 'form1')
        self.assertEqual(response.context['wizard']['form'].errors,
                         {'name': ['This field is required.'],
                          'user': ['This field is required.']})

    def test_form_post_success(self):
        response = self.client.post(
            reverse(self.wizard_urlname, kwargs={'step': 'form1'}),
            self.wizard_step_data[0])
        response = self.client.get(response.url)

        self.assertEqual(response.status_code, 200)
        wizard = response.context['wizard']
        self.assertEqual(wizard['steps'].current, 'form2')
        self.assertEqual(wizard['steps'].step0, 1)
        self.assertEqual(wizard['steps'].prev, 'form1')
        self.assertEqual(wizard['steps'].next, 'form3')

    def test_form_stepback(self):
        response = self.client.get(
            reverse(self.wizard_urlname, kwargs={'step': 'form1'}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['wizard']['steps'].current, 'form1')

        response = self.client.post(
            reverse(self.wizard_urlname, kwargs={'step': 'form1'}),
            self.wizard_step_data[0])
        response = self.client.get(response.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['wizard']['steps'].current, 'form2')

        response = self.client.post(
            reverse(self.wizard_urlname, kwargs={
                'step': response.context['wizard']['steps'].current
            }), {'wizard_goto_step': response.context['wizard']['steps'].prev})
        response = self.client.get(response.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['wizard']['steps'].current, 'form1')

    def test_form_jump(self):
        response = self.client.get(
            reverse(self.wizard_urlname, kwargs={'step': 'form1'}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['wizard']['steps'].current, 'form1')

        response = self.client.get(
            reverse(self.wizard_urlname, kwargs={'step': 'form3'}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['wizard']['steps'].current, 'form3')

    def test_form_finish(self):
        response = self.client.get(
            reverse(self.wizard_urlname, kwargs={'step': 'form1'}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['wizard']['steps'].current, 'form1')

        response = self.client.post(
            reverse(self.wizard_urlname,
                    kwargs={'step': response.context['wizard']['steps'].current}),
            self.wizard_step_data[0])
        response = self.client.get(response.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['wizard']['steps'].current, 'form2')

        post_data = self.wizard_step_data[1]
        with open(__file__, 'rb') as post_file:
            post_data['form2-file1'] = post_file
            response = self.client.post(
                reverse(self.wizard_urlname,
                        kwargs={'step': response.context['wizard']['steps'].current}),
                post_data)
        response = self.client.get(response.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['wizard']['steps'].current, 'form3')

        # Check that the file got uploaded properly.
        with open(__file__, 'rb') as f, temp_storage.open(UPLOADED_FILE_NAME) as f2:
            self.assertEqual(f.read(), f2.read())

        response = self.client.post(
            reverse(self.wizard_urlname,
                    kwargs={'step': response.context['wizard']['steps'].current}),
            self.wizard_step_data[2])
        response = self.client.get(response.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['wizard']['steps'].current, 'form4')

        response = self.client.post(
            reverse(self.wizard_urlname,
                    kwargs={'step': response.context['wizard']['steps'].current}),
            self.wizard_step_data[3])
        response = self.client.get(response.url)
        self.assertEqual(response.status_code, 200)

        # After the wizard is done no files should exist anymore.
        self.assertFalse(temp_storage.exists(UPLOADED_FILE_NAME))

        all_data = response.context['form_list']
        del all_data[1]['file1']
        self.assertEqual(all_data, [
            {'name': 'Pony', 'thirsty': True, 'user': self.testuser},
            {'address1': '123 Main St', 'address2': 'Djangoland'},
            {'random_crap': 'blah blah'},
            [{'random_crap': 'blah blah'}, {'random_crap': 'blah blah'}]])

    def test_cleaned_data(self):
        response = self.client.get(
            reverse(self.wizard_urlname, kwargs={'step': 'form1'}))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            reverse(self.wizard_urlname,
                    kwargs={'step': response.context['wizard']['steps'].current}),
            self.wizard_step_data[0])
        response = self.client.get(response.url)
        self.assertEqual(response.status_code, 200)

        post_data = self.wizard_step_data[1]
        with open(__file__, 'rb') as post_file:
            post_data['form2-file1'] = post_file
            response = self.client.post(
                reverse(self.wizard_urlname,
                        kwargs={'step': response.context['wizard']['steps'].current}),
                post_data)
        response = self.client.get(response.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(temp_storage.exists(UPLOADED_FILE_NAME))

        step2_url = reverse(self.wizard_urlname, kwargs={'step': 'form2'})
        response = self.client.get(step2_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['wizard']['steps'].current, 'form2')
        with open(__file__, 'rb') as f, temp_storage.open(UPLOADED_FILE_NAME) as f2:
            self.assertEqual(f.read(), f2.read())

        response = self.client.post(
            reverse(self.wizard_urlname,
                    kwargs={'step': response.context['wizard']['steps'].current}),
            self.wizard_step_data[2])
        response = self.client.get(response.url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            reverse(self.wizard_urlname,
                    kwargs={'step': response.context['wizard']['steps'].current}),
            self.wizard_step_data[3])
        response = self.client.get(response.url)
        self.assertEqual(response.status_code, 200)

        all_data = response.context['all_cleaned_data']
        self.assertEqual(all_data['file1'].name, UPLOADED_FILE_NAME)
        self.assertTrue(all_data['file1'].closed)
        self.assertFalse(temp_storage.exists(UPLOADED_FILE_NAME))
        del all_data['file1']
        self.assertEqual(
            all_data,
            {'name': 'Pony', 'thirsty': True, 'user': self.testuser,
             'address1': '123 Main St', 'address2': 'Djangoland',
             'random_crap': 'blah blah', 'formset-form4': [
                 {'random_crap': 'blah blah'},
                 {'random_crap': 'blah blah'}
             ]})

        form_dict = response.context['form_dict']
        self.assertIn('form1', form_dict.keys())
        self.assertIn('form2', form_dict.keys())
        self.assertEqual(form_dict['form1'].cleaned_data, response.context['form_list'][0])

    def test_manipulated_data(self):
        response = self.client.get(
            reverse(self.wizard_urlname, kwargs={'step': 'form1'}))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            reverse(self.wizard_urlname,
                    kwargs={'step': response.context['wizard']['steps'].current}),
            self.wizard_step_data[0])
        response = self.client.get(response.url)
        self.assertEqual(response.status_code, 200)

        post_data = self.wizard_step_data[1]
        with open(__file__, 'rb') as post_file:
            post_data['form2-file1'] = post_file
            response = self.client.post(
                reverse(self.wizard_urlname,
                        kwargs={'step': response.context['wizard']['steps'].current}),
                post_data)
        response = self.client.get(response.url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            reverse(self.wizard_urlname,
                    kwargs={'step': response.context['wizard']['steps'].current}),
            self.wizard_step_data[2])
        loc = response.url
        response = self.client.get(loc)
        self.assertEqual(response.status_code, 200, loc)

        self.client.cookies.pop('sessionid', None)
        self.client.cookies.pop('wizard_cookie_contact_wizard', None)

        response = self.client.post(
            reverse(self.wizard_urlname,
                    kwargs={'step': response.context['wizard']['steps'].current}),
            self.wizard_step_data[3])

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['wizard']['steps'].current, 'form1')

    def test_form_reset(self):
        response = self.client.post(
            reverse(self.wizard_urlname, kwargs={'step': 'form1'}),
            self.wizard_step_data[0])
        response = self.client.get(response.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['wizard']['steps'].current, 'form2')

        response = self.client.get(
            '%s?reset=1' % reverse('%s_start' % self.wizard_urlname))
        self.assertEqual(response.status_code, 302)

        response = self.client.get(response.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['wizard']['steps'].current, 'form1')


@override_settings(ROOT_URLCONF='tests.wizard.namedwizardtests.urls')
class NamedSessionWizardTests(NamedWizardTests, TestCase):
    wizard_urlname = 'nwiz_session'
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


@override_settings(ROOT_URLCONF='tests.wizard.namedwizardtests.urls')
class NamedCookieWizardTests(NamedWizardTests, TestCase):
    wizard_urlname = 'nwiz_cookie'
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


class NamedFormTests:

    def test_revalidation(self):
        request = get_request()

        testform = self.formwizard_class.as_view(
            [('start', Step1), ('step2', Step2)],
            url_name=self.wizard_urlname)
        response, instance = testform(request, step='done')

        instance.render_done(None)
        self.assertEqual(instance.storage.current_step, 'start')


class TestNamedUrlSessionWizardView(NamedUrlSessionWizardView):

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        return response, self


class TestNamedUrlCookieWizardView(NamedUrlCookieWizardView):

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        return response, self


@override_settings(ROOT_URLCONF='tests.wizard.namedwizardtests.urls')
class NamedSessionFormTests(NamedFormTests, TestCase):
    formwizard_class = TestNamedUrlSessionWizardView
    wizard_urlname = 'nwiz_session'


@override_settings(ROOT_URLCONF='tests.wizard.namedwizardtests.urls')
class NamedCookieFormTests(NamedFormTests, TestCase):
    formwizard_class = TestNamedUrlCookieWizardView
    wizard_urlname = 'nwiz_cookie'
