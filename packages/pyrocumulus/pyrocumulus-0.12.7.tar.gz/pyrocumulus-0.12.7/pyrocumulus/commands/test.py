#-*- coding: utf-8 -*-

from setuptools.dist import Distribution
from setuptools.command.test import test
from tornado import gen
from pyrocumulus.commands.base import BaseCommand


class TestCommand(BaseCommand):
    description = "run unit tests WITHOUT in-place build"

    user_options = [
        {'args': ('--test-suite',),
         'kwargs': {'help':
                        "Test suite to run (e.g. 'some_module.test_suite')",
                    'nargs': '?'}},

        {'args': ('--test-module',),
         'kwargs': {'help': "Run 'test_suite' in specified module",
                    'nargs': '?'}}

    ]

    def run(self):
        if not self.test_suite:
            self.test_suite = 'tests'
        dist = Distribution()
        dist.script_name = 'setup.py'
        t = test(dist)
        t.initialize_options()
        t.test_suite = self.test_suite
        t.finalize_options()
        t.run()
