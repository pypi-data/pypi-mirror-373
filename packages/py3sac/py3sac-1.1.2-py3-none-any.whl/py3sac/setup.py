from setuptools import setup
from os import environ

version = '1.0.0'

if('VERSION' in environ.keys()):
    version = environ['VERSION']

setup(
    name = 'py3sac',
    version = version,
    packages = [ 'py3sac' ],
    url = '',
    long_description = 'Python modules to process SAC files (e.g. convert them to'
    ' ASCII) and a Python class called Sac to interact with the SAC program'
    ' (Seismic Analysis Code).',
    description = 'Python tools to use SAC files and execute commands using'
    'the SAC program  (Seismic Analysis Code).',
    classifiers = [ 'License :: OSI Approved :: BSD License',
                   'Programming Language :: Python :: 3'],
    install_requires = [ 'py3sacio' , 'pyutils' ],
    scripts=['py3sac/sac2asc'],
    package_data = {'py3sac' : ['LICENSE.md']},
    license = "3-clause BSD 2.0"
)
