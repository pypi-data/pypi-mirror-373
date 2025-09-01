# -*- coding: utf-8 -*-

# Copyright 2013-2016 Juca Crispim <juca@poraodojuca.net>

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

from collections import OrderedDict
from mongoengine.base.fields import BaseField
from mongomotor.fields import (ReferenceField, ComplexBaseField,
                               EmbeddedDocumentField, ListField,
                               BooleanField)


def get_parser(model):
    return DocumentParser(model)


class DocumentParser:
    """
    Parse a Document and return a dict with {'field_name': field_type}.
    ReferenceFields, EmbeddedDocumentFields and ListFields are returned
    in repareted keys.
    """

    def __init__(self, model):
        self.model = model
        self._model_fields = self._get_model_fields()
        self._fields_info = OrderedDict()

    def _get_document_field_names(self):
        """Returns the names of the fields in the model document."""

        fields_names = [i for i in dir(self.model) if not i.startswith('_')
                        and not i == 'objects' and i != 'STRICT' and
                        isinstance(getattr(self.model, i), BaseField)]
        return fields_names

    def _get_model_fields(self):
        """Returns a list of tuples each one consistin in
        (field_name, field_type)."""

        model_fields = []
        fields_names = self._get_document_field_names()
        for name in fields_names:
            field = getattr(self.model, name)
            if callable(field):
                continue

            model_fields.append((name, field))

        return model_fields

    @property
    def fields(self):
        """Generator to iterate over the fields in the model document.
        each object ``yield``ed by the generator is a dictionary with
        information about the field."""

        # if self._fields_info:
        #     return (field for field in self._fields_info.values())

        model_fields = [f for f in self._model_fields if f[0] != 'pk']

        ordered = sorted(model_fields, key=lambda f: f[1].creation_counter)
        for field in ordered:

            is_ref = isinstance(field[1], ReferenceField) or (
                isinstance(field[1], ComplexBaseField) and
                isinstance(field[1].field, ReferenceField))

            is_embed = isinstance(field[1], EmbeddedDocumentField) or (
                isinstance(field[1], ComplexBaseField) and
                isinstance(field[1].field, EmbeddedDocumentField))

            is_bool = isinstance(field[1], BooleanField)

            field_info = {'name': field[0],
                          'type': field[1],
                          'required': field[1].required,
                          'primary_key': field[1].primary_key,
                          'unique': field[1].unique,
                          'is_reference': is_ref,
                          'is_bool': is_bool}

            if is_ref:
                try:
                    # for ReferenceField
                    ref_class = field[1].document_type
                except AttributeError:
                    # for ComplexBaseField
                    ref_class = field[1].field.document_type

                field_info.update({'reference_class': ref_class})

            if is_embed:
                try:
                    embed_class = field[1].document_type
                except AttributeError:
                    embed_class = field[1].field.document_type

                field_info.update({'embedded_class': embed_class})

            self._fields_info[field_info['name']] = field_info
            yield field_info

    @property
    def references(self):
        """Generator to iterate over the references in the model document."""

        for field in self.fields:
            if field['is_reference']:
                yield field

    @property
    def lists(self):
        """A generator to iterate over list fields of the model document."""

        for field in self.fields:
            if field['type'] == ListField or isinstance(
                    field['type'], ListField):
                yield field

    @property
    def embeddeds(self):
        """Generator to iterate over embedded documents of the model
        document."""

        for field in self.fields:
            is_embed = isinstance(field['type'], EmbeddedDocumentField) or (
                isinstance(field['type'], ComplexBaseField) and
                isinstance(field['type'].field, EmbeddedDocumentField))

            if is_embed:
                yield field

    def get(self, field_name):
        """Returns information about one field.
        :param field_name: The field name."""

        if not self._fields_info:
            # just to populate it
            list(self.lists)

        return self._fields_info.get(field_name)
