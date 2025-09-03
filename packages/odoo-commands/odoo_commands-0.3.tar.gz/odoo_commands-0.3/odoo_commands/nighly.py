import sys
import enum


class FileFormat(enum.Enum):
    deb = 'deb'
    exe = 'exe'
    rpm = 'rpm'
    tgz = 'tgz'
    zip = 'zip'


def download_odoo(odoo_version: str, file_format: FileFormat = 'zip'):
    import re

    if result := re.match(r'^(\d{2}\.0)\.\d{8}$', odoo_version):
        odoo_major_version = result.groups()[0]
    else:
        raise ValueError('Incorrect Odoo version. Correct version format is XX.0.YYYYMMdd')

    if file_format == FileFormat.deb:
        file_name = f'odoo_{odoo_version}_all.deb'
    elif file_format == FileFormat.exe:
        file_name = f'odoo_setup_{odoo_version}.exe'
    elif file_format == FileFormat.tgz:
        file_name = f'odoo_{odoo_version}.tar.gz'
    else:
        file_name = f'odoo_{odoo_version}.{file_format.value}'

    if file_format == FileFormat.zip:
        dir_name = 'src'
    else:
        dir_name = file_format.value

    file_url = f'https://nightly.odoo.com/{odoo_major_version}/nightly/{dir_name}/{file_name}'

    import shutil

    if shutil.which('curl'):
        # --fail option returns non-zero code and prevents output saving
        args = ['curl', '--fail', '--output', file_name, file_url]
    elif shutil.which('wget'):
        args = ['wget', '--output-document', file_name, file_url]
    else:
        raise OSError('There is no cURL and no wget')

    import subprocess
    return_code = subprocess.call(args)
    if return_code:
        sys.exit(return_code)

    # TODO print('docs how to unpack')
