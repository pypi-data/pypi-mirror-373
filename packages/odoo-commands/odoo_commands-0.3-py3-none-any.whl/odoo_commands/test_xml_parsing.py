from lxml import etree


def convert_xml_import(xml_file_path):
    doc = etree.parse(xml_file_path)
    root = doc.getroot()
    # return root

    for record in root.iterfind('.//record'):
        model = record.get('model')
        for field in record.iterfind('./field'):
            print(field.get('name', 'No'))
            # value = None
            # if field.get('type') == 'xml':
            #     value = '\n'.join(etree.tostring(element) for element in field)
            # elif field.text:
            #     value = field.text
            #
            # if value:
            #     yield model, field.get('name'), value

    # d = {
    #     'menu': ('ir.ui.menu', ('name',)),
    #     'act_window': ('ir.actions.act_window', ('name', 'help')),
    #     'report': ('ir.actions.report', ('name', 'help')),
    # }

    # for tag, model, fields in d:
    #     element = root.iterfind(tag)
    #     for field in fields:
    #         yield model, field, element.get(field)


root = convert_xml_import('tests/addons/module_name/views/sale_order.xml')
