#!/usr/bin/env python3
# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
import os


here = os.path.abspath(os.path.dirname(__file__))


def long_description():
    with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        return f.read()


def get_cdc_package_data():
    # Example that grabs all *.ini files in the cwd and all files in foo/bar
    # other_files = ['*.ini']
    # for r, _, fs in os.walk(os.path.join(here, 'foo', 'bar')):
    #     for f in fs:
    #         other_files.append(os.path.join(r, f))
    # return other_files
    return ['*.ini']


def get_data_files():
    pass


def __find(key):
    with open(os.path.join('cdc', '__init__.py')) as fp:
        key = '__{}__'.format(key)
        for line in fp:
            if key in line.strip():
                value = line.split('=', 1)[1].strip().strip('\'')
                return value


def find_version():
    return __find('version')


def find_bin_name():
    return __find('bin_name')


def find_desc():
    return __find('desc')


setup(
    name=find_bin_name(),
    version=find_version(),
    description=find_desc(),
    long_description=long_description(),
    long_description_content_type='text/markdown',
    author='Matt Traudt',
    author_email='sirmatt@ksu.edu',
    license='MIT',
    url='https://github.com/pastly/craps-dice-control',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.7',
    ],
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'cdc': get_cdc_package_data(),
    },
    data_files=get_data_files(),
    keywords='craps simulation dice statistics',
    python_requires='>=3.7',
    entry_points={
        'console_scripts': [
            'cdc = cdc.__main__:main',
        ]
    },
    install_requires=[
        'matplotlib',
        'scipy',
    ],
    extras_require={
        'test': ['tox', 'pytest', 'coverage'],
        'dev': ['flake8', 'vulture'],
        'fuzz': ['python-afl'],
    },
)
