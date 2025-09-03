"""
Steps for packaging
-------------------

Delete build & dist folders
python3 setup.py sdist bdist_wheel
python3 -m twine upload dist/*
Enter your username: __token__
Enter your password: *****
"""

import os
import codecs
from setuptools import setup

# Get README.md details
with codecs.open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'README.md'), encoding='utf-8') as f:
    long_description = '\n' + f.read()

# Setup
setup(name='test_rest_api',
      version='0.0.0.0.52',
      author='Troy M Jose',
      entry_points={"console_scripts": ["test_rest_api = test_rest_api.cli.cli:main", ], },
      author_email='',
      url='https://github.com/troymjose/test_rest_api',
      bugtrack_url='https://github.com/troymjose/test_rest_api/issues',
      project_urls={
          'Source': 'https://github.com/troymjose/test_rest_api',
          'Tracker': 'https://github.com/troymjose/test_rest_api/issues',
      },
      description='Asynchronous Test Framework #HighPerformance #EasyToLearn #FastToCode #AsyncTests',
      keywords=['test', 'unittest', 'restapi', 'testframework', 'asyncio', 'async', 'asynchronous',
                'testingframework', 'rest', 'api', 'python', 'python3', 'testing', 'unittesting', 'automation',
                'automationtest', 'automationtesting',
                'restapitest', 'restapitesting', 'restapiunittest', 'restapiunittesting', 'restapiautomation',
                'restapiautomationtest', 'restapiautomationtesting', 'apitest', 'apitesting', 'apiunittest',
                'apiunittesting', 'apiautomation', 'apiautomationtest', 'apiautomationtesting'],
      packages=['test_rest_api', 'test_rest_api.assertion', 'test_rest_api.bug', 'test_rest_api.constant',
                'test_rest_api.decorator', 'test_rest_api.environment', 'test_rest_api.exceptions',
                'test_rest_api.loggers', 'test_rest_api.logging', 'test_rest_api.reporting', 'test_rest_api.rest_api',
                'test_rest_api.runner', 'test_rest_api.runtime', 'test_rest_api.settings', 'test_rest_api.test_data',
                'test_rest_api.traceback_formatter', 'test_rest_api.utils', 'test_rest_api.variable'],
      install_requires=['aiohttp', 'Jinja2', 'python-dotenv'],
      long_description_content_type='text/markdown',
      long_description=long_description,
      classifiers=['Programming Language :: Python :: 3.12',
                   'Programming Language :: Python :: 3.13',
                   'License :: OSI Approved :: MIT License',
                   'Operating System :: OS Independent',
                   'Framework :: AsyncIO',
                   'Framework :: aiohttp',
                   'Topic :: Utilities',
                   'Topic :: Software Development',
                   'Topic :: Software Development :: Testing',
                   'Topic :: Software Development :: Testing :: Unit',
                   'Topic :: Software Development :: Quality Assurance',
                   'Topic :: Software Development :: Libraries',
                   'Topic :: Software Development :: Libraries :: Python Modules',
                   'Topic :: Software Development :: Libraries :: Application Frameworks'])
