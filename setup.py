import os
from setuptools import find_packages, setup


def read(*parts):
    filename = os.path.join(os.path.dirname(__file__), *parts)
    with open(filename, encoding="utf-8") as fp:
        return fp.read()


setup(
    name="django-formtools",
    use_scm_version={"version_scheme": "post-release", "local_scheme": "dirty-tag"},
    setup_requires=["setuptools_scm"],
    url="https://django-formtools.readthedocs.io/en/latest/",
    license="BSD",
    description="A set of high-level abstractions for Django forms",
    long_description=read("README.rst"),
    long_description_content_type="text/x-rst",
    author="Django Software Foundation",
    author_email="foundation@djangoproject.com",
    packages=find_packages(exclude=["tests", "tests.*"]),
    include_package_data=True,
    install_requires=["Django>=2.2"],
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Django :: 2.2",
        "Framework :: Django :: 3.1",
        "Framework :: Django :: 3.2",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Internet :: WWW/HTTP",
    ],
    zip_safe=False,
)
