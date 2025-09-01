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
import sys
import argparse
import importlib
from pkg_resources import resource_filename
from pyrocumulus.exceptions import(PyrocumulusCommandNotFound,
                                   PyrocumulusException)


class BaseCommand:
    """
    Base class for all commands. Your subclass must implement
    run().

    If your command accept command line arguments, just add they
    to the user_options list. Each command in this list is a
    dictionary, containing two keys: 'args', and 'kwargs'. Like this:

    [{'args': ('opt1',)
     'kwargs': {'default': True}}, ...]

    'args' and 'kwargs' are arguments passed to ArgumentParser.add_argument
    from argparse module. For details take a look here

    http://docs.python.org/3.3/howto/argparse.html#id1

    and here

    http://docs.python.org/3.3/library/argparse.html#module-argparse
    """

    description = None
    # --settings=settings.module
    default_options = [{'args': ('--settings',),
                        'kwargs': {'default': None,
                                   'help': 'settings module to use',
                                   'nargs': '?'}}]
    user_options = []

    def __init__(self):
        self.name = self.get_command_name()
        self.parser = argparse.ArgumentParser()
        self.add_args()
        self.parse_args()

    def __call__(self):
        self.run()

    def add_args(self):
        """
        Add the arguments in options
        """
        # first, adding the command itself, since the command is passed
        # as a param to pyromanager or pyrocumulus
        cmd_description = self.description or '%s command' % self.name
        self.parser.add_argument(self.name, help=cmd_description)

        self.user_options += self.default_options
        for option in self.user_options:
            self.parser.add_argument(*option['args'], **option['kwargs'])

    def parse_args(self):
        """
        Parse the args from the command line
        """
        options = self.parser.parse_args()
        self.settings = None
        args = [opt for opt in dir(options) if not opt.startswith('_')]
        for arg in args:
            setattr(self, arg, getattr(options, arg))

    def run(self):
        """
        Execute your action. Your command must implement this.
        This method is an async method. Must use @gen.coroutine
        """
        raise NotImplementedError

    def get_command_name(self):
        name = self.__class__.__module__.split('.')[-1]
        return name


def get_command(name):
    """
    Retuns a command based on `name`. The name of the command will be
    the file name, without the extension. So, if we have a mycommand.py
    file, the command name will be mycommand.
    """
    setenv()
    packages = []
    try:
        from pyrocumulus.conf import settings
        if hasattr(settings, 'COMMAND_PACKAGES'):
            packages = settings.COMMAND_PACKAGES
    except ImportError:  # pragma no cover
        # if we don't have settings we use only the pyrocumulus
        # commands.
        pass

    packages.append('pyrocumulus.commands')
    for package in packages:
        package_name = '%s.%s' % (package, name)
        try:
            module = importlib.import_module(package_name)
        except ImportError:
            continue
        names = [n for n in dir(module) if not n.startswith('_')]
        for cname in names:
            cmd_class = getattr(module, cname)

            # The idea behind the __subclasses__ is that
            # one can extend a already know command
            if type(cmd_class) == type(BaseCommand) and \
               issubclass(cmd_class, BaseCommand) and \
               cmd_class != BaseCommand and not cmd_class.__subclasses__():

                return cmd_class

    raise PyrocumulusCommandNotFound(name)


def get_command_name():
    """
    Returns the pyrocumulus command name based on the
    command line
    """
    try:
        if 'python' in sys.argv[0]:
            cmdname = sys.argv[2]
        else:
            cmdname = sys.argv[1]
    except IndexError:
        raise PyrocumulusException('Invalid command line')

    return cmdname


def get_settings_module_name():
    settings_module = None
    for arg in sys.argv:
        if '--settings' in arg:
            settings_module = arg.split('--settings')[1].strip().strip('=')

    return settings_module


def setenv():
    """Sets the PYROCUMULUS_SETTINGS_MODULE variable acording to
    the command line parameter."""

    settings = get_settings_module_name()
    if settings:
        os.environ['PYROCUMULUS_SETTINGS_MODULE'] = settings


def run_command():
    """
    runs a pyrocumulus command based on the command line
    """
    command_name = get_command_name()
    if command_name == '--help' or command_name == '-h':
        show_help_message()
    else:
        command = get_command(command_name)()
        command.run()


def show_help_message():  # pragma: no cover
    """
    Print a help message about command on screen and exit.
    """

    commands = list_commands()

    msg = """
Available commands:

%s

Use `python pyromanager.py cmd --help` for further information
""" % '\n'.join(commands)

    print(msg)


def list_commands():
    commands = []
    commands_dir = resource_filename('pyrocumulus', 'commands')
    for f in os.listdir(commands_dir):
        if f.startswith('_') or not f.endswith('.py'):
            continue
        cmdname = f.split('.')[0]
        if cmdname != 'base':
            commands.append(cmdname)
    return commands
