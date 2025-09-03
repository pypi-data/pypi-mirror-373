import ast
import glob
import hashlib
import os
import datetime
import runpy
import subprocess
from functools import lru_cache
from pprint import pprint
from typing import Set, Sequence
import time

# import odoo

# from click_odoo_contrib.initdb import _walk

import logging

from odoo_commands.module_set import OdooModuleSet
from odoo_commands.project import OdooProject

logger = logging.getLogger(__name__)


class IndentLogger(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        indent_level = self.extra['indent_level']
        return '    ' * indent_level + msg, kwargs

SECONDS_IN_HOUR = 60 * 60
SECONDS_IN_DAY = 24 * 60 * 60
EPOCH_FIRST_MONDAY = SECONDS_IN_DAY * 4

# import odoo
def shift(t, delta):
    # return (t + EPOCH_FIRST_MONDAY) - t % delta - EPOCH_FIRST_MONDAY
    # return t - (t + EPOCH_FIRST_MONDAY) % delta - EPOCH_FIRST_MONDAY
    return t - (t + EPOCH_FIRST_MONDAY) % delta
    # return (t - EPOCH_FIRST_MONDAY) - t % delta + EPOCH_FIRST_MONDAY


def cache_time_point_generator_3(seq):
    # SECONDS_IN_HOUR = 60 * 60
    # SECONDS_IN_DAY = 24 * 60 * 60
    # EPOCH_FIRST_MONDAY = SECONDS_IN_DAY * 4

    now = int(time.time())
    now = int(time.time() - 60 * SECONDS_IN_DAY)
    # now = 0
    # t = now + EPOCH_FIRST_MONDAY

    seq = [
        SECONDS_IN_HOUR,
        12 * SECONDS_IN_HOUR,
        SECONDS_IN_DAY,
        7 * SECONDS_IN_DAY,
        4 * 7 * SECONDS_IN_DAY,
        24 * 7 * SECONDS_IN_DAY,
    ]

    prev = None
    for s in seq:
        current = shift(now, s)
        if current != prev:
            yield datetime.datetime.fromtimestamp(current)
            prev = current

    # last_hour = shift(now, SECONDS_IN_HOUR)
    # last_12_hours = shift(now, 12 * SECONDS_IN_HOUR)
    # # last_hour = t - t % SECONDS_IN_HOUR
    # # last_12_hours = t - t % (12 * SECONDS_IN_HOUR)
    # last_day = shift(now, SECONDS_IN_DAY)
    # last_sunday = shift(now, 7 * SECONDS_IN_DAY)
    # last_4th_sunday = shift(now, 4 * 7 * SECONDS_IN_DAY)
    # last_24th_sunday = shift(now, 24 * 7 * SECONDS_IN_DAY)
    #
    # return [
    #     datetime.datetime.fromtimestamp(last_hour),
    #     datetime.datetime.fromtimestamp(last_12_hours),
    #     datetime.datetime.fromtimestamp(last_day),
    #     datetime.datetime.fromtimestamp(last_sunday),
    #     datetime.datetime.fromtimestamp(last_4th_sunday),
    #     datetime.datetime.fromtimestamp(last_24th_sunday),
    # ]

def cache_time_point_generator_2():
    now = datetime.datetime.utcnow()
    today = now.date()
    # weekday is in [0,6]; 0 is Monday
    last_monday = today - datetime.timedelta(days=today.weekday())

    first_monday = datetime.date(1970, 1, 5)
    days_from_first_monday = (last_monday - first_monday).days

    last_4th_sunday = last_monday - datetime.timedelta(days=days_from_first_monday % (7 * 4))
    last_24th_sunday = last_monday - datetime.timedelta(days=days_from_first_monday % (7 * 24))

    year, month, day, hour, *_ = now.timetuple()
    return [
        datetime.datetime(year, month, day, hour, 0, 0, 0),
        datetime.datetime(year, month, day, 0, 0, 0, 0),
        last_monday,
        last_4th_sunday,
        last_24th_sunday,
    ]


def cache_time_point_generator(dt=None):
    if dt:
        now = dt
    else:
        # now = datetime.datetime.now()
        now = datetime.datetime.utcnow()

    today = now.date()
    # weekday is in [0,6]; 0 is Monday
    last_monday = today - datetime.timedelta(days=today.weekday())

    first_monday = datetime.date(1970, 1, 5)
    days_from_first_monday = (last_monday - first_monday).days

    last_4th_sunday = last_monday - datetime.timedelta(days=days_from_first_monday % (7 * 4))
    last_24th_sunday = last_monday - datetime.timedelta(days=days_from_first_monday % (7 * 24))

    year, month, day, hour, *_ = now.timetuple()
    return [
        datetime.datetime(year, month, day, hour, 0, 0, 0),
        datetime.datetime(year, month, day, 0, 0, 0, 0),
        last_monday,
        last_4th_sunday,
        last_24th_sunday,
    ]

    return [
        time.mktime((year, month, day, hour, 0, 0, 0, 0, 0)),
        time.mktime((year, month, day, 0, 0, 0, 0, 0, 0)),
        time.mktime(last_monday.timetuple()),
        time.mktime(last_4th_sunday.timetuple()),
        time.mktime(last_24th_sunday.timetuple()),
    ]

# pprint(list(cache_time_point_generator_3([])))


# def read_manifest(module_dir):
#     manifest_path = os.path.join(module_dir, '__manifest__.py')
#     # if not os.path.isfile(manifest_path):
#     #     raise FileNotFoundError("No Odoo manifest found in %s" % addon_dir)
#     with open(manifest_path) as manifest_file:
#         return ast.literal_eval(manifest_file.read())


contrib_module_path = '/home/voronin/.local/share/virtualenvs/sintez_addons-7QRHjYmJ/lib/python3.6/site-packages/odoo/addons'

def module_dependencies(module_dir):
    return read_manifest(module_dir).get('depends', [])


def contrib_module_deps(contrib_module_path):
    res = {}
    for module_dir in glob.iglob(contrib_module_path + '/*'):
        if module_dir.endswith('__pycache__') or module_dir.endswith('__init__.py'):
            continue
        res[module_dir] = module_dependencies(module_dir)
    return res


def get_cache_timestamp_modules(modules, cache_timestamp):
    pass


def install(modules, cache_timestamps, level=0):
    # indent_logger = IndentLogger(logger, {'indent_level': level})
    cache_timestamp = next(cache_timestamps)
    cache_timestamp_modules = get_cache_timestamp_modules(modules, cache_timestamp)
    h = hash(cache_timestamp_modules)
    database = get_database(h)
    if not database:
        database = install(cache_timestamp_modules, cache_timestamps)
    return install_modules(database, modules - cache_timestamp_modules)


def install_modules(database, modules_to_install: OdooModuleSet):
    new_database = name()
    # cache
    copy_database(database, new_database)
    install_modules_2(new_database, modules_to_install)
    return new_database


def create_database(database: str, *, config_path=None, modules: Sequence[str]):
    modules = ','.join(modules)

    args = [
        'odoo',
        '--no-http',
        '--stop-after-init',
        '--without-demo=all',
        f'--database={database}',
        f'--init={modules}',
    ]
    if config_path:
        args.append(f'--config={config_path}')

    subprocess.check_call(args)

def populate_database(database: str, populate_script):
    import runpy
    from odoo_commands import DataGenerator

    global_vars = runpy.run_path(
        populate_script,
        init_globals={'DataGenerator': DataGenerator}
    )
    DatabaseGenerator = global_vars['DatabaseGenerator']
    DatabaseGenerator().generate(database)


# cache_time_points = cache_time_point_generator()
# return install(project.expand_dependencies(project.required_modules), cache_time_points)
