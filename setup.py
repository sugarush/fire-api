__author__ = 'Paul Severance'

from setuptools import setup

setup(
    name='fire-api',
    version='0.0.1',
    author='Paul Severance',
    author_email='paul.severance@gmail.com',
    url='https://github.com/sugarush/fire-api',
    packages=[
        'fire_api'
    ],
    description='An asynchronous JSONAPI implementation based on Sanic.',
    install_requires=[
        'fire-document@git+https://github.com/sugarush/fire-document@master',
        'fire-router@git+https://github.com/sugarush/fire-router@master',
        'fire-asynctest@git+https://github.com/sugarush/fire-asynctest@master',
        'fire-odm@git+https://github.com/sugarush/fire-odm@master',
        'sanic',
        'pyjwt',
        'aioredis'
    ]
)
