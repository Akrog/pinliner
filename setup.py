#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    # TODO: put package requirements here
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='pinliner',
    version='0.2.0',
    description="Python Inliner merges in a single file all files from a "
                "Python package.",
    long_description=readme + '\n\n' + history,
    author="Gorka Eguileor",
    author_email='gorka@eguileor.com',
    url='https://github.com/Akrog/pinliner',
    packages=[
        'pinliner',
    ],
    package_dir={'pinliner':
                 'pinliner'},
    include_package_data=True,
    install_requires=requirements,
    license="Apache",
    zip_safe=False,
    keywords='pinliner',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    entry_points={
        'console_scripts': [
            'pinliner=pinliner.pinliner:main',
        ],
    },
    package_data={'pinliner': ['importer.template']},
)
