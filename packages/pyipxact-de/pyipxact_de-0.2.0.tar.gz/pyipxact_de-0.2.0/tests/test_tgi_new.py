"""Tests for newly added TGI service groups (Administrative, Create, Traversal, Catalog refactor).

These tests validate:
* Handle stability and uniqueness.
* VLNV registration and lookup (registerVLNV/getID/getVLNV/unregisterVLNV).
* Catalog creation via createCatalog and automatic registration.
* Traversal enumeration of Catalog IDs.
* Integration of catalog add/remove/get/set functions using new handle manager.
"""
from collections.abc import Sequence

import pytest
from org.accellera.ipxact.v1685_2022 import Catalog
from amal.eda.ipxact_de.tgi.ipxact.v1685_2022 import (
    TgiError,
    addCatalogComponentsIpxactFile,
    getCatalogComponentsIpxactFileIDs,
    getCatalogIDs,
    getID,
    getIpxactFileName,
    getParameterIDs,
    getParameterValue,
    getParameterValueExpression,
    getVLNV,
    get_handle,
    registerVLNV,
    setIpxactFileName,
    setParameterValue,
    unregisterVLNV,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mk_vlnv(suffix: str) -> Sequence[str]:
    return ("vendor", "lib", f"obj{suffix}", "1.0")

# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def _create_root_catalog(vlnv: Sequence[str], *, register: bool):
    """Local helper replicating former root createCatalog semantics."""
    cat = Catalog(vendor=vlnv[0], library=vlnv[1], name=vlnv[2], version=vlnv[3])
    handle = get_handle(cat)
    if register:
        registerVLNV(cat, vlnv)
    return handle, cat


def test_create_and_register_catalog():
    handle, cat = _create_root_catalog(_mk_vlnv("A"), register=True)
    assert isinstance(cat, Catalog)
    assert getID(_mk_vlnv("A")) == handle
    assert getVLNV(handle) == tuple(_mk_vlnv("A"))


def test_register_duplicate_fails():
    handle, cat = _create_root_catalog(_mk_vlnv("B"), register=True)
    # second register of same VLNV should raise
    with pytest.raises(TgiError):
        registerVLNV(cat, _mk_vlnv("B"))
    # still resolves
    assert getID(_mk_vlnv("B")) == handle


def test_unregister_catalog():
    handle, _ = _create_root_catalog(_mk_vlnv("C"), register=True)
    assert unregisterVLNV(_mk_vlnv("C")) is True
    # second attempt returns False
    assert unregisterVLNV(_mk_vlnv("C")) is False
    assert getID(_mk_vlnv("C")) is None
    assert getVLNV(handle) is None


def test_traversal_catalog_ids_increase():
    baseline = set(getCatalogIDs())
    c1_handle, _ = _create_root_catalog(_mk_vlnv("D"), register=True)
    c2_handle, _ = _create_root_catalog(_mk_vlnv("E"), register=True)
    new_ids = set(getCatalogIDs())
    assert c1_handle in new_ids and c2_handle in new_ids
    assert len(new_ids) >= len(baseline) + 2


def test_handle_stability_and_uniqueness():
    _, c1 = _create_root_catalog(_mk_vlnv("F"), register=False)
    _, c2 = _create_root_catalog(_mk_vlnv("G"), register=False)
    h1_a = get_handle(c1)
    h1_b = get_handle(c1)
    h2 = get_handle(c2)
    assert h1_a == h1_b  # stable for same object
    assert h1_a != h2  # unique across objects


def test_catalog_component_add_remove_and_set():
    _, cat = _create_root_catalog(_mk_vlnv("H"), register=False)
    comp_vlnv = ("vendor", "lib", "compX", "1.0")
    file_id = addCatalogComponentsIpxactFile(cat, comp_vlnv, "compX.xml")
    ids = getCatalogComponentsIpxactFileIDs(cat)
    assert file_id in ids
    # rename
    assert cat.components is not None
    target = next(f for f in cat.components.ipxact_file if get_handle(f) == file_id)
    assert setIpxactFileName(target, "compX_new.xml")
    f_name = getIpxactFileName(target)
    assert f_name == "compX_new.xml"


def test_parameter_enumeration_and_get_set():
    # Create a minimal parameter container by attaching parameters to catalog
    # (development convenience; future: use a real container element).
    from org.accellera.ipxact.v1685_2022 import Parameter, Parameters, Value

    # Build an isolated Parameters container and reference directly.
    params = Parameters()
    p1 = Parameter(name="PWIDTH", value=Value(value="16"))
    p2 = Parameter(name="PDEPTH", value=Value(value="256"))
    params.parameter.extend([p1, p2])  # type: ignore[arg-type]
    params_h = get_handle(params)
    param_ids = getParameterIDs(params_h)
    assert len(param_ids) == 2
    # map back to ensure values accessible
    values = [getParameterValue(pid) for pid in param_ids]
    assert set(values) == {"16", "256"}
    # expression currently same
    exprs = [getParameterValueExpression(pid) for pid in param_ids]
    assert values == exprs
    # modify first
    assert setParameterValue(param_ids[0], "32") is True
    assert getParameterValue(param_ids[0]) == "32"

