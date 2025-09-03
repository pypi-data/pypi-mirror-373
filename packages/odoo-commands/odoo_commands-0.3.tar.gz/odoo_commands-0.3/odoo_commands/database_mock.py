import datetime

from odoo_commands.project import OdooModule, OdooModuleSet
from functools import lru_cache

SUPERUSER_ID = 1

class FakeDatabase:
    table_existing_query = """
        SELECT c.relname
          FROM pg_class c
          JOIN pg_namespace n ON (n.oid = c.relnamespace)
         WHERE c.relname IN %s
           AND c.relkind IN ('r', 'v', 'm')
           AND n.nspname = current_schema
    """

    read_module_fields_query = """SELECT "ir_module_module"."id" as "id", "ir_module_module"."name" as "name", "ir_module_module"."category_id" as "category_id", "ir_module_module"."shortdesc" as "shortdesc", "ir_module_module"."summary" as "summary", "ir_module_module"."description" as "description", "ir_module_module"."author" as "author", "ir_module_module"."maintainer" as "maintainer", "ir_module_module"."contributors" as "contributors", "ir_module_module"."website" as "website", "ir_module_module"."latest_version" as "latest_version", "ir_module_module"."published_version" as "published_version", "ir_module_module"."url" as "url", "ir_module_module"."sequence" as "sequence", "ir_module_module"."auto_install" as "auto_install", "ir_module_module"."state" as "state", "ir_module_module"."demo" as "demo", "ir_module_module"."license" as "license", "ir_module_module"."menus_by_module" as "menus_by_module", "ir_module_module"."reports_by_module" as "reports_by_module", "ir_module_module"."views_by_module" as "views_by_module", "ir_module_module"."application" as "application", "ir_module_module"."icon" as "icon", "ir_module_module"."to_buy" as "to_buy", "ir_module_module"."create_uid" as "create_uid", "ir_module_module"."create_date" as "create_date", "ir_module_module"."write_uid" as "write_uid", "ir_module_module"."write_date" as "write_date" FROM "ir_module_module" WHERE "ir_module_module".id IN %s"""

    module_table_fields = [
        'id',
        'name',
        'category_id',
        'shortdesc',
        'summary',
        'description',
        'author',
        'maintainer',
        'contributors',
        'website',
        'latest_version',
        'published_version',
        'url',
        'sequence',
        'auto_install',
        'state',
        'demo',
        'license',
        'menus_by_module',
        'reports_by_module',
        'views_by_module',
        'application',
        'icon',
        'to_buy',
        'create_uid',
        'create_date',
        'write_uid',
        'write_date',
    ]

    def __init__(self, installed_modules: OdooModuleSet):
        self.data = {}
        self.installed_modules = installed_modules
        self.fill_module_table(installed_modules)

    @staticmethod
    def _module_vals(module: OdooModule):
        return {
            'name': module.name,
            'shortdesc': module.shortdesc,
            'summary': module.summary,
            'description': module.description,
            'author': module.author,
            'maintainer': module.maintainer,
            'contributors': module.contributors,
            'website': module.website,
            'latest_version': module.version,
            'published_version': module.version,
            'url': module.live_test_url,
            'sequence': module.sequence,
            'auto_install': module.auto_install,
            'demo': None,
            'license': None,
            'menus_by_module': None,
            'reports_by_module': None,
            'views_by_module': None,
            'application': module.application,
            'icon': module.icon,
            'to_buy': module.to_buy,
        }

    def fill_module_table(self, installed_modules: OdooModuleSet):
        module_data = []
        now = datetime.datetime.now()
        for record_id, module in enumerate(installed_modules, start=1):
            module_vals = self._module_vals(module)
            module_vals.update({
                'id': record_id,
                'category_id': None,
                'state': 'installed',
                'create_uid': SUPERUSER_ID,
                'create_date': now,
                'write_uid': SUPERUSER_ID,
                'write_date': now,
            })
            module_data.append(module_vals)

        self.data['ir_module_module'] = module_data

    def execute(self, query, params) -> list[tuple | dict]:
        if query in {
            # self.table_existing_query,
            "SELECT proname FROM pg_proc WHERE proname='unaccent'",
            "SELECT * FROM ir_model_fields WHERE state='manual'",
            # Odoo 15
            "SELECT proname FROM pg_proc WHERE proname='word_similarity'",
            "SET SESSION lock_timeout = '15s'",
        }:
            return []

        if (query, params) in (
            ('SELECT * FROM ir_model WHERE state=%s', ['manual']),
        ):
            return []

        if query == self.table_existing_query and params == [('ir_module_module',)]:
            return [(1,)]

        if (
            query == "SELECT name from ir_module_module WHERE state IN %s"
            and params == (('installed', 'to upgrade', 'to remove'),)
        ):
            return [(module.name,) for module in self.installed_modules]

        # Odoo 15
        if query == 'SELECT "ir_module_module".id FROM "ir_module_module" WHERE ("ir_module_module"."state" = %s) ORDER BY  "ir_module_module"."name"  ':
            if params == ['installed']:
                return self.select('ir_module_module', ['id'], sort_key=lambda x: x['name'])

        if query == self.read_module_fields_query:
            return self.select('ir_module_module', self.module_table_fields, lambda x: x['id'] in params)

        if query == "SELECT name from ir_module_module WHERE state IN ('to install', 'to upgrade')":
            return []

        if query == "SELECT name, id, state, demo AS dbdemo, latest_version AS installed_version  FROM ir_module_module WHERE name IN %s":
            result = []
            for module in self.modules:
                if module['name'] in params:
                    module_copy = module.copy()
                    module_copy['dbdemo'] = module_copy.pop('demo')
                    result.append(module_copy)
            return result

        if query == 'select digits from decimal_precision where name=%s':
            return self.decimal_precision(params)

        # modules/loading.py:reset_modules_state
        if query in {
            "UPDATE ir_module_module SET state='installed' WHERE state IN ('to remove', 'to upgrade')",
            "UPDATE ir_module_module SET state='uninstalled' WHERE state='to install'",
        }:
            return []

        # ResLang._check_active
        if query == 'SELECT count(1) FROM "res_lang" WHERE ("res_lang"."active" = %s)':
            return [(1,)]

        # No test mode
        if query == "SELECT sequence_name FROM information_schema.sequences WHERE sequence_name='base_registry_signaling'":
            return [('base_registry_signaling',)]

        if query == """ SELECT base_registry_signaling.last_value,
                                  base_cache_signaling.last_value
                           FROM base_registry_signaling, base_cache_signaling""":
            return [(1, 1)]

        if query == "SELECT value FROM ir_config_parameter WHERE key = %s":
            if params == ['crm.pls_fields']:
                return [('phone_state,email_state',)]

        if query == ('SELECT "ir_act_report_xml".id FROM "ir_act_report_xml"'
                     ' WHERE ("ir_act_report_xml"."report_type" = %s) ORDER BY  "ir_act_report_xml"."name"  '):
            if params == ['py3o']:
                return []

        raise NotImplementedError(f'Unknown SQL query:\n{query}\n\nparams: {params}')

    def select(self, table, fields, condition=lambda x: True, sort_key=None, row_type=tuple):
        records = filter(condition, self.data[table])

        if sort_key:
            records = sorted(records, key=sort_key)

        result = []
        if row_type is tuple:
            for record in records:
                result.append(tuple(record[field] for field in fields))
        elif row_type is dict:
            for record in records:
                result.append({field: record[field] for field in fields})
        else:
            raise ValueError(f'Incorrect row_type: {row_type}')

        return result

    @property
    @lru_cache(maxsize=1)
    def modules(self):
        return [
            {
                'id': 1,
                'name': module.name,
                'state': 'installed',
                'dbdemo': False,
                'installed_version': '11.0.1.3',
            }
            for module_id, module in enumerate(self.installed_modules, start=1)
        ]

    def decimal_precision(self, names):
        return [(2,)] * len(names)


