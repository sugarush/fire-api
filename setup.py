__author__ = 'Paul Severance'

from setuptools import setup

setup(
    name='sugar-api',
    version='0.0.1',
    author='Paul Severance',
    author_email='paul.severance@gmail.com',
    url='https://github.com/sugarush/sugar-api',
    packages=[
        'sugar_api'
    ],
    description='An asynchronous JSONAPI implementation based on Sanic.',
    install_requires=[
        'sugar-document@git+https://github.com/sugarush/sugar-document@master',
        'sugar-router@git+https://github.com/sugarush/sugar-router@master',
        'sugar-asynctest@git+https://github.com/sugarush/sugar-asynctest@master',
        'sugar-odm@git+https://github.com/sugarush/sugar-odm@master',
        'sanic',
        'pyjwt',
        'aioredis'
    ]
)
