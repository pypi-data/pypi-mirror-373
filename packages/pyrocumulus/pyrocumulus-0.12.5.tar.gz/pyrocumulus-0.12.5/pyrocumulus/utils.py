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

import sys
try:
    import imp
    importlib = imp.importlib
except ImportError:
    import importlib
import inspect
import bcrypt
from pyrocumulus.conf import settings

SALT_ROUNDS = 8


def get_value_from_settings(key, default=None):
    value = getattr(settings, key, default)
    return value


def fqualname(obj):
    """
    Returns the full qualified name for an object, like
    pyrocumulus.converters.DocumentConverter

    :param obj: A python class
    """
    module = inspect.getmodule(obj)
    name = '%s.%s' % (module.__name__, obj.__name__)
    return name


def import_class(cls_fqualname):
    mod, cls = cls_fqualname.rsplit('.', 1)
    mod = importlib.import_module(mod)
    return getattr(mod, cls)


def bcrypt_string(string, salt=None):
    encoding = sys.getdefaultencoding()
    if not salt:
        salt = bcrypt.gensalt(SALT_ROUNDS)
    encrypted = bcrypt.hashpw(string.encode(encoding), salt)
    return encrypted.decode()
