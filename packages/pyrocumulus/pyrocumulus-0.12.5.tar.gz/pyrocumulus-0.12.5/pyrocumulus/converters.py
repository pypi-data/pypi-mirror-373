# Copyright 2013-2015, 2017 Juca Crispim <juca@poraodojuca.net>

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

import asyncio
import re
import copy
import json
import inspect
import warnings
from bson.objectid import ObjectId
from bson.dbref import DBRef
from datetime import datetime
from mongoengine.queryset import QuerySetManager
from mongomotor import Document, EmbeddedDocument
from mongomotor.fields import (ReferenceField, ListField,
                               EmbeddedDocumentField, IntField)
from pyrocumulus.parsers import get_parser


def get_converter(obj, max_depth=0):
    if isinstance(obj, Document) or isinstance(obj, EmbeddedDocument):
        return DocumentConverter(obj, max_depth)
    return QuerySetConverter(obj, max_depth)


def get_request_converter(arguments, body, model):
    return RequestConverter(arguments, body, model)


class BaseConverter:
    """
    Base class for all converters. These converters are
    meant to convert mongomotor objects - Document or
    QuerySet - or an incomming request
    """

    def __init__(self, obj, max_depth=0):
        self.obj = obj
        self.max_depth = max_depth

    def sanitize_dict(self, dict_to_sanitize):
        """
        Handle values which can't be serialized,
        like datetime.datetime.now() and ObjectId()
        """
        new_dict = copy.copy(dict_to_sanitize)

        for key, value in dict_to_sanitize.items():
            try:
                val = json.dumps(value)
            except TypeError:
                if isinstance(value, datetime):
                    val = value.strftime('%Y-%m-%d %H:%M:%S')
                    new_dict[key] = val
                elif isinstance(value, ObjectId):
                    val = str(value)
                    new_dict[key] = val
                elif isinstance(value, dict):
                    val = self.sanitize_dict(value)
                    new_dict[key] = val
                elif isinstance(value, list):
                    val = [self.sanitize_dict(v) for v in value]
                    new_dict[key] = val
                else:
                    warnings.warn('Could not serialize %s. Skipping it' % key,
                                  RuntimeWarning)
                    del new_dict[key]
        return new_dict

    def to_json(self, obj_to_convert):
        return json.dumps(obj_to_convert)


class DocumentConverter(BaseConverter):
    """
    Converts a mongomotor Document subclass
    into a dict
    """

    @asyncio.coroutine
    def to_dict(self):
        """ Converts a Document (self.obj) into a dict
        """

        # Ok, it's ugly and I'm not proud of it...

        return_obj = {}
        obj_attrs = [attr for attr in dir(self.obj)
                     if not attr.startswith('_') and not attr == 'STRICT']
        for attr in obj_attrs:
            obj_attr = getattr(self.obj, attr)
            if inspect.isawaitable(obj_attr):
                obj_attr = yield from obj_attr

            is_manager = isinstance(obj_attr, QuerySetManager)

            attr2compare = None if is_manager else getattr(
                self.obj.__class__, attr)

            is_dbref = False if is_manager else isinstance(attr2compare, DBRef)
            is_ref = False if is_manager else isinstance(
                attr2compare, ReferenceField)
            is_list = False if is_manager else isinstance(
                attr2compare, ListField)
            is_embed = False if is_manager else isinstance(
                attr2compare, EmbeddedDocumentField)

            # The thing here is that we are skipping things we don't want
            # in the final dict
            if ((callable(obj_attr) or is_manager) or (
                    (is_list or is_ref or is_embed or is_dbref)
                    and self.max_depth == 0)):
                continue

            if is_ref or is_embed:
                converter = self.__class__(obj_attr,
                                           max_depth=self.max_depth - 1)
                obj_attr = yield from converter.to_dict()
            elif is_list:
                # is is a ListField, check each one to see if is necessary
                # to convert it.
                ret_list = []

                for item in obj_attr:
                    is_ref = issubclass(type(item), Document)
                    is_embed = issubclass(type(item), EmbeddedDocument)
                    is_dbref = issubclass(type(item), DBRef)
                    if is_ref or is_embed:
                        converter = type(self)(item,
                                               max_depth=self.max_depth)
                        item = yield from converter.to_dict()
                    ret_list.append(item)
                obj_attr = ret_list

            return_obj[attr] = obj_attr

        return return_obj

    @asyncio.coroutine
    def to_json(self):
        dict_to_convert = yield from self.to_dict()
        dict_to_convert = self.sanitize_dict(dict_to_convert)
        return super(DocumentConverter, self).to_json(dict_to_convert)


