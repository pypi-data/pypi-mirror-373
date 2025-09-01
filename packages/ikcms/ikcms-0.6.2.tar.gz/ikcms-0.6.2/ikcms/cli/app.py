import os
import fnmatch
import sys
from multiprocessing import Process
from itertools import chain
from iktomi.cli.app import App as _AppCli
from iktomi.cli.app import wait_for_code_change
from iktomi.cli.app import flush_fds
from iktomi.cli.app import MAXFD
from .base import Cli
import logging
import time
from itertools import chain
import logging

logging.basicConfig()
logger = logging.getLogger()


def iter_module_files():
    for module in sys.modules.values():
        filename = getattr(module, '__file__', None)
        if filename:
            while not os.path.isfile(filename): # pragma: no cover
                # NOTE: this code is needed for the cases of importing
                # from archive or custom importers
                # for example, if we importing from archive foo.zip
                # module named zipped, then this zipped.__file__ will equal
                # to foo.zip/zipped.py, and os.path.dirname will give us
                # file, not directory.
                # It is marked as pragma: no cover, because this code was taken
                # from werkzeug and we believe that it is tested
                filename = os.path.dirname(filename)
                if not filename:
                    break
            else:
                if filename.endswith(('.pyc', '.pyo')):
                    filename = filename[:-1]
                yield filename

def wait_for_code_change(extra_files=None, interval=1):
    mtimes = {}
    while 1:
        for filename in chain(iter_module_files(), extra_files or ()):
            try:
                mtime = os.stat(filename).st_mtime
            except OSError: # pragma: no cover
                # this is cannot be guaranteed covered by coverage because of interpreter optimization
                # see https://bitbucket.org/ned/coveragepy/issues/198/continue-marked-as-not-covered#comment-4052311

                continue

            old_time = mtimes.get(filename)
            if old_time is None:
                mtimes[filename] = mtime
            elif mtime > old_time:
                logger.info('Changes in file "%s"', filename)
                return
        time.sleep(interval)

def http_process(host, port, stdin_fdno, app_factory):
    sys.stdin = os.fdopen(stdin_fdno)
    from wsgiref.simple_server import make_server
    app = app_factory.create_app()
    host = host or app.cfg.HTTP_SERVER_HOST
    port = port and int(port) or app.cfg.HTTP_SERVER_PORT
    print('Staring HTTP server {}:{}...'.format(host, port))
    server = make_server(host, port, app)
    server.serve_forever()


class AppCli(Cli):
    name = 'app'

    def command_serve(self, host=None, port=None, cfg=''):

        stdin = os.dup(sys.stdin.fileno())
        p1 = Process(target=http_process, args=(host, port, stdin, self))
        p1.start()

        cfg = self.create_cfg(custom_cfg_path=cfg)

        extra_files = []
        file_types = ['*.py', '*.yaml']

        for root, dirnames, filenames in os.walk(cfg.ROOT_DIR):
            filenames_to_check = chain.from_iterable(
                fnmatch.filter(filenames, files) for files in file_types
            )
            for filename in filenames_to_check:
                extra_files.append(os.path.join(root, filename))

        try:
            wait_for_code_change(extra_files=extra_files)
            p1.terminate()
            p1.join()
            flush_fds()

            pid = os.fork()
            if pid:
                os.closerange(3, MAXFD)
                os.waitpid(pid, 0)
                os.execvp(sys.executable, [sys.executable] + sys.argv)
            else:
                sys.exit()

        except KeyboardInterrupt:
            print('Terminating HTTP server...')
            p1.terminate()

        sys.exit()

    def command_shell(self, level=None, cfg=''):
        kwargs = dict(custom_cfg_path=cfg)
        if level:
            kwargs['LOG_LEVEL'] = level
        app = self.create_app(**kwargs)
        return self._cli(app).command_shell()

    def shell_namespace(self, app):
        return {
            'app': app,
        }

    def _cli(self, app):
        return _AppCli(app, shell_namespace=self.shell_namespace(app))
