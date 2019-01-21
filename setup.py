__author__ = 'Lucifer Avada'

from setuptools import setup

setup(
    name='sugar-api',
    version='0.0.1',
    author='Lucifer Avada',
    author_email='lucifer.avada@gmail.com',
    url='https://github.com/sugarush/sugar-api',
    packages=[
        'sugar_api',
    ],
    description='A Sanic JSONAPI implementation.',
    install_requires=[
        'sugar_document',
        'sugar_asynctest',
        'sugar_odm'
    ],
    dependency_links=[
        'git+https://github.com/sugarush/sugar-document@master#egg=sugar-document',
        'git+https://github.com/sugarush/sugar-asynctest@master#egg=sugar-asynctest',
        'git+https://github.com/sugarush/sugar-odm@master#egg=sugar-odm',
    ]
)
