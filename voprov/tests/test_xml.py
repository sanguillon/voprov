from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import difflib
import glob
import inspect
import io
from lxml import etree
import os
import unittest
import warnings

from voprov.identifier import Namespace, QualifiedName
from voprov.constants import PROV
import voprov.model as voprov
from voprov.tests.test_model import AllTestsBase
from voprov.tests.utility import RoundTripTestCase


EX_NS = ('ex', 'http://example.com/ns/ex#')
EX_TR = ('tr', 'http://example.com/ns/tr#')

# Most general way to get the path.
DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(inspect.getfile(
    inspect.currentframe()))), "xml")


def remove_empty_tags(tree):
    if tree.text is not None and tree.text.strip() == "":
        tree.text = None
    for elem in tree:
        if etree.iselement(elem):
            remove_empty_tags(elem)


def compare_xml(doc1, doc2):
    """
    Helper function to compare two XML files. It will parse both once again
    and write them in a canonical fashion.
    """
    try:
        doc1.seek(0, 0)
    except AttributeError:
        pass
    try:
        doc2.seek(0, 0)
    except AttributeError:
        pass

    obj1 = etree.parse(doc1)
    obj2 = etree.parse(doc2)

    # Remove comments from both.
    for c in obj1.getroot().xpath("//comment()"):
        p = c.getparent()
        p.remove(c)
    for c in obj2.getroot().xpath("//comment()"):
        p = c.getparent()
        p.remove(c)

    remove_empty_tags(obj1.getroot())
    remove_empty_tags(obj2.getroot())

    buf = io.BytesIO()
    obj1.write_c14n(buf)
    buf.seek(0, 0)
    str1 = buf.read().decode()
    str1 = [_i.strip() for _i in str1.splitlines() if _i.strip()]

    buf = io.BytesIO()
    obj2.write_c14n(buf)
    buf.seek(0, 0)
    str2 = buf.read().decode()
    str2 = [_i.strip() for _i in str2.splitlines() if _i.strip()]

    unified_diff = difflib.unified_diff(str1, str2)

    err_msg = "\n".join(unified_diff)
    if err_msg:
        msg = "Strings are not equal.\n"
        raise AssertionError(msg + err_msg)


