# -*- coding: utf-8 -*-

# Copyright 2015 Juca Crispim <juca@poraodojuca.net>

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
# along with pyrocumulus. If not, see <http://www.gnu.org/licenses/>.

from pyrocumulus.web.operationmappers import HandlerOperationMapper


def _get_class_fqualname_from_method(method):
    """Returns the full qualified name for a class using a method from
    the class as reference. """
    module_name = method.__module__
    cls_name, meth_name = method.__qualname__.split('.')
    fqualname = '.'.join([module_name, cls_name])
    return fqualname


class BaseOperationDecorator:

    def __init__(self, req_method, operation):
        self.req_method = req_method
        self.operation = operation

    def __call__(self, cls_meth):
        fqualname = _get_class_fqualname_from_method(cls_meth)

        HandlerOperationMapper.set_operation(fqualname, self.req_method,
                                             self.operation, cls_meth)
        return cls_meth


class get(BaseOperationDecorator):

    def __init__(self, operation):
        super().__init__('get', operation)


class post(BaseOperationDecorator):

    def __init__(self, operation):
        super().__init__('post', operation)


class put(BaseOperationDecorator):

    def __init__(self, operation):
        super().__init__('put', operation)


class delete(BaseOperationDecorator):

    def __init__(self, operation):
        super().__init__('delete', operation)


class options(BaseOperationDecorator):

    def __init__(self, operation):
        super().__init__('options', operation)


class patch(BaseOperationDecorator):

    def __init__(self, operation):
        super().__init__('patch', operation)
