#-*- coding: utf-8 -*-

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

from mongomotor.connection import connect, disconnect
from pyrocumulus.conf import get_settings_module


class MongoConnection(object):

    def __init__(self, db=None, host=None, port=None, db_section='default'):
        if not (db or host or port):
            settings = get_settings_module().DATABASE[db_section]
        else:
            settings = {'db': db, 'host': host, 'port': port}
        self.settings = {}
        for key, value in settings.items():
            self.settings[key.lower()] = value
            setattr(self, key.lower(), value)

        self.settings['async_framework'] = 'asyncio'
        self.connection = None

    def connect(self):
        self.connection = connect(**self.settings)

    def disconnect(self):
        disconnect()
        self.connection = None