from odoo.sql_db import BaseCursor

class CursorMock(BaseCursor):
    """Mocked Odoo cursor class"""
    databases = {}

    def __init__(self, pool, dbname, dsn, serialized=True):
        self.dbname = dbname
        self.sql_log_count = 0
        self.transaction = None

    def execute(self, query, params=None, log_exceptions=None):
        database = self.databases.get(self.dbname)
        if not database:
            raise ValueError(f'There is no fake database: {self.dbname}')

        self.result = database.execute(query, params)

    @staticmethod
    def _convert_to_tuple(row):
        if isinstance(row, tuple):
            return row
        elif isinstance(row, dict):
            return tuple(row.values())

        raise TypeError(f'Unexpected type: {type(row)}')

    @staticmethod
    def _convert_to_dict(row):
        if isinstance(row, tuple):
            raise ValueError('Cursor execute result is list of tuples. Unavailable convert to dict')
        elif isinstance(row, dict):
            return row

        raise TypeError(f'Unexpected type: {type(row)}')

    def _fetchone(self, convert):
        if self.result:
            print(self.result)
            return convert(self.result.pop(0))

    def _fetchall(self, convert):
        fetch_result = list(map(convert, self.result))
        self.result = []
        return fetch_result

    def fetchone(self):
        return self._fetchone(self._convert_to_tuple)

    def fetchall(self):
        return self._fetchall(self._convert_to_tuple)

    def fetchmany(self, size=None):
        raise NotImplementedError

    def dictfetchone(self):
        self._fetchone(self._convert_to_dict)

    def dictfetchall(self):
        return self._fetchall(self._convert_to_dict)

    def dictfetchmany(self):
        raise NotImplementedError

    def commit(self):
        pass

    def close(self):
        pass

    def split_for_in_conditions(self, ids, size=None):
        return ids


def cursor_mock_class(installed_module_names_callback):

    class CursorDbMock(CursorMock):
        db = FakeDatabase(installed_module_names_callback)

    return CursorDbMock
