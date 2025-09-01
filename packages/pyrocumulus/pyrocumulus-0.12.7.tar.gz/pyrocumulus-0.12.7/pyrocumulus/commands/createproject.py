#-*- coding: utf-8 -*-

# Copyright 2013-2015 Juca Crispim <juca@poraodojuca.net>

# This file is part of pyrocumulus.

# pyrocumulus is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# pyrocumulus is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with pyrocumulus.  If not, see <http://www.gnu.org/licenses/>.

import os
from tornado import gen
from pyrocumulus.commands.base import BaseCommand


SETUP_TEMPLATE = """#-*- coding: utf-8 -*-

from setuptools import setup, find_packages


setup(name='%(name)s',
      version='0.1',
      author='You Buddy',
      author_email='you@somewhere.com',
      description='%(name)s is really cool software',
      long_description="It's based on pyrocumulus and have nice features!",
      url='https://some-url-to-my-project.com',
      packages=find_packages(),
      install_requires=['pyrocumulus'],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Programming Language :: Python :: 3',
      ],
      test_suite='tests',
      provides=['%(name)s'],
)
"""

TESTS_TEMPLATE = """#-*- coding: utf-8 -*-

import unittest
"""

PYROMANAGER_TEMPLATE = """#!/usr/bin/env python
#-*- coding: utf-8 -*-

from tornado import ioloop
from pyrocumulus.commands.base import run_command

run_command()

"""

SETTINGS_TEMPLATE = """#-*- coding: utf-8 -*-

PROJECT_NAME = '%(name)s'

DATABASE = {'default': {'host': 'localhost',
                        'port': 27017,
                        'db': 'pyrocumulus'}}

APPLICATIONS = []

DEBUG = True
"""

MODELS_TEMPLATE = """#-*- coding: utf-8 -*-

"""

WEB_TEMPLATE = """#-*- coding: utf-8 -*-

"""

INIT_TEMPLATE = """#-*- coding: utf-8 -*-

from pyrocumulus.db import MongoConnection

connection = MongoConnection()
connection.connect()

"""


class CreateProjectCommand(BaseCommand):

    user_options = [
        # path
        {'args': ('path',),
         'kwargs': {'help': 'Path for this project'}},
        # --project-name name
        {'args': ('--project-name',),
         'kwargs': {'default': None, 'nargs': '?',
                    'help': 'Project\'s name'}}
    ]

    def run(self):
        self.project_name = self.project_name or \
            self.path.split(os.sep)[-1]

        self.path = os.path.abspath(self.path)
        print('creating new project at %s...' % self.path)
        self.package_path = os.path.join(self.path, self.project_name)

        try:
            os.mkdir(self.path)
            os.mkdir(self.package_path)
        except OSError:
            msg = 'Could not create dir %s for new project' % self.path
            raise OSError(msg)

        with open(os.path.join(self.path, 'setup.py'), 'w') as f:
            template = SETUP_TEMPLATE % {'name': self.project_name}
            f.write(template)

        with open(os.path.join(self.path, 'settings.py'), 'w') as f:
            template = SETTINGS_TEMPLATE % {'name': self.project_name}
            f.write(template)

        with open(os.path.join(self.path, 'tests.py'), 'w') as f:
            f.write(TESTS_TEMPLATE)

        with open(os.path.join(self.path, 'pyromanager.py'), 'w') as f:
            f.write(PYROMANAGER_TEMPLATE)

        with open(os.path.join(self.package_path, '__init__.py'), 'w') as f:
            f.write(INIT_TEMPLATE)

        with open(os.path.join(self.package_path, 'models.py'), 'w') as f:
            f.write(MODELS_TEMPLATE)

        with open(os.path.join(self.package_path, 'web.py'), 'w') as f:
            f.write(WEB_TEMPLATE)
