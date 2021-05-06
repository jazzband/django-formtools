from django import forms
from django.db import models


class ManyModel(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        app_label = 'formtools'


class OtherModel(models.Model):
    name = models.CharField(max_length=100)
    manymodels = models.ManyToManyField(ManyModel)

    class Meta:
        app_label = 'formtools'


class OtherModelForm(forms.ModelForm):
    class Meta:
        model = OtherModel
        fields = '__all__'


class TestForm(forms.Form):
    field1 = forms.CharField()
    field1_ = forms.CharField()
    bool1 = forms.BooleanField(required=False)
    date1 = forms.DateField(required=False)


class HashTestForm(forms.Form):
    name = forms.CharField()
    bio = forms.CharField()


class HashTestBlankForm(forms.Form):
    name = forms.CharField(required=False)
    bio = forms.CharField(required=False)
