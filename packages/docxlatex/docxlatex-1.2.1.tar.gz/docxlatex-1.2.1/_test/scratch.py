from xml.dom import minidom
from defusedxml import ElementTree
import zipfile


def get_pretty_xml(filepath):
    zip_f = zipfile.ZipFile(filepath, 'r')
    for f in zip_f.namelist():
        if f.startswith('word/document'):
            return minidom.parse(zip_f.open(f)).toprettyxml()


def get_xml_root(filepath):
    zip_f = zipfile.ZipFile(filepath, 'r')
    for f in zip_f.namelist():
        if f.startswith('word/document'):
            return ElementTree.fromstring(zip_f.read(f))


if __name__ == '__main__':
    print(get_pretty_xml('../tests/docx/tags/r/r.docx'))
    root = get_xml_root('../tests/docx/tags/r/r.docx')
    for tag in root.iter():
        if tag.tag == '{http://schemas.openxmlformats.org/officeDocument/2006/math}oMath':
            print(''.join(tag.itertext()))
            break
