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

from importlib import import_module
from tornado.web import Application
from tornado.web import URLSpec
from pyrocumulus.conf import settings
from pyrocumulus.utils import fqualname
from pyrocumulus.web.urlmappers import DocumentURLMapper
from pyrocumulus.web.handlers import get_rest_handler
from pyrocumulus.web.handlers import StaticFileHandler


class PyroApplication(Application):
    """Base application for pyrocumulus applications."""

    @property
    def urls(self):
        urls = []
        for rule in self.default_router.rules:
            urls += rule.target.rules
        return urls


class RestApplication(PyroApplication):

    def __init__(self, *models, url_prefix='', auth=False, readonly=False,
                 handlerfactory=None):
        self.models = models
        self.handlerfactory = handlerfactory or get_rest_handler
        self.url_prefix = url_prefix
        self.auth = auth
        self.readonly = readonly

        self._handlers_map = self._get_handlers_map()
        self._auto_urls = self.create_urls()

        self._tornado_opts = getattr(settings, 'TORNADO_OPTS', {})
        super().__init__(self._auto_urls, **self._tornado_opts)

    def _get_handlers_map(self):
        handlers_map = {}

        for model in self.models:
            key = fqualname(model)
            value = self.handlerfactory(model, auth=self.auth,
                                        readonly=self.readonly)
            handlers_map[key] = value
        return handlers_map

    def create_urls(self):
        """
        Returns the urls created based on ``self.models``.
        """
        urls = []
        for document in self.models:
            request_handler = self._handlers_map[fqualname(document)]
            mapper = DocumentURLMapper(document, request_handler,
                                       self.url_prefix)
            urls += mapper.get_urls()
        return urls


class StaticApplication(PyroApplication):

    def __init__(self):

        static_url = URLSpec(settings.STATIC_URL + '(.*)', StaticFileHandler,
                             dict(static_dirs=settings.STATIC_DIRS))

        super(StaticApplication, self).__init__([static_url])


def get_main_application():
    """
    Returns an Application instance to be used as the main one.
    It uses all applications listed in the APPLICATIONS settings
    variable.

    Using the urls of these applications, creates a new
    `tornado.web.application.Application`
    instance with all urls foundd in the applications.
    """

    urls = []
    for app in settings.APPLICATIONS:
        urls += _get_application_urls(app)

    tornado_opts = getattr(settings, 'TORNADO_OPTS', {})
    main_app = PyroApplication(urls, **tornado_opts)
    return main_app


def _get_application_urls(app_name):
    """
    Returns a list of urls to a given application name.
    It must be a fully qualified name for the application.
    """
    module_name, app_name = app_name.rsplit('.', 1)
    urls = []
    try:
        module = import_module(module_name)
        application = getattr(module, app_name)
        if application:
            urls += application.urls
    except ImportError:
        pass

    return urls
