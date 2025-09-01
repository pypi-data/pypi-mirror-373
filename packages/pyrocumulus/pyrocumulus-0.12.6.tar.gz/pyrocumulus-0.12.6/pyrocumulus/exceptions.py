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


class PyrocumulusException(Exception):  # pragma: no cover
    pass


class PyrocumulusConverterException(PyrocumulusException):  # pragma: no cover
    pass


class PyrocumulusCommandNotFound(PyrocumulusException):  # pragma: no cover
    pass


class TemplateNotFound(PyrocumulusException):  # pragma: no cover
    pass


class StaticFileError(PyrocumulusException):  # pragma: no cover
    pass


class PyrocumulusConfusionError(PyrocumulusException):  # pragma: no cover
    pass


class PyrocumulusBadToken(PyrocumulusException):  # pragma: no cover
    pass