class QuerySetConverter(BaseConverter):
    """
    Converts a QuerySet instance into a list of
    dictionaries
    """

    @asyncio.coroutine
    def to_dict(self):
        queryset_list = []
        while (yield from self.obj.fetch_next):
            document = self.obj.next_object()
            converter = DocumentConverter(document, max_depth=self.max_depth)
            obj_dict = yield from converter.to_dict()
            queryset_list.append(obj_dict)
        queryset_dict = {'items': queryset_list,
                         'quantity_items': len(queryset_list)}
        return queryset_dict

    @asyncio.coroutine
    def to_json(self):
        mydict = yield from self.to_dict()
        queryset_dict = self.sanitize_dict(mydict)
        return super(QuerySetConverter, self).to_json(queryset_dict)


class RequestConverter(BaseConverter):
    """
    Merges the elements of the request body and arguments into
    one dictionary.
    """

    def __init__(self, arguments, body, model):
        """
        :param arguments: The request's arguments.`.
        :param body: Request body. It must by a json.
        :param model: model from a request handler - a mongomotor document.
        """

        if body:
            self.body = json.loads(body.decode())
            obj = self.body
        else:
            self.body = {}
            obj = {}

        self.arguments = arguments
        obj.update(arguments)
        super(RequestConverter, self).__init__(obj)
        self.parsed_model = get_parser(model)

    def to_json(self):
        raise NotImplementedError

    @asyncio.coroutine
    def _parse(self, obj, care_about_lists=False):
        """Parse request's arguments or body and returns
        a dictionary to be used with mongomotor queryset."""

        arguments = {}
        for key, value in obj.items():

            field = self._get_field(key)
            if not field:
                # if the parameter is not a field in the model
                # we dont touch it.
                arguments[key] = value
                continue

            if care_about_lists:
                is_list = self._is_listfield(key)
                # keep as a list only what is a ListField
                if not is_list:
                    value = value[0].decode()
                else:
                    value = [v.decode() for v in value]

            if isinstance(field['type'], IntField):
                value = int(value)

            is_reference = field['is_reference']
            is_join = is_reference and '__' in key
            is_date = self._is_date(value)
            is_bool = field['is_bool']

            # handling ReferenceFields. If the param is
            # `thing__id`, and there's a ReferenceField
            # called `thing`, let's try to get an
            # instance of the referenced object
            if is_reference and is_join:
                key, value = yield from self._get_reference(key, value)

            # handling datetime. The value must be a string like
            # YYYY-mm-dd HH:MM:SS. Will be turned into a datetime object
            elif is_date:
                value = self._handle_date(is_date)

            elif is_bool and isinstance(value, str):
                value = self._get_bool_value(value)

            arguments[key] = value

        return arguments

    @asyncio.coroutine
    def get_query(self):
        """
        Parse request arguments and create dict containing
        only params to be passed to mongomotor queryset
        get() or filter()
        """
        r = yield from self._parse(self.arguments, care_about_lists=True)
        return r

    @asyncio.coroutine
    def get_body(self):
        """
        Parse request params and create dict containing
        only params to be passed to mongomotor queryset
        get() or filter()
        """

        r = yield from self._parse(self.body)
        return r

    def _is_date(self, value):
        pattern_string = '(\d+)-(\d+)-(\d+)\s(\d+):(\d+):(\d+)'
        datetime_pattern = re.compile(pattern_string)

        is_date = False if not isinstance(value, str) else \
            datetime_pattern.match(value) or False
        return is_date

    def _handle_date(self, date):
        datelist = [int(i) for i in date.groups()]
        value = datetime(*datelist)
        return value

    def _is_listfield(self, key):
        return key in [f['name'] for f in self.parsed_model.lists]

    def _get_field(self, key):
        if '__' in key:
            key = key.split('__')[0]

        return self.parsed_model.get(key)

    @asyncio.coroutine
    def _get_reference(self, key, value):
        param_name = key.split('__')[1]
        # key == refname
        key = key.split('__')[0]
        ref_class = self.parsed_model.get(key)['reference_class']
        try:
            kwargs = {param_name: value}
            value = yield from ref_class.objects.get(**kwargs)
        except ref_class.DoesNotExist:
            value = ref_class(**kwargs)

        return key, value

    def _get_bool_value(self, bool_value):
        table = {'0': False,
                 'false': False,
                 '1': True,
                 'true': True}
        return table.get(bool_value.lower(), bool_value)
