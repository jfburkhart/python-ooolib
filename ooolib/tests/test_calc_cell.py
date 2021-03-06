import os
import unittest
import zipfile
from StringIO import StringIO

import ooolib
from lxml import etree
from ooolib.tests.utils import prepare_mkdtemp


class TestCell(unittest.TestCase):

    namespaces = {
        'style': 'urn:oasis:names:tc:opendocument:xmlns:style:1.0',
        'fo': 'urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0',
        'text': 'urn:oasis:names:tc:opendocument:xmlns:text:1.0',
        'table': 'urn:oasis:names:tc:opendocument:xmlns:table:1.0',
    }

    def setUp(self):
        self.dirname = prepare_mkdtemp(self)

    def test_cell_border(self):
        # create odt document
        thin_value = '0.001in solid #ff0000'
        bold_value = '0.01in solid #00ff00'

        filename = os.path.join(self.dirname, "test.ods")
        doc = ooolib.Calc("test_cell")
        doc.set_cell_property('border', thin_value)
        doc.set_cell_value(2, 2, "string", "Name")
        doc.set_cell_property('border', bold_value)
        doc.set_cell_value(2, 4, "string", "Value")
        doc.save(filename)

        # check created document
        handle = zipfile.ZipFile(filename)
        xdoc = etree.parse(StringIO(handle.read('content.xml')))

        style_definition = xdoc.xpath('//style:table-cell-properties[@fo:border="%s"]/../@style:name' % thin_value,
                                      namespaces=self.namespaces)
        cell_style = xdoc.xpath('//text:p[text()="Name"]/../@table:style-name', namespaces=self.namespaces)
        self.assertEqual(cell_style, style_definition)

        style_definition = xdoc.xpath('//style:table-cell-properties[@fo:border="%s"]/../@style:name' % bold_value,
                                      namespaces=self.namespaces)
        cell_style = xdoc.xpath('//text:p[text()="Value"]/../@table:style-name', namespaces=self.namespaces)
        self.assertEqual(cell_style, style_definition)

    def test_cell_wrap_option(self):
        # create odt document
        filename = os.path.join(self.dirname, "test.ods")
        doc = ooolib.Calc("test_cell")
        doc.set_cell_property('wrap-option', 'wrap')
        doc.set_cell_value(2, 2, "string", "Name")
        doc.save(filename)

        # check created document
        handle = zipfile.ZipFile(filename)
        xdoc = etree.parse(StringIO(handle.read('content.xml')))

        style_definition = xdoc.xpath('//style:table-cell-properties[@fo:wrap-option="wrap"]/../@style:name',
                                      namespaces=self.namespaces)
        cell_style = xdoc.xpath('//text:p[text()="Name"]/../@table:style-name', namespaces=self.namespaces)
        self.assertEqual(cell_style, style_definition)

    def test_cell_hyphenate(self):
        # create odt document
        filename = os.path.join(self.dirname, "test.ods")
        doc = ooolib.Calc("test_cell")
        doc.set_cell_property('hyphenate', True)
        doc.set_cell_value(2, 2, "string", "Name")
        doc.save(filename)

        # check created document
        handle = zipfile.ZipFile(filename)
        xdoc = etree.parse(StringIO(handle.read('content.xml')))

        style_definition = xdoc.xpath('//style:text-properties[@fo:hyphenate="true"]/../@style:name',
                                      namespaces=self.namespaces)
        cell_style = xdoc.xpath('//text:p[text()="Name"]/../@table:style-name', namespaces=self.namespaces)
        self.assertEqual(cell_style, style_definition)

    def test_cell_padding(self):
        # create odt document
        filename = os.path.join(self.dirname, "test.ods")
        doc = ooolib.Calc("test_cell")
        doc.set_cell_property('padding-left', '0.1in')
        doc.set_cell_value(2, 2, "string", "Left")
        doc.set_cell_property('padding-left', False)

        doc.set_cell_property('padding-right', '0.2in')
        doc.set_cell_value(3, 2, "string", "Right")
        doc.set_cell_property('padding-right', False)

        doc.set_cell_property('padding', '0.3in')
        doc.set_cell_value(4, 2, "string", "Full")
        doc.set_cell_property('padding', False)

        doc.set_cell_value(5, 2, "string", "No-padding")

        doc.save(filename)

        # check created document
        handle = zipfile.ZipFile(filename)
        xdoc = etree.parse(StringIO(handle.read('content.xml')))

        style_definition = xdoc.xpath('//style:table-cell-properties[@fo:padding-left="0.1in"]/../@style:name',
                                      namespaces=self.namespaces)
        cell_style = xdoc.xpath('//text:p[text()="Left"]/../@table:style-name', namespaces=self.namespaces)
        self.assertEqual(cell_style, style_definition)

        style_definition = xdoc.xpath('//style:table-cell-properties[@fo:padding-right="0.2in"]/../@style:name',
                                      namespaces=self.namespaces)
        cell_style = xdoc.xpath('//text:p[text()="Right"]/../@table:style-name', namespaces=self.namespaces)
        self.assertEqual(cell_style, style_definition)

        style_definition = xdoc.xpath('//style:table-cell-properties[@fo:padding="0.3in"]/../@style:name',
                                      namespaces=self.namespaces)
        cell_style = xdoc.xpath('//text:p[text()="Full"]/../@table:style-name', namespaces=self.namespaces)
        self.assertEqual(cell_style, style_definition)

        cell_style = xdoc.xpath('//text:p[text()="No-padding"]/../@table:style-name', namespaces=self.namespaces)
        self.assertEqual(cell_style, [])


class TestCalcSheet(unittest.TestCase):

    def test_clean_formula(self):
        sheet = ooolib.CalcSheet('Sheet Name')

        data = sheet.clean_formula('The test.')
        self.assertEqual(data, 'The test.')

        data = sheet.clean_formula('=SUM(A1:A2)')
        self.assertEqual(data, 'oooc:=SUM([.A1]:[.A2])')

        data = sheet.clean_formula('=IF((A5>A4);A3;"The test.")')
        self.assertEqual(data, 'oooc:=IF(([.A5]&gt;[.A4]);[.A3];&quot;The test.&quot;)')
