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

import asyncio
import base64
import uuid
import bcrypt
from mongomotor import Document
from mongomotor.fields import ReferenceField, StringField, ListField
from pyrocumulus.exceptions import PyrocumulusBadToken
from pyrocumulus.utils import bcrypt_string, fqualname


# Models for basic auth
class AccessToken(Document):
    SALT_ROUNDS = 8

    name = StringField()
    token_id = StringField(required=True)
    token = StringField(required=True)
    domains = ListField(StringField())

    async def generate_token(self):
        # first, the id
        token_id = str(uuid.uuid4())
        token = uuid.uuid4().hex
        crypto_token = bcrypt_string(token, bcrypt.gensalt(self.SALT_ROUNDS))
        final = base64.b64encode('{}:{}'.format(
            token_id, token).encode()).decode()
        self.token_id = token_id
        self.token = crypto_token
        await self.save()
        return final

    def check_token(self, token):
        valid = bcrypt.checkpw(token.encode(), self.token.encode())
        if not valid:
            raise PyrocumulusBadToken
        return valid

    @classmethod
    @asyncio.coroutine
    def get_by_token(cls, token):
        try:
            token = base64.b64decode(token.encode()).decode()
        except UnicodeDecodeError:
            # this happens when a bad base64 token is sent.
            raise PyrocumulusBadToken
        token_id, token = token.split(':')
        access_token = yield from cls.objects.get(token_id=token_id)
        access_token.check_token(token)
        return access_token

    @asyncio.coroutine
    def save(self):
        token = None
        if not self.token:
            token = yield from self.generate_token()
        yield from super().save()
        return token

    @asyncio.coroutine
    def get_perms(self, model):
        """ Returns the permissions for this token on a given model.
        :param model: mongomotor.Document instance or fqualname
        """

        if not isinstance(model, str):
            model = fqualname(model)

        perms = Permission.objects.filter(access_token=self, model=model)
        perms_list = []
        perms = yield from perms.to_list()
        for perm in perms:
            perms_list += list(perm.perms)

        perms = set(perms_list)
        return perms

    @asyncio.coroutine
    def has_create_perm(self, model):
        perms = yield from self.get_perms(model)
        return 'c' in perms

    @asyncio.coroutine
    def has_retrieve_perm(self, model):
        perms = yield from self.get_perms(model)
        return 'r' in perms

    @asyncio.coroutine
    def has_update_perm(self, model):
        perms = yield from self.get_perms(model)
        return 'u'in perms

    @asyncio.coroutine
    def has_delete_perm(self, model):
        perms = yield from self.get_perms(model)
        return 'd' in perms


class Permission(Document):
    access_token = ReferenceField(AccessToken, required=True)
    # model is pyrocumulus.utils.fqualname(ModelClass)
    model = StringField(required=True)
    # perms are 'r' for retrieve, 'c' for create, 'u' for update
    # and 'd' for delete. The perms string can be any combination of these
    # 4 letters.
    perms = StringField(required=True)

    @classmethod
    @asyncio.coroutine
    def create_perms_to(cls, access_token, model, perms):
        """ Creates a Permission instance to ``token`` related to ``model``.
        :param access_token: AccessToken instance
        :param model: class or fqualname
        :param perms: perms to apply ('r', 'c', 'u', 'd')
        """

        if not isinstance(model, str):
            model = fqualname(model)

        perms = cls(access_token=access_token, model=model, perms=perms)
        yield from perms.save()
        return perms
