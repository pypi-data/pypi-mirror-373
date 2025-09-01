# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import io
import os


about = {}
about_filename = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'volgactf', 'final', '__about__.py')
with io.open(about_filename, 'rb') as fp:
    exec(fp.read(), about)


setup(
    name='volgactf.final',
    version=about['__version__'],
    description='VolgaCTF Final CLI & public API library',
    author='VolgaCTF',
    author_email='it@volgactf.ru',
    url='https://github.com/VolgaCTF/volgactf-final-py',
    license='MIT',
    packages=find_packages('.'),
    install_requires=[
        'setuptools>=35.0.0',
        'requests>=2.18.4',
        'grequests==0.3.0',
        'click>=6.7',
        'python-dateutil>=2.6.0',
        'PyJWT>=2.4.0',
        'cryptography>=2.3.0'
    ],
    python_requires='>=3.9',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
    ],
    namespace_packages=[
        'volgactf'
    ],
    entry_points={
        'console_scripts': [
            'volgactf-final = volgactf.final:cli',
        ]
    }
)
