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


import os
import unittest


class TornadoApplicationTestCase(unittest.TestCase):
    """
    Base class for tests with tornado.
    setUpClass() runs a tornado server in background
    and tearDownClass kills it.
    """

    python_exec = 'python'
    runtornado_command = 'pyromanager.py runtornado'
    application = None

    @classmethod
    def setUpClass(cls):
        super(TornadoApplicationTestCase, cls).setUpClass()
        options = ['--daemonize']
        if cls.application:
            options.append('--application %s' % cls.application)

        runtornado_cmd_line = cls._mount_runtorando_cmd_line(*options)

        os.system(runtornado_cmd_line)

    @classmethod
    def tearDownClass(cls):
        super(TornadoApplicationTestCase, cls).tearDownClass()
        options = ['--kill']
        if cls.application:
            options.append('--application %s' % cls.application)
        runtornado_cmd_line = cls._mount_runtorando_cmd_line(*options)

        os.system(runtornado_cmd_line)

    @classmethod
    def _mount_runtorando_cmd_line(cls, *options):
        options_line = ' '.join(options)
        cmd_line = '%s %s %s' % (cls.python_exec, cls.runtornado_command,
                                 options_line)

        return cmd_line
