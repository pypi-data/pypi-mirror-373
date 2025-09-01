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

from importlib import import_module
import tornado
from pyrocumulus import auth
from pyrocumulus.db import MongoConnection
from pyrocumulus.commands.base import BaseCommand


class AuthCli:
    def __init__(self):
        self.connection = MongoConnection()
        self.connection.connect()
        self.ioloop = tornado.ioloop.IOLoop.instance()

    # just to make tests easier
    def print2screen(self, text):  # pragma: no cover
        print(text)

    def list_tokens(self):
        tokens = self.ioloop.run_sync(auth.AccessToken.objects.all().to_list)
        self.print2screen('id | name')
        for token in tokens:
            self.print2screen('{} | {}'.format(token.id, token.name))
        return tokens

    def add_token(self, name, domains, *perms):
        uncrypted_token, token = self.create_token(name, domains=domains)

        for model, perm in perms:
            if isinstance(model, str):
                module_name, model_name = model.rsplit('.', 1)
                module = import_module(module_name)
                model = getattr(module, model_name)

            @tornado.gen.coroutine
            def create_perms():
                yield auth.Permission.create_perms_to(token, model, perm)

            self.ioloop.run_sync(create_perms)

        self.print2screen(
            'Token successfull added!\n{}'.format(uncrypted_token))

        return uncrypted_token

    def del_token(self, uncrypted_token):

        @tornado.gen.coroutine
        def del_token():
            token = yield from auth.AccessToken.get_by_token(uncrypted_token)
            perms = yield from auth.Permission.objects.filter(
                access_token=token).to_list()
            for perm in perms:
                yield from perm.delete()

            yield from token.delete()

        self.ioloop.run_sync(del_token)

        # why is it not covered?
        self.print2screen('Token {} successfull deleted!'. format(
            uncrypted_token))  # pragma: no cover

    def create_token(self, name, domains=None):
        token = auth.AccessToken(name=name)
        uncrypted_token = self.ioloop.run_sync(token.save)
        return uncrypted_token, token


class AuthCliCommand(BaseCommand):
    user_options = [
        # action
        # action can be: [add_token|list_tokens]
        {'args': ('action',),
         'kwargs': {'help': 'Action to execute'}},

        # --token-name name
        {'args': ('--token-name',),
         'kwargs': {'help': 'Token\'s name'}},

        # --perms some.Model:rw,other.Model:w
        {'args': ('--perms',),
         'kwargs': {'default': '', 'nargs': '?',
                    'help': 'Perms to model'}},

        # --domains=some.domain.com,otherplace.net
        {'args': ('--domains',),
         'kwargs': {'default': '', 'nargs': '?',
                    'help': 'Domains allowed to use this token'}},
    ]

    def run(self):
        self.cli = AuthCli()
        self.perms = self._parse_perms(self.perms)
        self.domains = [d for d in self.domains.split(',') if d]

        if self.action == 'add_token':
            self.cli.add_token(self.token_name, self.domains, *self.perms)

        elif self.action == 'list_tokens':
            self.cli.list_tokens()

        elif self.action == 'del_token':
            self.cli.del_token(self.token)

        else:
            self.cli.print2screen('Action {} does not exist!'.format(
                self.action))

    def _parse_perms(self, perms):
        parsed = []
        if not perms:  # pragma: no cover
            return parsed
        perms = perms.split(',')
        for perm in perms:
            model, p = perm.split(':')
            parsed.append((model, p))

        return parsed
