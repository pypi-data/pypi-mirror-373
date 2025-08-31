"""Tests for configurable element category TGI functions."""
from org.accellera.ipxact.v1685_2022 import ConfigurableElementValue, ConfigurableElementValues

from amal.eda.ipxact_de.tgi.ipxact.v1685_2022 import (
    getConfigurableElementIDs,
    getConfigurableElementValue,
    getConfigurableElementValueExpression,
    getConfigurableElementValueIDs,
    getConfigurableElementValueReferenceID,
    getConfigurableElementValueValueExpression,
    getUnconfiguredID,
    get_handle,
)


def _make_owner():
    cev1 = ConfigurableElementValue(reference_id="REF1", value="10")
    cev2 = ConfigurableElementValue(reference_id="REF2", value="WIDTH*2")
    container = ConfigurableElementValues(configurable_element_value=[cev1, cev2])
    class Owner:  # simple dynamic owner with attribute
        def __init__(self, cev):
            self.configurable_element_values = cev
    return Owner(container)


def test_configurable_element_value_traversal_and_gets():
    owner = _make_owner()
    owner_id = get_handle(owner)
    val_ids = getConfigurableElementValueIDs(owner_id)
    assert len(val_ids) == 2
    # element-level IDs identical placeholder mapping
    # Use category implementation (new module) which mirrors value IDs for now.
    element_ids = getConfigurableElementIDs(owner_id)
    assert element_ids == val_ids
    # check each
    for vid in val_ids:
        assert getConfigurableElementValueValueExpression(vid) is not None
        assert getConfigurableElementValue(vid) == getConfigurableElementValueExpression(vid)
        ref = getConfigurableElementValueReferenceID(vid)
        assert ref in {"REF1", "REF2"}
    # unconfigured mapping identity
    assert getUnconfiguredID(val_ids[0]) == val_ids[0]
