import subprocess
import sys
import textwrap

import prov.constants
import prov.model

from voprov import constants as c
from voprov.model import records as r
from voprov.registry import register, voprov_record_classes


def table_sizes():
    return (len(prov.model.PROV_REC_CLS), len(prov.constants.PROV_N_MAP),
            len(prov.constants.PROV_ATTRIBUTE_QNAMES), len(prov.constants.PROV_ATTRIBUTE_LITERALS),
            len(prov.constants.PROV_BASE_CLS), len(prov.constants.ADDITIONAL_N_MAP))


def run(code):
    """Run code in a fresh interpreter (prov's tables are process-global)."""
    return subprocess.run([sys.executable, "-W", "ignore", "-c", textwrap.dedent(code)],
                          capture_output=True, text=True, check=True).stdout.strip()


def test_importing_constants_does_not_touch_prov():
    out = run("""
        import prov.constants, prov.model
        t = lambda: (len(prov.model.PROV_REC_CLS), len(prov.constants.PROV_N_MAP),
                     len(prov.constants.PROV_ATTRIBUTE_QNAMES), len(prov.model.DEFAULT_NAMESPACES))
        before = t()
        import voprov.constants
        print(before == t())
    """)
    assert out == "True"


def test_importing_model_registers_voprov():
    out = run("""
        import prov.model
        n = len(prov.model.PROV_REC_CLS)
        import voprov.model
        print(len(prov.model.PROV_REC_CLS) > n)
    """)
    assert out == "True"


def test_prov_default_namespaces_untouched():
    assert "voprov" not in prov.model.DEFAULT_NAMESPACES
    assert "voprov" in c.DEFAULT_NAMESPACES


def test_register_is_idempotent():
    before = table_sizes()
    register()
    register()
    assert table_sizes() == before


def test_record_classes_registered():
    classes = voprov_record_classes()
    assert classes[c.VOPROV_ENTITY] is r.VOProvEntity
    assert classes[c.VOPROV_ACTIVITY_DESCRIPTION] is r.VOProvActivityDescription
    for record_type, cls in classes.items():
        assert prov.model.PROV_REC_CLS[record_type] is cls


def test_tables_extended():
    for record_type, name in c.VOPROV_N_MAP.items():
        assert prov.constants.PROV_N_MAP[record_type] == name
    for record_type, base in c.VOPROV_BASE_CLS.items():
        assert prov.constants.PROV_BASE_CLS[record_type] == base
    assert c.VOPROV_ATTRIBUTE_QNAMES <= prov.constants.PROV_ATTRIBUTE_QNAMES


def test_merged_views_match_registered_tables():
    assert c.PROV_N_MAP == prov.constants.PROV_N_MAP
    assert c.PROV_BASE_CLS == prov.constants.PROV_BASE_CLS
    assert c.ADDITIONAL_N_MAP == prov.constants.ADDITIONAL_N_MAP
    assert c.PROV_ATTRIBUTE_QNAMES == prov.constants.PROV_ATTRIBUTE_QNAMES
    assert c.PROV_ATTRIBUTE_LITERALS == prov.constants.PROV_ATTRIBUTE_LITERALS


def test_every_registered_class_has_a_provn_name():
    for record_type in voprov_record_classes():
        assert record_type in c.PROV_N_MAP, record_type


def test_plain_prov_documents_still_build_prov_records():
    d = prov.model.ProvDocument()
    d.add_namespace("ex", "http://example.org/")
    assert type(d.entity("ex:e")) is prov.model.ProvEntity
    assert type(d.activity("ex:a")) is prov.model.ProvActivity
