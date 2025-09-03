import csv
import fnmatch
import os
import pathlib
from collections import defaultdict
from pprint import pprint

import odoo.api
# from odoo.tools import PoFile
from babel.messages import extract
from lxml import etree
from odoo.tools import xml_translate, html_translate

# from odoo_commands.config import read_config, odoo_project_config
# from .createdb import OdooProject
from odoo_commands.project import OdooProject, OdooModule
# from odoo_commands.odoo_translate import PoFile


# d = {
#     'menu': ('ir.ui.menu', ('name',)),
#     'act_window': ('ir.actions.act_window', ('name', 'help')),
#     'report': ('ir.actions.report', ('name', 'help')),
# }

class DataFileExtractor:
    tag_to_model = {
        'menuitem': 'ir.ui.menu',
        'act_window': 'ir.actions.act_window',
        'report': 'ir.actions.report',
    }

    translate_fields = {
        'ir.ui.view': {
            'name': False,
            'model': False,
            'key': False,
            'arch': xml_translate,
            'field_parent': False,
            'xml_id': False,
        },
        'ir.ui.menu': {
            'name': True,
            'web_icon': False,
        },
        'ir.actions.act_window': {
            'name': True,
            'type': False,
            'domain': False,
            'context': False,
            'res_model': False,
            'src_model': False,
            'view_mode': False,
            'usage': False,
            'search_view': False,
            'xml_id': False,
            'help': html_translate,
        },
        'ir.actions.report': {
            'name': True,
            'type': False,
            'model': False,
            'report_name': False,
            'report_file': False,
            'print_report_name': False,
            'attachment': False,
            'module': False,
            'lo_bin_path': False,
            'xml_id': False,
            'help': html_translate,
            # Added
            'py3o_template_fallback': False,
            'msg_py3o_report_not_available': False,
        },
        'ir.module.category': {
            'name': True,
            'description': True,
            'xml_id': False,
        },
        'res.groups': {
            'name': True,
            'comment': True,
        },
        'ir.model.access': {
            'name': False,
        },
        'ir.rule': {
            'name': False,
            'domain_force': False,
        },
    }

    # def __init__(self, field_translates: dict):
    #     self.field_translates = field_translates


    def extract_terms(self, module):
        with odoo.api.Environment.manage():
            registry = odoo.registry(f'module:{module.name}')

        self.res = self.extract_from_source_code(module)

    def extract_from_source_code(self, module: OdooModule):
        """
        Odoo 15: odoo.tools.translate.TranslationModuleReader._babel_extract_terms()
        """
        # result = []
        result = defaultdict(lambda: {
            'modules': set(),
            'tnrs': [],
            'comments': set(),
        })

        for method, path_template, keywords, options, extra_comments in [
            ('python', '**/*.py', {'_': None, '_lt': None}, {'encoding': 'UTF-8'}, []),
            # TODO Skip static/js/lib dir
            ('javascript', 'static/src/js/**/*.js', {'_t': None, '_lt': None}, None, ['openerp-web']),
            ('odoo.tools.translate:babel_extract_qweb', 'static/src/xml/**/*.xml', {'_': None}, None, ['openerp-web']),
            # ('odoo_commands.odoo_translate:babel_extract_qweb', 'static/src/xml/**/*.xml', {'_': None}, None, ['openerp-web']),
        ]:
            for file_path in module.path.glob(path_template):
                display_path = 'addons/' + str(file_path)
                with open(file_path, 'rb') as src_file:
                    for lineno, message, comments, _ in extract.extract(
                        method,
                        src_file,
                        keywords=keywords,
                        options=options,
                    ):
                        # result.append((module_name, trans_type, display_path, lineno, message, '', tuple(comments + extra_comments)))
                        message_data = result[message]
                        message_data['modules'].add(module.name)
                        message_data['tnrs'].append(('code', display_path, lineno))
                        message_data['comments'].update(comments + extra_comments)

        return result

    def extract_from_data_files(self, module):
        for data_file_path in module.data_file_paths():
            data_file_extension = data_file_path.suffix
            if data_file_extension == '.xml':
                self.extract_from_xml_data_file(data_file_path)
            elif data_file_extension == '.csv':
                self.extract_from_csv_data_file(data_file_path)

    def extract_from_xml_data_file(self, data_file_path):
        doc = etree.parse(data_file_path)
        root = doc.getroot()
        # return root

        def field_value(field_tag):
            if field_tag.get('type') == 'xml':
                return ''.join(etree.tostring(child, encoding='unicode') for child in field_tag)
            elif field_tag.text:
                return field_tag.text

        for record in root.iterfind('.//record'):
            model = record.get('model')
            for field in record.iterfind('./field'):
                field_name = field.get('name')
                value = field_value(field)
                if not value:
                    continue
                translate = self.translate(model, field_name)
                # TODO callable translate
                yield model, field.get('name'), value

            # if model in self.translate_fields:
            #     for field_name in self.translate_fields[model]:
            #         field_tag = record.find(f'./field[@name="{field_name}"]')
            #         if field_tag:
            #             value = field_value(field_tag)
            #             if value:
            #                 yield model, field_tag.get('name'), value
            # else:
            #     for field_tag in record.iterfind(f'./field'):
            #         value = field_value(field_tag)
            #         if value and translate:
            #             yield model, field_tag.get('name'), value

        for menuitem in root.iterfind('.//menuitem'):
            yield 'ir.ui.menu', 'name', menuitem.get('name')

        # TODO template tag
        # https://www.odoo.com/documentation/16.0/developer/reference/backend/data.html#template

    def extract_from_csv_data_file(self, file_path):
        model = file_path.stem
        with open(file_path) as csv_file:
            csv_reader = csv.reader(csv_file, quotechar='"', delimiter=',')
            headers = next(csv_reader)
            assert 'id' in headers

            translate_fields = set()
            for field_name in headers:
                if field_name.endswith(':id'):
                    continue
                translate = self.translate(model, field_name)
                if translate:
                    translate_fields.add(field_name)


def write_pot(modules, rows, pot_path, lang):
    buffer = open(pot_path, 'wb')
    writer = PoFile(buffer)
    writer.write_infos(modules)

    # we now group the translations by source. That means one translation per source.
    # grouped_rows = {}
    # for module, type, name, res_id, src, trad, comments in rows:
    #     row = grouped_rows.setdefault(src, {})
    #
    #     row.setdefault('modules', set()).add(module)
    #     if not row.get('translation') and trad != src:
    #         row['translation'] = trad
    #     row.setdefault('tnrs', []).append((type, name, res_id))
    #     row.setdefault('comments', set()).update(comments)

    for src, row in sorted(rows.items()):
        # if not lang:
            # translation template, so no translation value
            # row['translation'] = ''
        # elif not row.get('translation'):
        #     row['translation'] = src
        writer.write(row['modules'], row['tnrs'], src, '', row['comments'])


def parse_xml_file():
    doc = etree.parse(xmlfile)
    obj = xml_import(cr, module, idref, mode, report=report, noupdate=noupdate, xml_filename=xml_filename)
    obj.parse(doc.getroot(), mode=mode)


def generate_pot(module_paths, module_name):
    project = OdooProject(module_paths)
    module = project.module(module_name)

    res = extract_from_source_code(module)
    res.update(extract_from_data_files(module))

    for r in res:
        print(r, res[r])
    write_pot([module_name], res, 'test.pot', False)


# generate_pot(['tests/addons/'], 'module_name')
