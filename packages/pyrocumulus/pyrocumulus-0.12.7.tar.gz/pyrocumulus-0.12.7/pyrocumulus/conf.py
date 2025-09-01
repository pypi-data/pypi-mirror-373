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
import importlib


def get_settings_module_name():
    """
    Returns the module's name to be used as the settings module
    for this project. It can be changed by the environment variable
    ``PYROCYMULUS_SETTINGS_MODULE``.

    Defaults to 'settings'.
    """
    settings_module = os.environ.get('PYROCUMULUS_SETTINGS_MODULE') or \
        'settings'

    return settings_module


def get_settings_module(module_name=None):
    """
    Returns the module to be used as the settings for this
    project. If `module_name` is None (default) get_settings_module_name
    is used.
    """
    module_name = module_name or get_settings_module_name()
    try:
        module = importlib.import_module(module_name)
    except ImportError:
        err_msg = 'Could not import settings module "%s"' % (module_name)
        raise ImportError(err_msg)

    return module


class Settings:

    def __getattr__(self, attrname):
        return getattr(get_settings_module(), attrname)

    def __setattr__(self, attrname, value):
        raise AttributeError('you can\'t set here')

settings = Settings()
