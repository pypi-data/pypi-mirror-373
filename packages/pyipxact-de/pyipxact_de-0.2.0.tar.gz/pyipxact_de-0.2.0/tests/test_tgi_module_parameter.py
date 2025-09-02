"""Tests for module parameter category TGI functions."""
from org.accellera.ipxact.v1685_2022 import ComponentInstantiationType, ModuleParameterType, Value

from amal.eda.ipxact_de.tgi.ipxact.v1685_2022 import (
    getModuleParameterIDs,
    getModuleParameterValue,
    getModuleParameterValueExpression,
    setModuleParameterValue,
    get_handle,
)


def _make_inst():
    # Build a component instantiation with nested module parameters
    mp1 = ModuleParameterType(name="WIDTH", value=Value(value="8"))
    mp2 = ModuleParameterType(name="DEPTH", value=Value(value="256"))
    inst = ComponentInstantiationType()
    inst.module_parameters = ComponentInstantiationType.ModuleParameters(module_parameter=[mp1, mp2])
    return inst


def test_module_parameter_traversal_get_set():
    inst = _make_inst()
    inst_id = get_handle(inst)
    ids = getModuleParameterIDs(inst_id)
    assert len(ids) == 2
    values = {getModuleParameterValue(i) for i in ids}
    assert values == {"8", "256"}
    exprs = {getModuleParameterValueExpression(i) for i in ids}
    assert exprs == values
    # update first
    assert setModuleParameterValue(ids[0], "16") is True
    assert getModuleParameterValue(ids[0]) == "16"
