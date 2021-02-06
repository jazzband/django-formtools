export DJANGO_SETTINGS_MODULE = tests.settings
export PYTHONPATH := $(shell pwd)

clean:
	git clean -Xfd

maketranslations:
	cd formtools; django-admin.py makemessages -a -v2

pulltranslations:
	tx pull -f -a --minimum-perc=1

compiletranslations:
	cd formtools; django-admin.py compilemessages

translations: pulltranslations maketranslations compiletranslations
	@echo "Pulling, making and compiling translations"

docs:
	$(MAKE) -C docs clean html

test:
	@flake8
	@isort --check-only --diff formtools tests
	@ coverage run `which django-admin` test tests
	@coverage report
	@coverage xml

.PHONY: clean docs test maketranslations pulltranslations compiletranslations
