# -*- coding: utf-8 -*-

import warnings
from pyrocumulus.web.handlers import (ModelHandler, RestHandler,
                                      EmbeddedDocumentHandler,
                                      StaticFileHandler, get_rest_handler,
                                      HTTPError, ReadOnlyRestHandler,
                                      RequestHandler)

make_pyflakes_happy = [ModelHandler, RestHandler,
                       EmbeddedDocumentHandler, StaticFileHandler,
                       get_rest_handler]
del make_pyflakes_happy

msg = ' '.join(["pyrocumulus.request_handlers is deprecated.",
                "Use pyrocumulus.handlers instead"])

warnings.warn(msg, DeprecationWarning)
