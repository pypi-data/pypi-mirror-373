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

from copy import deepcopy
from pyrocumulus.web.operationmappers import HandlerOperationMapper
from pyrocumulus.utils import fqualname


class HandlerOperationMetaclass(type):

    def __new__(cls, name, bases, attrs):
        attrs['operation_mapper'] = HandlerOperationMapper
        new_class = super().__new__(cls, name, bases, attrs)

        cls_fqualname = fqualname(new_class)

        # Here we save the operations of the class so we can update the final
        # operations with them after we do it with all bases.
        cls_ops = deepcopy(HandlerOperationMapper.get_allowed_operations_for(
            cls_fqualname))
        if not cls_ops:
            cls_ops = HandlerOperationMapper.create_allowed_operations(
                cls_fqualname)

        # Here we inherit the operations from base classes
        for base in list(reversed(bases)):
            base_fqualname = fqualname(base)
            base_ops = HandlerOperationMapper.get_allowed_operations_for(
                base_fqualname)
            HandlerOperationMapper.update_operations_for(cls_fqualname,
                                                         base_ops)

        HandlerOperationMapper.update_operations_for(cls_fqualname, cls_ops)

        return new_class
