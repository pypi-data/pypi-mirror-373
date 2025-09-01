# -*- coding: utf-8 -*-

# Copyright 2016 Juca Crispim <juca@poraodojuca.net>

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

from collections import defaultdict
from tornado.routing import PathMatches
from tornado.web import HTTPError


class HandlerOperationMapper:
    """Maps operations for a Handler method."""

    _allowed_operations = defaultdict(dict)

    @classmethod
    def create_allowed_operations(cls, cls_fqualname):
        """Creates initial allowed operations for a class.

        :param cls_fqualname: The fully qualified name for a handler
          class."""

        ops = {'get': {},
               'post': {},
               'put': {},
               'patch': {},
               'delete': {},
               'options': {},
               'inherited': False}

        cls._allowed_operations[cls_fqualname] = ops

        return cls._allowed_operations[cls_fqualname]

    @classmethod
    def get_allowed_operations_for(cls, cls_fqualname):
        """Returns the allowed operations for ``cls_fqualname``

        :param cls_fqualname: Fully qualified named of a class"""

        return cls._allowed_operations.get(cls_fqualname) or {}

    @classmethod
    def set_operation(cls, cls_fqualname, req_method, operation, cls_meth):
        """ Sets ``operation`` as an allowed operation for ``cls_fqualname``
        using ``req_method``.

        :param cls_fqualname: The fully qualified name for the class that
          will have the allowed operation.
        :param req_method: The request method for the operation. This can be
          ``get``, ``post``, ``put`` or ``delete``.
        :param operation: The operation name.
        :param cls_meth: Method that will be used in this operation."""

        if cls_fqualname not in cls._allowed_operations.keys():
            allowed = cls.create_allowed_operations(cls_fqualname)
        else:
            allowed = cls.get_allowed_operations_for(cls_fqualname)

        try:
            allowed[req_method].update({operation: cls_meth})
        except KeyError:
            msg = 'Request method {} not known!'.format(req_method)
            raise KeyError(msg)

    @classmethod
    def update_operations_for(cls, cls_fqualname, operations):
        """Updates the allowed operations for ``cls_fqualname``.

        :param cls_fqualname: Fully qualified name for the class
          that will have the operations updated.
        :param operations: A dict with the allowed operations."""

        for req_meth, ops in operations.items():
            if not hasattr(ops, 'items'):
                continue
            for op, call in ops.items():
                cls.set_operation(cls_fqualname, req_meth, op, call)

    @classmethod
    def get_all_operations_for(cls, cls_fqualname):
        """Returns a set with all operations valid for ``cls_fqualname``.

        :param cls_fqualname: Fully qualified name for a class."""

        allowed = cls.get_allowed_operations_for(cls_fqualname)
        all_ops = set()
        for k, v in allowed.items():
            # The thing here is that in the operations dict, we have
            # the key inherited that has a bool value, not related to
            # the operations itself.
            if hasattr(v, 'keys'):
                all_ops.update(set(v.keys()))

        return all_ops

    @classmethod
    def _match_against(self, operation, ops):
        for op in ops:
            matcher = PathMatches(op)
            fake_request = type('FakeRequest', (), {'path': operation})
            match = matcher.match(fake_request)
            if match is not None:
                return match, op

        return None, None

    @classmethod
    def validate(cls, cls_fqualname, req_type, operation):
        """Validates if ``operation`` is valid for ``cls_fqualname``
        using ``req_type``. Returns the method to be used by ``operation``
        if it is valid. Raises 404 if the operation does not exist or
        405 if the operation is not allowed for ``req_type``

        :param cls_fqualname: Fully qualified name of the handler.
        :param req_type: Request method being used.
        :param operation: The operation to be validated."""

        all_ops = cls.get_all_operations_for(cls_fqualname)
        args, op = cls._match_against(operation, all_ops)
        if args is None:
            raise HTTPError(404)

        req_ops = cls.get_allowed_operations_for(cls_fqualname)[req_type]
        args, op = cls._match_against(operation, req_ops.keys())
        if args is None:
            raise HTTPError(405)

        meth = req_ops[op]
        args, kwargs = args.get('path_args', []), args.get('path_kwargs', {})
        return meth, args, kwargs
