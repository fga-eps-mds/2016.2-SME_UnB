# -*- coding: utf-8 -*-
#
# This file were created by Python Boilerplate. Use boilerplate to start simple
# usable and best-practices compliant Python projects.
#
# Learn more about it at: http://github.com/fabiommendes/python-boilerplate/
#

import os
import codecs
from setuptools import setup, find_packages

# Save version and author to __meta__.py
version = open('VERSION').read().strip()
dirname = os.path.dirname(__file__)
path = os.path.join(dirname, 'src', 'SME_UnB', '__meta__.py')
meta = '''# Automatically created. Please do not edit.
__version__ = u'%s'
__author__ = u'Brenddon Gontijo'
''' % version
with open(path, 'w') as F:
    F.write(meta)

setup(
    # Basic info
    name=u'SME-UnB',
    version=version,
    author='Brenddon Gontijo',
    author_email='brenddongontijo@msn.com',
    url='',
    description='A short description for your project.',
    long_description=codecs.open('README.rst', 'rb', 'utf8').read(),

    # Classifiers (see https://pypi.python.org/pypi?%3Aaction=list_classifiers)
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries',
    ],

    # Packages and dependencies
    package_dir={'': 'src'},
    packages=find_packages('src'),
    install_requires=[
        'requests[security]',
        'django==1.9.8',
        'psycopg2==2.6',
        'numpy',
        'pandas',
        'django-bootstrap3',
        'Sphinx',
        'django-polymorphic',
        'manuel',
    ],
    extras_require={
        'dev': [
            'python-boilerplate[dev]',
            'coverage==3.6',
            'mock',
        ],
    },

    # Other configurations
    zip_safe=False,
    platforms='any',
)
