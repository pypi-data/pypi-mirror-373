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
# along with pyrocumulus.  If not, see <http://www.gnu.org/licenses/>.

from importlib import import_module
import logging
import os
import sys
from tornado import ioloop
from tornado.httpserver import HTTPServer
from tornado.platform.asyncio import AsyncIOMainLoop
from pyrocumulus.utils import get_value_from_settings
from pyrocumulus.commands.base import BaseCommand
from pyrocumulus.web.applications import get_main_application


class RunTornadoCommand(BaseCommand):
    user_message = 'Starting tornado webserver. Listen port {}'
    description = "command to start a tornado server"
    user_options = [
        # some.application.instance
        {'args': ('--application',),
         'kwargs': {'help': 'application module'}},
        # --daemonize
        {'args': ('--daemonize',),
         'kwargs': {'default': False, 'help': 'run as a daemon',
                    'action': 'store_true'}},
        # --port 9876
        {'args': ('--port',),
         'kwargs': {'default': None, 'help': 'port to listen',
                    'nargs': '?'}},
        # --stdout some/file.log
        {'args': ('--stdout',),
         'kwargs': {'default': 'logs/stdout.log', 'help': 'stdout log file',
                    'nargs': '?'}},
        # --stderr some/file.log
        {'args': ('--stderr',),
         'kwargs': {'default': 'logs/stderr.log', 'help': 'stderr log file',
                    'nargs': '?'}},
        # --pidfile some/file.pid
        {'args': ('--pidfile',),
         'kwargs': {'default': None, 'help': 'stderr log file',
                    'nargs': '?'}},
        # --kill
        {'args': ('--kill',),
         'kwargs': {'default': False, 'help': 'kill tornado server',
                    'action': 'store_true'}},
        # --log-level
        {'args': ('--loglevel',),
         'kwargs': {'default': 'info', 'help': 'Log level',
                    'nargs': '?'}},

    ]

    def run(self):
        self.port = self.get_port()
        self.pidfile = self.pidfile or 'tornado-%i.pid' % self.port

        if self.kill:
            return self.killtornado()

        if self.daemonize:
            self.run_as_a_daemon()
            self.close_file_descriptors()
            self.redirect_stdout_stderr()
            self._write_to_file(self.pidfile, str(os.getpid()))

        AsyncIOMainLoop().install()
        ioloop_inst = ioloop.IOLoop.instance()
        self.application = self.get_application()

        self._set_log_level()
        logger = logging.getLogger()
        msg = self.user_message.format(self.port)
        logger.log(logging.INFO, msg)
        tornado_opts = get_value_from_settings('HTTP_SERVER_OPTS', {})
        server = HTTPServer(self.application, **tornado_opts)
        server.listen(self.port)
        ioloop_inst.start()

    def killtornado(self):
        """
        Kills tornado server if pidfile is found
        """
        pid = None
        try:
            pid = int(self._read_file(self.pidfile))
        except IOError:
            print('Tornado pid file not found. Exiting')
        except TypeError:
            print('Bad content on pid file. Exiting')

        if pid is None:
            return False

        os.kill(pid, 9)
        print('Tornado server killed')
        os.remove(self.pidfile)
        return True

    def run_as_a_daemon(self):
        """
        Fork twice and setsid
        """
        self._do_fork()
        os.setsid()
        self._do_fork()

    def _set_log_level(self):
        logging.basicConfig(level=getattr(logging, self.loglevel.upper()))

    def close_file_descriptors(self):
        """
        Closes stdin
        """
        # the `canonical` way of doing this is to close
        # all file descriptors, using RLIMIT_NOFILE.
        # But doing it here, crashes tornado server when
        # starting it. I don't know why
        # """
        # Closes all file descriptors possibly handled by
        # the parent process
        # """

        # import resource
        # limit = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
        # for fd in range(limit):
        #     try:
        #         os.close(fd)
        #     except OSError:  # pragma: no cover
        #         pass

        sys.stdin.close()

    def redirect_stdout_stderr(self):
        """
        Redirect stdout and stderr to /dev/null or to a
        log file
        """
        for fd in sys.stdout, sys.stderr:
            fd.flush()

        if not os.path.exists(os.path.dirname(self.stdout)):
            os.makedirs(os.path.dirname(self.stdout))

        if not os.path.exists(os.path.dirname(self.stderr)):
            os.makedirs(os.path.dirname(self.stderr))

        stdout_fh = open(self.stdout, 'a', 1)
        stderr_fh = open(self.stderr, 'a', 1)
        os.dup2(stdout_fh.fileno(), sys.stdout.fileno())
        os.dup2(stderr_fh.fileno(), sys.stderr.fileno())

    def _try_create_required_dirs_and_files(self):
        dirs = []
        dirs.append(os.path.dirname(self.stdout))
        dirs.append(os.path.dirname(self.stderr))

        for directory in dirs:
            try:
                os.mkdir(directory)
            except OSError:
                pass

    def _do_fork(self):
        pid = os.fork()
        if pid != 0:
            sys.exit(0)

    def _read_file(self, fname):
        with open(fname) as f:
            content = f.read()
        return content

    def _write_to_file(self, fname, content):
        with open(fname, 'w') as f:
            f.write(content)

    def get_application(self):
        """
        application is an instance of tornado.web.Application
        and will be used in this tornado instance.
        """
        if not self.application:
            main_app = get_main_application()

            return main_app

        app_path = self.application
        module_name = '.'.join(app_path.split('.')[:-1])
        app_name = app_path.split('.')[-1]
        module = import_module(module_name)
        app = getattr(module, app_name)
        return app

    def get_port(self):
        """
        Get the port to tornado server listen. If --port command line
        option, this port will be used. If not command line option
        get it from TORNADO_PORT settings variable. If not TORNADO_PORT
        on settings, use 8888
        """
        settings_port = get_value_from_settings('TORNADO_PORT', 8888)
        port = self.port or settings_port
        return int(port)