class ProvXMLTestCase(unittest.TestCase):
    def test_serialization_example_6(self):
        """
        Test the serialization of example 6 which is a simple entity
        description.
        """
        document = voprov.ProvDocument()
        ex_ns = document.add_namespace(*EX_NS)
        document.add_namespace(*EX_TR)

        document.entity("tr:WD-prov-dm-20111215", (
            (voprov.PROV_TYPE, ex_ns["Document"]),
            ("ex:version", "2")
        ))

        with io.BytesIO() as actual:
            document.serialize(format='xml', destination=actual)
            compare_xml(os.path.join(DATA_PATH, "example_06.xml"), actual)

    def test_serialization_example_7(self):
        """
        Test the serialization of example 7 which is a basic activity.
        """
        document = voprov.ProvDocument()
        document.add_namespace(*EX_NS)

        document.activity(
            "ex:a1",
            "2011-11-16T16:05:00",
            "2011-11-16T16:06:00", [
                (voprov.PROV_TYPE, voprov.Literal("ex:edit", voprov.XSD_QNAME)),
                ("ex:host", "server.example.org")])

        with io.BytesIO() as actual:
            document.serialize(format='xml', destination=actual)
            compare_xml(os.path.join(DATA_PATH, "example_07.xml"), actual)

    def test_serialization_example_8(self):
        """
        Test the serialization of example 8 which deals with generation.
        """
        document = voprov.ProvDocument()
        document.add_namespace(*EX_NS)

        e1 = document.entity("ex:e1")
        a1 = document.activity("ex:a1")

        document.wasGeneratedBy(entity=e1, activity=a1,
                                time="2001-10-26T21:32:52",
                                other_attributes={"ex:port": "p1"})

        e2 = document.entity("ex:e2")

        document.wasGeneratedBy(entity=e2, activity=a1,
                                time="2001-10-26T10:00:00",
                                other_attributes={"ex:port": "p2"})

        with io.BytesIO() as actual:
            document.serialize(format='xml', destination=actual)
            compare_xml(os.path.join(DATA_PATH, "example_08.xml"), actual)

    def test_deserialization_example_6(self):
        """
        Test the deserialization of example 6 which is a simple entity
        description.
        """
        actual_doc = voprov.ProvDocument.deserialize(
            source=os.path.join(DATA_PATH, "example_06.xml"),
            format="xml")

        expected_document = voprov.ProvDocument()
        ex_ns = expected_document.add_namespace(*EX_NS)
        expected_document.add_namespace(*EX_TR)

        expected_document.entity("tr:WD-prov-dm-20111215", (
            (voprov.PROV_TYPE, ex_ns["Document"]),
            ("ex:version", "2")
        ))

        self.assertEqual(actual_doc, expected_document)

    def test_deserialization_example_7(self):
        """
        Test the deserialization of example 7 which is a simple activity
        description.
        """
        actual_doc = voprov.ProvDocument.deserialize(
            source=os.path.join(DATA_PATH, "example_07.xml"),
            format="xml")

        expected_document = voprov.ProvDocument()
        ex_ns = Namespace(*EX_NS)
        expected_document.add_namespace(ex_ns)

        expected_document.activity(
            "ex:a1",
            "2011-11-16T16:05:00",
            "2011-11-16T16:06:00", [
                (voprov.PROV_TYPE, QualifiedName(ex_ns, "edit")),
                ("ex:host", "server.example.org")])

        self.assertEqual(actual_doc, expected_document)

    def test_deserialization_example_04_and_05(self):
        """
        Example 4 and 5 have a different type specification. They use an
        xsi:type as an attribute on an entity. This can be read but if
        written again it will become an XML child element. This is
        semantically identical but cannot be tested with a round trip.
        """
        # Example 4.
        xml_string = """
        <voprov:document
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xmlns:xsd="http://www.w3.org/2001/XMLSchema"
            xmlns:voprov="http://ivoa.net/ns/voprov#"
            xmlns:ex="http://example.com/ns/ex#"
            xmlns:tr="http://example.com/ns/tr#">

          <voprov:entity voprov:id="tr:WD-prov-dm-20111215" xsi:type="voprov:Plan">
            <voprov:type xsi:type="xsd:QName">ex:Workflow</voprov:type>
          </voprov:entity>

        </voprov:document>
        """
        with io.StringIO() as xml:
            xml.write(xml_string)
            xml.seek(0, 0)
            actual_document = voprov.ProvDocument.deserialize(source=xml,
                                                            format="xml")

        expected_document = voprov.ProvDocument()
        ex_ns = Namespace(*EX_NS)
        expected_document.add_namespace(ex_ns)
        expected_document.add_namespace(*EX_TR)

        # The xsi:type attribute is mapped to a proper PROV attribute.
        expected_document.entity("tr:WD-prov-dm-20111215", (
            (voprov.PROV_TYPE, QualifiedName(ex_ns, "Workflow")),
            (voprov.PROV_TYPE, PROV["Plan"])))

        self.assertEqual(actual_document, expected_document, "example_04")

        # Example 5.
        xml_string = """
        <voprov:document
          xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
          xmlns:xsd="http://www.w3.org/2001/XMLSchema"
          xmlns:voprov="http://ivoa.net/ns/voprov#"
          xmlns:ex="http://example.com/ns/ex#"
          xmlns:tr="http://example.com/ns/tr#">

        <voprov:entity voprov:id="tr:WD-prov-dm-20111215" xsi:type="voprov:Plan">
          <voprov:type xsi:type="xsd:QName">ex:Workflow</voprov:type>
          <voprov:type xsi:type="xsd:QName">voprov:Plan</voprov:type> <!-- inferred -->
          <voprov:type xsi:type="xsd:QName">voprov:Entity</voprov:type> <!-- inferred -->
        </voprov:entity>

        </voprov:document>
        """
        with io.StringIO() as xml:
            xml.write(xml_string)
            xml.seek(0, 0)
            actual_document = voprov.ProvDocument.deserialize(source=xml,
                                                            format="xml")

        expected_document = voprov.ProvDocument()
        expected_document.add_namespace(*EX_NS)
        expected_document.add_namespace(*EX_TR)

        # The xsi:type attribute is mapped to a proper PROV attribute.
        expected_document.entity("tr:WD-prov-dm-20111215", (
            (voprov.PROV_TYPE, QualifiedName(ex_ns, "Workflow")),
            (voprov.PROV_TYPE, PROV["Entity"]),
            (voprov.PROV_TYPE, PROV["Plan"])
        ))

        self.assertEqual(actual_document, expected_document, "example_05")

    def test_other_elements(self):
        """
        PROV XML uses the <voprov:other> element to enable the storage of non
        PROV information in a PROV XML document. It will be ignored by this
        library a warning will be raised informing the user.
        """
        # This is example 42 from the PROV XML documentation.
        xml_string = """
        <voprov:document
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xmlns:xsd="http://www.w3.org/2001/XMLSchema"
            xmlns:voprov="http://ivoa.net/ns/voprov#"
            xmlns:ex="http://example.com/ns/ex#">

          <!-- voprov statements go here -->

          <voprov:other>
            <ex:foo>
              <ex:content>bar</ex:content>
            </ex:foo>
          </voprov:other>

          <!-- more voprov statements can go here -->

        </voprov:document>
        """
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            with io.StringIO() as xml:
                xml.write(xml_string)
                xml.seek(0, 0)
                doc = voprov.ProvDocument.deserialize(source=xml, format="xml")

        self.assertEqual(len(w), 1)
        self.assertTrue(
            "Document contains non-PROV information in <voprov:other>. It will "
            "be ignored in this package." in str(w[0].message))

        # This document contains nothing else.
        self.assertEqual(len(doc._records), 0)

    def test_nested_default_namespace(self):
        """
        Tests that a default namespace that is defined in a lower level tag is
        written to a bundle.
        """
        filename = os.path.join(DATA_PATH, "nested_default_namespace.xml")
        doc = voprov.ProvDocument.deserialize(source=filename, format="xml")

        ns = Namespace("", "http://example.org/0/")

        self.assertEqual(len(doc._records), 1)
        self.assertEqual(doc.get_default_namespace(), ns)
        self.assertEqual(doc._records[0].identifier.namespace, ns)
        self.assertEqual(doc._records[0].identifier.localpart, "e001")

    def test_redefining_namespaces(self):
        """
        Test the behaviour when namespaces are redefined at the element level.
        """
        filename = os.path.join(DATA_PATH,
                                "namespace_redefined_but_does_not_change.xml")
        doc = voprov.ProvDocument.deserialize(source=filename, format="xml")
        # This has one record part of the original namespace.
        self.assertEqual(len(doc._records), 1)
        ns = Namespace("ex", "http://example.com/ns/ex#")
        self.assertEqual(doc._records[0].attributes[0][1].namespace, ns)

        # This also has one record but now in a different namespace.
        filename = os.path.join(DATA_PATH, "namespace_redefined.xml")
        doc = voprov.ProvDocument.deserialize(source=filename, format="xml")
        new_ns = doc._records[0].attributes[0][1].namespace
        self.assertNotEqual(new_ns, ns)
        self.assertEqual(new_ns.uri, "http://example.com/ns/new_ex#")


