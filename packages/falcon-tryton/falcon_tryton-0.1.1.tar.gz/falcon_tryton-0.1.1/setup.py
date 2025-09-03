# This file is part of flask_tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
import io
import os
import re

from setuptools import setup


def read(fname):
    return io.open(
        os.path.join(os.path.dirname(__file__), fname),
        'r', encoding='utf-8').read()


def get_version():
    init = read('falcon_tryton.py')
    return re.search("__version__ = '([0-9.]*)'", init).group(1)


setup(name='falcon_tryton',
    version=get_version(),
    description='Adds Tryton support to Falcon application',
    long_description=read('README.md'),
    long_description_content_type="text/markdown",
    author='Numael Garay',
    author_email='mantrixsoft@gmail.com',
    url='https://gitlab.com/numaelis/falcon-tryton',    
    py_modules=['falcon_tryton'],
    zip_safe=False,
    platforms='any',
    keywords='falcon tryton web',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Tryton',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
        ],
    license='GPL-3',
    python_requires='>=3.8',
    install_requires=[
        'Falcon>=4.0',
        'Werkzeug',
        'trytond>=5.0',
        ],
    )
 
