import os
import os.path
import sys
from invoke import run, task


@task
def clean():
    run('git clean -Xfd')


@task
def test():
    print('Python version: ' + sys.version)
    test_cmd = 'coverage run `which django-admin.py` test --settings=tests.settings'
    flake_cmd = 'flake8 --ignore=W801,E128,E501,W402'

    # Fix issue #49
    cwp = os.path.dirname(os.path.abspath(__name__))
    pythonpath = os.environ.get('PYTHONPATH', '').split(os.pathsep)
    pythonpath.append(os.path.join(cwp, 'tests'))
    os.environ['PYTHONPATH'] = os.pathsep.join(pythonpath)

    run('{0} formtools'.format(flake_cmd))
    run('{0} tests'.format(test_cmd))
    run('coverage report')


@task
def translations(pull=False):
    if pull:
        run('tx pull -a')
    run('cd formtools; django-admin.py makemessages -a; django-admin compilemessages; cd ..')


@task
def docs():
    run('cd docs; make html; cd ..')