class ProvXMLRoundTripFromFileTestCase(unittest.TestCase):
    def _perform_round_trip(self, filename, force_types=False):
        document = voprov.ProvDocument.deserialize(
            source=filename, format="xml")

        with io.BytesIO() as new_xml:
            document.serialize(format='xml', destination=new_xml,
                               force_types=force_types)
            compare_xml(filename, new_xml)


# Add one test for each found file. Lazy way to do metaprogramming...
# I think parametrized tests are justified in this case as the test
# function names make it clear what is going on.
for filename in glob.iglob(os.path.join(
        DATA_PATH, "*" + os.path.extsep + "xml")):
    name = os.path.splitext(os.path.basename(filename))[0]
    test_name = "test_roundtrip_from_xml_%s" % name

    # Cannot round trip this one as the namespace in the PROV data model are
    # always defined per bundle and not per element.
    if name in ("nested_default_namespace",
                "nested_changing_default_namespace",
                "namespace_redefined_but_does_not_change",
                "namespace_redefined"):
        continue

    # Python creates closures on function calls...
    def get_fct(f):
        # Some test files have a lot of type declarations...
        if name in ["pc1"]:
            force_types = True
        else:
            force_types = False

        def fct(self):
            self._perform_round_trip(f, force_types=force_types)
        return fct

    fct = get_fct(filename)
    fct.__name__ = str(test_name)

    # Disabled round-trip XML comparisons since deserializing then serializing
    # PROV-XML does not maintain XML equivalence. (For example, voprov:entity
    # elements with type voprov:Plan become voprov:plan elements)
    # TODO: Revisit these tests

    # setattr(ProvXMLRoundTripFromFileTestCase, test_name, fct)


class RoundTripXMLTests(RoundTripTestCase, AllTestsBase):
    FORMAT = 'xml'


if __name__ == '__main__':
    unittest.main()
