import pytest
from prov.model import ProvException

from voprov.constants import VOPROV, VOPROV_DATASET_ENTITY, VOPROV_ACTIVITY_DESCRIPTION
from voprov.model import VOProvDocument


def types_in(container):
    return [r.get_type() for r in container.records]


def ids_in(container, record_type):
    return {str(r.identifier) for r in container.records if r.get_type() == record_type}


@pytest.mark.parametrize("missing", ["product_id", "step_id", "used_ids", "generated_ids"])
def test_mandatory_keys(onestep_doc, onestep, missing):
    del onestep[missing]
    with pytest.raises(ProvException, match=missing):
        onestep_doc.add_one_step(onestep)


@pytest.mark.parametrize("with_default_namespace", [True, False])
def test_builds_records(onestep_doc, onestep, with_default_namespace):
    """Works with and without a default namespace (dedicated bundles are named differently)."""
    if with_default_namespace:
        onestep_doc.set_default_namespace(VOPROV.uri)
    product = onestep_doc.add_one_step(onestep)

    assert str(product.identifier) == "obs:image1b"
    assert product.get_type() == VOPROV_DATASET_ENTITY
    assert ids_in(onestep_doc, VOPROV_DATASET_ENTITY) == {"obs:image1b"}
    # step activity, plus the used/generated relations
    assert "ps:2459" in {str(r.identifier) for r in onestep_doc.records}
    # descriptions and configuration live in dedicated bundles
    assert len(onestep_doc.bundles) == 2
    bundle_ids = {str(b.identifier) for b in onestep_doc.bundles}
    assert any("#description#ps#bias_subtraction" in i for i in bundle_ids)
    assert any("#configuration#ps#2459" in i for i in bundle_ids)
    description_bundle = next(b for b in onestep_doc.bundles if "#description#" in str(b.identifier))
    assert VOPROV_ACTIVITY_DESCRIPTION in types_in(description_bundle)


def test_bundle_names_without_default_namespace(onestep_doc, onestep):
    onestep_doc.add_one_step(onestep)
    assert {str(b.identifier) for b in onestep_doc.bundles} == {
        "voprov:#description#ps#bias_subtraction",
        "voprov:#configuration#ps#2459",
    }


def test_bundle_names_with_default_namespace(onestep_doc, onestep):
    onestep_doc.set_default_namespace(VOPROV.uri)
    onestep_doc.add_one_step(onestep)
    assert {b.identifier.localpart for b in onestep_doc.bundles} == {
        "#description#ps#bias_subtraction",
        "#configuration#ps#2459",
    }


def test_integer_process_id(onestep_doc, onestep):
    """process_id is often a number (a PID); it must be turned into a valid identifier.

    A bare number has no prefix, so a default namespace is needed to resolve it.
    """
    onestep_doc.set_default_namespace(VOPROV.uri)
    onestep["process_id"] = 7531
    onestep_doc.add_one_step(onestep)
    assert "7531" in {str(r.identifier).split(":")[-1] for r in onestep_doc.records}


def test_instrument(onestep_doc, onestep):
    onestep.update(process_id="ps:proc1", instrument_id="obs:camera", instrument_name="Camera")
    onestep_doc.add_one_step(onestep)
    identifiers = {str(r.identifier) for r in onestep_doc.records}
    assert {"ps:proc1", "obs:camera"} <= identifiers


def test_two_steps_share_entities(onestep_doc, onestep):
    """A second step using the first step's product reuses the same identifiers (no duplicate records)."""
    onestep_doc.add_one_step(onestep)
    second = dict(onestep, product_id="obs:image2", step_id="ps:2460", step_name="ps:flat_field",
                  used_ids=["obs:image1b"], step_parameters={})
    onestep_doc.add_one_step(second)
    onestep_doc.unified()  # must not raise
    products = ids_in(onestep_doc, VOPROV_DATASET_ENTITY)
    assert products == {"obs:image1b", "obs:image2"}


def test_serializable(onestep_doc, onestep):
    onestep_doc.add_one_step(onestep)
    content = onestep_doc.serialize(format="json")
    again = VOProvDocument.deserialize(content=content, format="json")
    assert again == onestep_doc
