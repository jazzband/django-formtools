from django import forms


class TestForm(forms.Form):
    field1 = forms.CharField()
    field1_ = forms.CharField()
    bool1 = forms.BooleanField(required=False)
    date1 = forms.DateField(required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(TestForm, self).__init__(*args, **kwargs)


class HashTestForm(forms.Form):
    name = forms.CharField()
    bio = forms.CharField()


class HashTestBlankForm(forms.Form):
    name = forms.CharField(required=False)
    bio = forms.CharField(required=False)


class HashTestFormWithFile(forms.Form):
    name = forms.CharField()
    attachment = forms.FileField(required=False)
