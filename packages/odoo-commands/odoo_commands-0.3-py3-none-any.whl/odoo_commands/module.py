import ast
from functools import cached_property, lru_cache
from pathlib import Path
import typing
from collections import ChainMap

from babel.core import Locale


def adapt_version(version, serie):
    """
    Copy-paste from odoo/modules/module.py:adapt_version()
    Adapt module version using Odoo major version.

    >>> adapt_version('1.0', '15.0')
    '15.0.1.0'
    >>> adapt_version('15.0', '15.0')
    '15.0.15.0'
    >>> adapt_version('15.0.1.0.0', '15.0')
    '15.0.1.0.0'
    """
    if version == serie or not version.startswith(serie + '.'):
        version = '%s.%s' % (serie, version)
    return version


def is_module(path: Path):
    return (path / '__manifest__.py').is_file()


class OdooModule:
    # TODO Add slots
    # __slots__ = ('path', 'name')

    README_FILE_NAMES = ['README.rst', 'README.md', 'README.txt']
    ICON_PATH = 'static/description/icon.png'

    # Default info from odoo/modules/module.py:load_information_from_description_file()
    default_info = {
        'application': False,
        'author': 'Odoo S.A.',
        'auto_install': False,
        'category': 'Uncategorized',
        'depends': [],
        'description': '',
        # 'icon': get_module_icon(module),
        'installable': True,
        'post_load': '',
        'version': '1.0',
        'web': False,
        'sequence': 100,
        'summary': '',
        'website': '',

        'data': [],
        'demo': [],
        'license': 'LGPL-3',
        # Ignored fields: test, init_xml, update_xml, demo_xml,
    }

    OTHER_FIELD_NAMES = frozenset([
        'name',
        'summary',
        'maintainer',
        'contributors',
        'external_dependencies',
        'to_buy',   # ?
        'assets',
        'pre_init_hook',
        'post_init_hook',
        'uninstall_hook',
        'images',
        'images_preview_theme',
        'snippet_lists',
        'live_test_url',
    ])

    _cache = {}

    def __new__(cls, path, *args, **kwargs):
        path = Path(path).resolve()
        if not is_module(path):
            raise ValueError()

        if path in cls._cache:
            return cls._cache[path]

        instance = super().__new__(cls, *args, **kwargs)
        instance.path = path
        instance.name = path.name
        cls._cache[path] = instance
        return instance

    def __repr__(self):
        return f'OdooModule({self.name!r})'

    def __eq__(self, other):
        return self.path == other.path

    def __hash__(self):
        return self.path.__hash__()

    def __truediv__(self, path):
        return self.path / path

    @cached_property
    def manifest(self):
        with open(self.path / '__manifest__.py') as manifest_file:
            return ast.literal_eval(manifest_file.read())

    def __getattr__(self, item):
        if item == 'name':
            raise ValueError('To get non-technical name of module use `shortdesc` attribute')
        elif item == 'shortdesc':
            item = 'name'

        if item in self.manifest:
            return self.manifest[item]
        elif item in self.default_info:
            return self.default_info[item]
        elif item in self.OTHER_FIELD_NAMES:
            return None

        raise AttributeError(f'Unknown attribute: {item!r}')

    @cached_property
    def description(self):
        module_description = self.__getattr__('description')
        if module_description:
            return module_description

        for readme_file_name in self.README_FILE_NAMES:
            readme_file_path = self / readme_file_name
            if readme_file_path.is_file():
                with open(readme_file_path) as description_file:
                    return description_file.read()

        return module_description

    @cached_property
    def icon(self):
        if 'icon' in self.manifest:
            return self.manifest['icon']
        # Copy-paste from odoo/modules/module.py:get_module_icon()
        if (self / self.ICON_PATH).is_file():
            return f'/{self.name}/{self.ICON_PATH}'
        return '/base/' + self.ICON_PATH

    @lru_cache
    def version(self, serie):
        return adapt_version(self.__getattr__('version'), serie)

    # TODO Read description from file

    def data_file_path(self):
        yield from self.manifest.get('data', [])

    # @property
    # def depends(self):
    #     return self.manifest.get('depends', [])

    @cached_property
    def auto_install(self):
        """Manifest `auto_install` can be True, False or list of depends. Convert it to bool"""
        auto_install = self.__getattr__('auto_install')
        if isinstance(auto_install, typing.Iterable):
            return True
        return auto_install

    @cached_property
    def auto_install_depends(self):
        auto_install = self.__getattr__('auto_install')
        if auto_install is False:
            return None
        if auto_install is True:
            return frozenset(self.depends)
        return frozenset(auto_install)

    def _file_translations(self, po_file_name):
        from odoo.tools.translate import PoFileReader

        result = {}
        for subdir in ['i18n_extra', 'i18n']:
            po_file_path = self / subdir / po_file_name
            if not po_file_path.exists():
                continue
            with open(po_file_path, 'rb') as f:
                for translation in PoFileReader(f):
                    trns = (
                        translation['type'],
                        translation['name'],
                        translation['res_id'],
                        translation['src'],
                    )
                    result[trns] = translation['value']

        return result

    @lru_cache()
    def translations(self, locale_identifier):
        locale = Locale.parse(locale_identifier)

        base_trans = self._file_translations(f'{locale.language}.po')
        if not locale.territory or locale.territory.lower() == locale.language:
            return base_trans

        # if locale.territory and locale.territory.lower() != locale.language:
        spec_trans = self._file_translations(f'{locale_identifier}.po')
        return ChainMap(spec_trans, base_trans)
