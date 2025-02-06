from django import forms
from django.core.exceptions import ValidationError


class ManagementForm(forms.Form):
    """
    ``ManagementForm`` is used to keep track of the current wizard step.
    """
    def __init__(self, steps, **kwargs):
        self.steps = steps
        super().__init__(**kwargs)

    template_name = "django/forms/p.html"  # Remove when Django 5.0 is minimal version.
    current_step = forms.CharField(widget=forms.HiddenInput)

    def clean_current_step(self):
        data = self.cleaned_data['current_step']
        if data not in self.steps:
            raise ValidationError("Invalid step name.")
        return data
