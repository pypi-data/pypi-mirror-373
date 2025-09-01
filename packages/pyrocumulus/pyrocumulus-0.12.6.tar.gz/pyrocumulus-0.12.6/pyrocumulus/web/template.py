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
from importlib import import_module
from tornado.template import Loader
from pyrocumulus.exceptions import TemplateNotFound
from pyrocumulus.conf import settings


class TemplateFinder:

    """
    Locates a template in the file system, looking for it
    in the directories in TEMPLATE_DIRS settings variable.
    """

    def __init__(self):
        self.template_dirs = settings.TEMPLATE_DIRS

    def find_template(self, template):
        """
        Returns the full file path for a template.
        :param template: file name with relative path.
        """

        for directory in self.template_dirs:
            template_path = os.path.join(directory, template)
            if os.path.exists(template_path):
                return template_path
        raise TemplateNotFound('Template %s not found in %s' % (
            template, ', '.join(self.template_dirs)))


class ContextManager:

    def __init__(self, request):
        self.request = request

    def get_context_processors(self):
        """
        Returns a list of context processors based on the
        CONTEXT_PROCESSORS settings variable
        """
        processors = []
        processors_names = getattr(settings, 'CONTEXT_PROCESSORS', [])
        for processor_fname in processors_names:
            module_name, processor_name = processor_fname.rsplit('.', 1)
            module = import_module(module_name)
            processor = getattr(module, processor_name)(self.request)
            processors.append(processor)
        return processors

    def get_context(self):
        """
        Returns a dict to be used as a context while
        rendering a template.
        Uses the context processors from settings
        """
        context = {}
        for processor in self.get_context_processors():
            context.update(processor())
        return context


class ContextProcessor:

    """
    A context processor is a callable that returns
    a dict to be included in the template as a contex.
    It receives a request in the constructor
    """

    def __init__(self, request):
        """
        :params request: A request from a request handler
        """
        self.request = request

    def __call__(self):
        return self.get_context()

    def get_context(self):
        """
        Returns a dict to be used as a context,
        returns {'static_url': settings.STATIC_URL}.
        Sub-classes should re-implement this method
        and returns its own context.
        """
        static_url = settings.STATIC_URL
        return {'static_url': static_url}


def render_template(template, request=None, extra_context={}):
    finder = TemplateFinder()
    dirpath, filename = finder.find_template(template).rsplit(os.sep, 1)
    loader = Loader(dirpath)
    context = ContextManager(request).get_context()
    context.update(extra_context)
    return loader.load(filename).generate(**context)
