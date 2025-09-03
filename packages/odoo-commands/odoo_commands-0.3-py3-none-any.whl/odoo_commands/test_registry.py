import time

from IPython import start_ipython

from odoo_commands.database_mock import CursorMock, FakeDatabase

s1 = time.time()

import logging
import mock

import odoo
from odoo.modules.registry import Registry
from odoo.tools import config

s2 = time.time()
print('01 >>', format(s2 - s1, '.2f'))


class MockRegistry(Registry):
    # def init(self, db_name):
    #     super().init(db_name)
    #     self._db = None

    def setup_signaling(self):
        print('setup_signaling')


class PostgresCursorMock:
    pass


class PostgresConnectionMock:
    def cursor(self):
        return PostgresCursorMock()


# class ConnectionPoolMock(ConnectionPool):
class ConnectionPoolMock:
    def __init__(self, maxconn=64):
        self._maxconn = max(maxconn, 1)

    def borrow(self, connection_info):
        return PostgresConnectionMock()


class ConnectionMock:
    pass

_logger = logging.getLogger(__name__)


def is_initialized(cr):
    return True

def reset_modules_state(dbname):
    print('reset_modules_state')

Registry.setup_signaling = lambda self: None
import odoo.modules
odoo.modules.reset_modules_state = lambda dbname: None


def start_env():
    t01 = time.time()
    config.parse_config([])
    # config.parse_config(['-d', 'prod2'])
    # config.parse_config(['--workers', '1'])
    odoo.cli.server.report_configuration()
    odoo.service.server.start(preload=[], stop=True)

    t02 = time.time()
    print('1 >>>', format(t02 - t01, '.2f'))

    class CursorDbMock(CursorMock):
        db = FakeDatabase(lambda self: ['base',])

    # with mock.patch('odoo.sql_db.db_connect', db_connect):
    with mock.patch('odoo.sql_db.Cursor', CursorDbMock):
        t03 = time.time()
        print('2 >>>', format(t03 - t02, '.2f'))

        # registry = odoo.registry('none')
        # registry = Registry('none')
        # cr = registry.cursor()
        # env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
        # registry = MockRegistry('none')

        with odoo.api.Environment.manage(), odoo.registry('none').cursor() as cr:
            env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
            t04 = time.time()
            print('3 >>>', format(t04 - t03, '.2f'))
            print('>>>>>', format(t04 - s1, '.2f'))
            start_ipython(argv=[], user_ns={'env': env})
            # yield env

        # with registry.cursor() as cr:
        #     env = odoo.api.Environment(cr, 1, {})

        # with odoo.api.Environment.manage():
            # registry = odoo.registry('none')
            # registry = MockRegistry('none')

s10 = time.time()
print('02 >>', format(s10 - s2, '.2f'))

start_env()
