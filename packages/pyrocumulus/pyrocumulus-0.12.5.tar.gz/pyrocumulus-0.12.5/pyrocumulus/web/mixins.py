# -*- coding: utf-8 -*-

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
# along with pyrocumulus. If not, see <http://www.gnu.org/licenses/>.

import asyncio
import re
from tornado.web import HTTPError
from pyrocumulus.auth import AccessToken, PyrocumulusBadToken


class BasicAPIKeyAuthMixin:
    """Mixin for api with authentication. Requires an ``api_key`` parameter
    on the incomming request and validates if the key is valid and
    if it has enougth permissions."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.token = None
        self.access_token = None
        self.referrer_domain = None

    def _get_token(self):

        try:
            token = self.request.headers['Authorization']
        except KeyError:
            raise HTTPError(401, 'No Authorization header found')

        try:
            token = token.split('token: ')[1]
        except IndexError:
            raise HTTPError(401, 'Mal-formed token')
        return token

    def _get_domain(self, url):
        pattern = re.compile('http[s|]://(.*?)/')
        try:
            domain = re.findall(pattern, url)[0]
        except IndexError:
            domain = None
        except TypeError:
            # It is not string or buffer
            domain = None

        return domain

    @asyncio.coroutine
    def check_perms(self, token):
        """Checks if ``token`` is a valid one and if it has
        permissions for the referrer. If it is valid,
        continues the super() line.

        :param token: The auth token (the ``api_key`` param)."""

        try:
            access_token = yield from AccessToken.get_by_token(token)
        except (AccessToken.DoesNotExist, PyrocumulusBadToken):
            raise HTTPError(401, 'bad api_key')

        referrer = self.request.headers.get('Referer', '')
        self.referrer_domain = self._get_domain(referrer)
        domains = access_token.domains

        if domains and self.referrer_domain not in domains:

            raise HTTPError(401, 'Not enough perms')
        return access_token

    @asyncio.coroutine
    def async_prepare(self):
        """Checks if the request has an api_key param and if the
        key has enough permissions."""

        if not self.request.method.lower() == 'options':
            self.token = self._get_token()
            self.access_token = yield from self.check_perms(self.token)

        r = yield from super().async_prepare()
        return r


class RestAPIAuthMixin(BasicAPIKeyAuthMixin):

    @asyncio.coroutine
    def check_perms(self, token):
        """ Check token's permissions on self.model
        """

        access_token = yield from super().check_perms(token)

        needed_perms = {'get': 'r', 'put': 'u', 'delete': 'd', 'post': 'c'}

        reqmethod = self.request.method.lower()
        needed_perm = needed_perms[reqmethod]

        perms = yield from access_token.get_perms(self.model)
        if needed_perm not in perms:
            raise HTTPError(401, 'Not enough perms')

        return access_token


class ReadOnlyMixin:

    def __getattribute__(self, attrname):
        if attrname in ['post', 'put', 'delete']:
            return self.deny_method
        else:
            return super().__getattribute__(attrname)

    def deny_method(self, operation):
        raise HTTPError(405)
