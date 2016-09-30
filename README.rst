This is a fork of django-formtools (https://github.com/django/django-formtools)
which intends to solve the forced validation when you want to navigate to previous
form. 

More specifically, say you have 5 forms altogether and you are currently in form 3
and you want to navigate to previous form. If you have required fields in form 3,
then you will be asked to fill in all the necessary fields by client-side JQuery
before you can go to form 2. Even if you have filled out the form and managed to
go to previous form, the data you have entered will not be saved and you will end
up having to do the again.

The solution of this fork is to add JQuery in the default template to skip the
validation and also make sure the navigation works as expected.

If you want to have your own template instead of your default one, please have a 
look at formtools/templates/formtools/wizard/wizard_form.html. 
If you are happy with the validation on click of previous button, then you will 
probably be annoyed by the fact that the data entered for the current form will 
not be saved after navigating to previous form. To fix this problem, 
refer to file formtools/wizard/views.py. Move codes between 
line 265 - 277 to line 301 will solve your problem.

If you have any question regarding this issue, let me know.

