import logging
import time
from functools import lru_cache

import mock
from odoo.modules.registry import Registry

from odoo_commands.database_mock import cursor_mock_class, cursor

s1 = time.time()

import odoo
from odoo.api import Environments

s2 = time.time()
print('S >>', format(s2 - s1, '.3f'))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

cr = None


class Project:
    def __init__(self):
        self._env_generator = None

    # TODO Use functools.cached_property for Python3.8+
    @property
    @lru_cache(maxsize=1)
    def env(self):
        # Keep ref on generator force close generator later
        self._env_generator = self._get_env_generator()
        return next(self._env_generator)

    def _get_env_generator(self):
        installed_modules = [
            'account',
            'analytic',
            'base',
            'product',
            'portal',
            'base_setup',
            'mail',
            'http_routing',
            'decimal_precision',
            'web',
            'bus',
            'web_tour',
            'sale',
            'sales_team',
            'web_planner',
        ]

        with mock.patch('odoo.sql_db.Cursor', cursor_mock_class(lambda self: ['base'])):
            with odoo.api.Environment.manage():
                with odoo.registry('soma').cursor() as cr:
                    print('2')
                    yield odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})

    def payload(self):
        Registry.in_test_mode = lambda self: True

        print('1')
        print(self.env)
        print('3')
        print('10')


project = Project()
project.payload()
