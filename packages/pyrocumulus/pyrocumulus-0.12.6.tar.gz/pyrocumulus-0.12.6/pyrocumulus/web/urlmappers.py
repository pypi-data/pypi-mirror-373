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

from tornado.web import URLSpec
from pyrocumulus import utils
from pyrocumulus.conf import settings
from pyrocumulus.parsers import get_parser


class DocumentURLMapper:
    """
    Maps urls for an mongomotor Document. Creates urls like:

    URLSpec('url_prefix/document_name/(.*)$', RestHandler,
             dict(model=document),
             name='nameprefix.full.Name')
    """

    def __init__(self, document, request_handler, url_prefix='',
                 url_name_prefix='url'):
        """
        :param document: A mongomotor Document subclass
        :param request_handler: A tornado RequestHandler (or a subclass).
        :param url_prefix: URL prefix
        :param url_name_prefix: Prefix to url name
        """
        self.document = document
        self.document_name = self.document.__name__.lower()
        self.request_handler = request_handler
        self.url_prefix = url_prefix
        self.url_name_prefix = url_name_prefix

    @property
    def urls(self):
        r = self.get_urls()
        return r

    def get_urls(self):
        """
        Returns a list of URLSpec objects related to self.document,
        including its EmbeddedDocuments.
        """
        urls = []
        parsed_model = get_parser(self.document)
        for field in parsed_model.embeddeds:
            name = field['name']
            embedded = field['embedded_class']
            prefix = self.document_name
            if self.url_prefix:
                prefix = '%s/%s' % (self.url_prefix, prefix)
            embedded_handler = self.request_handler.embeddedhandler()
            mapper = EmbeddedDocumentURLMapper(embedded, self.document,
                                               embedded_handler,
                                               url_prefix=prefix,
                                               document_name=name)
            urls += mapper.get_urls()

        pattern = self.get_url_pattern(prefix=self.url_prefix)
        urlname = self.get_url_name()
        kwargs = self.get_handler_kwargs()
        url = URLSpec(pattern, self.request_handler, kwargs,
                      name=urlname)
        urls.append(url)

        return urls

    def get_url_name(self):
        """
        Get name for URLSpec
        """
        name = utils.fqualname(self.document)
        prefix = self.url_name_prefix
        name = '%s.%s' % (prefix, name)
        return name

    def get_handler_kwargs(self):
        """
        Get kwargs to be passed to request handler
        """
        kwargs = dict(model=self.document)
        obj_depth = getattr(self.document, 'REST_OBJECT_DEPTH', 1)
        kwargs['object_depth'] = obj_depth
        if hasattr(settings, 'CORS_ORIGINS') and settings.CORS_ORIGINS:
            kwargs.update({'cors_origins': settings.CORS_ORIGINS})

        return kwargs

    def get_url_pattern(self, prefix=''):
        """
        :param prefix: will be inserted in the pattern

        Returns a pattern to be used in the url mapping process.
        """
        pattern = '%s/(.*)' % self.document_name
        if prefix:
            pattern = '%s/%s' % (prefix, pattern)
        return pattern


class EmbeddedDocumentURLMapper(DocumentURLMapper):
    """
    URLMapper for EmbeddedDocuments. Creates urls like:

    URLSpec('url_prefix/parent_name/document_name/(.*)$',
             RestHandler, dict(model=document),
             name='full.Name')
    """

    def __init__(self, document, parent_doc, request_handler, url_prefix='',
                 document_name='', url_name_prefix='url'):
        """
        :param document: A mongomotor EmbeddedDocument subclass.
        :param parent_doc: A mongomotor Document subclass, the parent doc
        of the EmbeddedDocument.
        :param url_prefix: URL prefix
        :param request_handler: A tornado RequestHandler (or a subclass).
        :param document_name: Name to be used in URL pattern. If not name,
        self.document.__name__.lower() will be used.
        :param url_name_prefix: Prefix to url name
        """
        self.document = document
        self.parent_doc = parent_doc
        self.document_name = document_name or self.document.__name__.lower()
        self.request_handler = request_handler
        self.url_prefix = url_prefix
        self.url_name_prefix = url_name_prefix

    def get_handler_kwargs(self):
        """
        Returns the kwargs to be passed to self.request_handler
        """
        return dict(model=self.document, parent_doc=self.parent_doc)

    def get_url_name(self):
        """
        Get name for URLSpec
        """
        prefix = self.url_name_prefix
        name = utils.fqualname(self.parent_doc)
        class_name = self.document.__name__
        name = '%s.%s.%s' % (prefix, name, class_name)
        return name
