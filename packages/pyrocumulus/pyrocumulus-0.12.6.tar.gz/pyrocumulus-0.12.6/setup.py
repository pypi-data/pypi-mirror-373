# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from setuptools.command.test import test


def get_version_from_file():
    # get version number from __init__ file
    # before module is installed

    fname = 'pyrocumulus/__init__.py'
    with open(fname) as f:
        fcontent = f.readlines()
    version_line = [l for l in fcontent if 'VERSION' in l][0]
    return version_line.split('=')[1].strip().strip("'").strip('"')


def get_long_description_from_file():
    # content of README will be the long description

    fname = 'README'
    with open(fname) as f:
        fcontent = f.read()
    return fcontent


class custom_test(test):
    # hack to run my functional tests on buildbot
    user_options = test.user_options + [
        ('tornadoenv=', None, "run tornado on correct virtualevn"),
    ]

    def initialize_options(self):
        super(custom_test, self).initialize_options()
        self.tornadoenv = None


VERSION = get_version_from_file()
DESCRIPTION = """
Glue-code to make (even more!) easy and fun work with mongoengine and tornado
"""
LONG_DESCRIPTION = get_long_description_from_file()

setup(name='pyrocumulus',
      version=VERSION,
      author='Juca Crispim',
      author_email='juca@poraodojuca.net',
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      url='https://gitorious.org/mongomotor',
      packages=find_packages(exclude=['tests', 'tests.*', 'settings',
                                      'settings.*']),
      install_requires=['tornado>=5.0.1', 'mongomotor>=0.9.3',
                        'bcrypt>=3.1.4'],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Internet :: WWW/HTTP',
          'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
      ],
      test_suite='tests',
      scripts=['script/pyrocumulus'],
      provides=['pyrocumulus'],
      cmdclass={'test': custom_test})
