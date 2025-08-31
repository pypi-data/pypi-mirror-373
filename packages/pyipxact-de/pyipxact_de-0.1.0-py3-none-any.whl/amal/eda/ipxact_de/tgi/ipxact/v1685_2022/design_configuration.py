"""Design configuration category TGI functions (IEEE 1685-2022).

Implements BASE (F.7.39) and EXTENDED (F.7.40) functions for
``designConfiguration``. Only the public TGI API ("no more, no less") is
exported. Mutators return ``True`` on success and raise :class:`TgiError` with
``TgiFaultCode.INVALID_ID`` for invalid handles. If an element to remove is not
found the function returns ``False`` without raising.

Helper functions are prefixed with ``_`` and intentionally excluded from the
public API surface.
"""
# ruff: noqa: I001

from org.accellera.ipxact.v1685_2022 import (
    Choices,
    ConfigurableElementValue,
    ConfigurableLibraryRefType,
    DesignConfiguration,
    InstanceName,
    LibraryRefType,
)

from .core import (
    TgiError,
    TgiFaultCode,
    get_handle,
    resolve_handle,
    register_parent,
    detach_child_by_handle,
)

__all__ = [
    # BASE (F.7.39)
    "getAbstractorInstanceAbstractorRefByID",
    "getAbstractorInstanceAbstractorRefByVLNV",
    "getAbstractorInstanceInstanceName",
    "getAbstractorInstanceViewName",
    "getAbstractorInstancesAbstractorInstanceIDs",
    "getAbstractorInstancesInterfaceRefIDs",
    "getDesignConfigurationChoiceIDs",
    "getDesignConfigurationDesignRefByID",
    "getDesignConfigurationDesignRefByVLNV",
    "getDesignConfigurationGeneratorChainConfigurationIDs",
    "getDesignConfigurationInterconnectionConfigurationIDs",
    "getDesignConfigurationViewConfigurationIDs",
    "getGeneratorChainConfigurationRefByID",
    "getGeneratorChainConfigurationRefByVLNV",
    "getInterconnectionConfigurationAbstractorsInstancesIDs",
    "getInterconnectionConfigurationInterconnectionRefByID",
    "getInterconnectionConfigurationInterconnectionRefByName",
    "getViewConfigurationConfigurableElementValueIDs",
    "getViewConfigurationInstanceName",
    "getViewConfigurationViewID",
    # EXTENDED (F.7.40)
    "addAbstractorInstancesAbstractorInstance",
    "addAbstractorInstancesInterfaceRef",
    "addDesignConfChoice",  # spec naming retained
    "addDesignConfigurationGeneratorChainConfiguration",
    "addDesignConfigurationInterconnectionConfiguration",
    "addDesignConfigurationViewConfiguration",
    "addInterconnectionConfigurationAbstractorInstances",
    "removeAbstractorInstancesAbstractorInstance",
    "removeAbstractorInstancesInterfaceRef",
    "removeDesignConfChoice",
    "removeDesignConfigurationDesignRef",
    "removeDesignConfigurationGeneratorChainConfiguration",
    "removeDesignConfigurationInterconnectionConfiguration",
    "removeDesignConfigurationViewConfiguration",
    "removeInterconnectionConfigurationAbstractorInstances",
    "removeViewConfigurationConfigurableElementValue",
    "setAbstractorInstanceAbstractorRef",
    "setAbstractorInstanceInstanceName",
    "setAbstractorInstanceViewName",
    "setDesignConfigurationDesignRef",
]


# ---------------------------------------------------------------------------
# Helpers (non-spec)
# ---------------------------------------------------------------------------

def _resolve(dcID: str) -> DesignConfiguration | None:
    obj = resolve_handle(dcID)
    return obj if isinstance(obj, DesignConfiguration) else None


def _resolve_interconnection_configuration(icID: str) -> DesignConfiguration.InterconnectionConfiguration | None:
    obj = resolve_handle(icID)
    return obj if isinstance(obj, DesignConfiguration.InterconnectionConfiguration) else None


def _resolve_abstractor_instances(
    aiID: str,
) -> DesignConfiguration.InterconnectionConfiguration.AbstractorInstances | None:
    obj = resolve_handle(aiID)
    return (
        obj
        if isinstance(
            obj,
            DesignConfiguration.InterconnectionConfiguration.AbstractorInstances,
        )
        else None
    )


def _resolve_abstractor_instance(
    instID: str,
) -> (
    DesignConfiguration.InterconnectionConfiguration.AbstractorInstances.AbstractorInstance
    | None
):
    obj = resolve_handle(instID)
    return (
        obj
        if isinstance(
            obj,
            DesignConfiguration.InterconnectionConfiguration.AbstractorInstances.AbstractorInstance,
        )
        else None
    )


def _resolve_interface_ref(
    irID: str,
) -> DesignConfiguration.InterconnectionConfiguration.AbstractorInstances.InterfaceRef | None:
    obj = resolve_handle(irID)
    return (
        obj
        if isinstance(
            obj,
            DesignConfiguration.InterconnectionConfiguration.AbstractorInstances.InterfaceRef,
        )
        else None
    )


def _resolve_view_configuration(vcID: str) -> DesignConfiguration.ViewConfiguration | None:
    obj = resolve_handle(vcID)
    return obj if isinstance(obj, DesignConfiguration.ViewConfiguration) else None


def _resolve_configurable_element_value(cevID: str) -> ConfigurableElementValue | None:
    obj = resolve_handle(cevID)
    return obj if isinstance(obj, ConfigurableElementValue) else None


# ---------------------------------------------------------------------------
# BASE (F.7.39)
# ---------------------------------------------------------------------------

def getAbstractorInstanceAbstractorRefByID(abstractorInstanceID: str) -> str | None:
    """Return handle of the ``abstractorRef`` element of an abstractorInstance.

    Section: F.7.39.1. Returns ``None`` if not present (schema requires it though).
    """
    inst = _resolve_abstractor_instance(abstractorInstanceID)
    if inst is None:
        raise TgiError("Invalid abstractorInstance handle", TgiFaultCode.INVALID_ID)
    ref = inst.abstractor_ref
    return None if ref is None else get_handle(ref)


def getAbstractorInstanceAbstractorRefByVLNV(
    abstractorInstanceID: str,
) -> tuple[str | None, str | None, str | None, str | None]:
    """Return (vendor, library, name, version) of the abstractorRef.

    Section: F.7.39.2.
    """
    inst = _resolve_abstractor_instance(abstractorInstanceID)
    if inst is None:
        raise TgiError("Invalid abstractorInstance handle", TgiFaultCode.INVALID_ID)
    ref = inst.abstractor_ref
    if ref is None:
        return (None, None, None, None)
    return (ref.vendor, ref.library, ref.name, ref.version)


def getAbstractorInstanceInstanceName(abstractorInstanceID: str) -> str | None:
    """Return instanceName of an abstractorInstance.

    Section: F.7.39.3.
    """
    inst = _resolve_abstractor_instance(abstractorInstanceID)
    if inst is None:
        raise TgiError("Invalid abstractorInstance handle", TgiFaultCode.INVALID_ID)
    return inst.instance_name


def getAbstractorInstanceViewName(abstractorInstanceID: str) -> str | None:
    """Return viewName of an abstractorInstance.

    Section: F.7.39.4.
    """
    inst = _resolve_abstractor_instance(abstractorInstanceID)
    if inst is None:
        raise TgiError("Invalid abstractorInstance handle", TgiFaultCode.INVALID_ID)
    return inst.view_name


def getAbstractorInstancesAbstractorInstanceIDs(abstractorInstancesID: str) -> list[str]:
    """Return handles of ``abstractorInstance`` children within an abstractorInstances container.

    Section: F.7.39.5.
    """
    ai = _resolve_abstractor_instances(abstractorInstancesID)
    if ai is None:
        raise TgiError("Invalid abstractorInstances handle", TgiFaultCode.INVALID_ID)
    return [get_handle(x) for x in ai.abstractor_instance]


def getAbstractorInstancesInterfaceRefIDs(abstractorInstancesID: str) -> list[str]:
    """Return handles of ``interfaceRef`` elements under an abstractorInstances.

    Section: F.7.39.6.
    """
    ai = _resolve_abstractor_instances(abstractorInstancesID)
    if ai is None:
        raise TgiError("Invalid abstractorInstances handle", TgiFaultCode.INVALID_ID)
    return [get_handle(x) for x in ai.interface_ref]


def getDesignConfigurationChoiceIDs(designConfigurationID: str) -> list[str]:
    """Return handles of ``choice`` elements.

    Section: F.7.39.7.
    """
    dc = _resolve(designConfigurationID)
    if dc is None:
        raise TgiError("Invalid designConfiguration handle", TgiFaultCode.INVALID_ID)
    if dc.choices is None:
        return []
    return [get_handle(c) for c in getattr(dc.choices, "choice", [])]


def getDesignConfigurationDesignRefByID(designConfigurationID: str) -> str | None:
    """Return handle of the ``designRef`` element.

    Section: F.7.39.8.
    """
    dc = _resolve(designConfigurationID)
    if dc is None:
        raise TgiError("Invalid designConfiguration handle", TgiFaultCode.INVALID_ID)
    dr = dc.design_ref
    return None if dr is None else get_handle(dr)


def getDesignConfigurationDesignRefByVLNV(
    designConfigurationID: str,
) -> tuple[str | None, str | None, str | None, str | None]:
    """Return designRef VLNV tuple.

    Section: F.7.39.9.
    """
    dc = _resolve(designConfigurationID)
    if dc is None:
        raise TgiError("Invalid designConfiguration handle", TgiFaultCode.INVALID_ID)
    dr = dc.design_ref
    if dr is None:
        return (None, None, None, None)
    return (dr.vendor, dr.library, dr.name, dr.version)


def getDesignConfigurationGeneratorChainConfigurationIDs(designConfigurationID: str) -> list[str]:
    """Return handles of ``generatorChainConfiguration`` entries.

    Section: F.7.39.10.
    """
    dc = _resolve(designConfigurationID)
    if dc is None:
        raise TgiError("Invalid designConfiguration handle", TgiFaultCode.INVALID_ID)
    return [get_handle(g) for g in dc.generator_chain_configuration]


def getDesignConfigurationInterconnectionConfigurationIDs(designConfigurationID: str) -> list[str]:
    """Return handles of ``interconnectionConfiguration`` entries.

    Section: F.7.39.11.
    """
    dc = _resolve(designConfigurationID)
    if dc is None:
        raise TgiError("Invalid designConfiguration handle", TgiFaultCode.INVALID_ID)
    return [get_handle(ic) for ic in dc.interconnection_configuration]


def getDesignConfigurationViewConfigurationIDs(designConfigurationID: str) -> list[str]:
    """Return handles of ``viewConfiguration`` entries.

    Section: F.7.39.12.
    """
    dc = _resolve(designConfigurationID)
    if dc is None:
        raise TgiError("Invalid designConfiguration handle", TgiFaultCode.INVALID_ID)
    return [get_handle(vc) for vc in dc.view_configuration]


def getGeneratorChainConfigurationRefByID(generatorChainConfigurationID: str) -> str | None:
    """Return handle of a generatorChainConfiguration element (identity pass-through).

    Section: F.7.39.13. Provided for spec completeness – the handle is the object itself.
    """
    obj = resolve_handle(generatorChainConfigurationID)
    if not isinstance(obj, ConfigurableLibraryRefType):
        raise TgiError("Invalid generatorChainConfiguration handle", TgiFaultCode.INVALID_ID)
    return get_handle(obj)


def getGeneratorChainConfigurationRefByVLNV(
    generatorChainConfigurationID: str,
) -> tuple[str | None, str | None, str | None, str | None]:
    """Return VLNV of a generatorChainConfiguration reference.

    Section: F.7.39.14.
    """
    obj = resolve_handle(generatorChainConfigurationID)
    if not isinstance(obj, ConfigurableLibraryRefType):
        raise TgiError("Invalid generatorChainConfiguration handle", TgiFaultCode.INVALID_ID)
    return (obj.vendor, obj.library, obj.name, obj.version)


def getInterconnectionConfigurationAbstractorsInstancesIDs(interconnectionConfigurationID: str) -> list[str]:
    """Return handles of ``abstractorInstances`` groups under an interconnectionConfiguration.

    Section: F.7.39.15.
    """
    ic = _resolve_interconnection_configuration(interconnectionConfigurationID)
    if ic is None:
        raise TgiError("Invalid interconnectionConfiguration handle", TgiFaultCode.INVALID_ID)
    return [get_handle(ai) for ai in ic.abstractor_instances]


def getInterconnectionConfigurationInterconnectionRefByID(interconnectionConfigurationID: str) -> str | None:
    """Return the interconnectionRef as a string (ID form).

    Section: F.7.39.16. The reference is a name string, so we return it directly.
    """
    ic = _resolve_interconnection_configuration(interconnectionConfigurationID)
    if ic is None:
        raise TgiError("Invalid interconnectionConfiguration handle", TgiFaultCode.INVALID_ID)
    return ic.interconnection_ref


def getInterconnectionConfigurationInterconnectionRefByName(interconnectionConfigurationID: str) -> str | None:
    """Alias of F.7.39.16 per spec naming – returns the interconnectionRef name.

    Section: F.7.39.17.
    """
    return getInterconnectionConfigurationInterconnectionRefByID(interconnectionConfigurationID)


def getViewConfigurationConfigurableElementValueIDs(viewConfigurationID: str) -> list[str]:
    """Return handles of configurableElementValue children within a viewConfiguration's view.

    Section: F.7.39.18.
    """
    vc = _resolve_view_configuration(viewConfigurationID)
    if vc is None:
        raise TgiError("Invalid viewConfiguration handle", TgiFaultCode.INVALID_ID)
    v = vc.view
    if v is None or v.configurable_element_values is None:
        return []
    return [get_handle(cev) for cev in getattr(v.configurable_element_values, "configurable_element_value", [])]


def getViewConfigurationInstanceName(viewConfigurationID: str) -> str | None:
    """Return instanceName for a viewConfiguration.

    Section: F.7.39.19.
    """
    vc = _resolve_view_configuration(viewConfigurationID)
    if vc is None:
        raise TgiError("Invalid viewConfiguration handle", TgiFaultCode.INVALID_ID)
    inst = vc.instance_name
    return None if inst is None else inst.value  # type: ignore[attr-defined]


def getViewConfigurationViewID(viewConfigurationID: str) -> str | None:
    """Return handle of the ``view`` element of a viewConfiguration.

    Section: F.7.39.20.
    """
    vc = _resolve_view_configuration(viewConfigurationID)
    if vc is None:
        raise TgiError("Invalid viewConfiguration handle", TgiFaultCode.INVALID_ID)
    view = vc.view
    return None if view is None else get_handle(view)


# ---------------------------------------------------------------------------
# EXTENDED (F.7.40)
# ---------------------------------------------------------------------------

def addAbstractorInstancesAbstractorInstance(
    abstractorInstancesID: str,
    instanceName: str,
    viewName: str,
    abstractorRefVLNV: tuple[str, str, str, str],
) -> str:
    """Create and append an ``abstractorInstance``.

    Section: F.7.40.1.
    """
    ai = _resolve_abstractor_instances(abstractorInstancesID)
    if ai is None:
        raise TgiError("Invalid abstractorInstances handle", TgiFaultCode.INVALID_ID)
    inst = DesignConfiguration.InterconnectionConfiguration.AbstractorInstances.AbstractorInstance(
        instance_name=instanceName,
        view_name=viewName,
        abstractor_ref=ConfigurableLibraryRefType(
            vendor=abstractorRefVLNV[0],
            library=abstractorRefVLNV[1],
            name=abstractorRefVLNV[2],
            version=abstractorRefVLNV[3],
        ),
    )
    ai.abstractor_instance.append(inst)  # type: ignore[attr-defined]
    register_parent(inst, ai, ("abstractor_instance",), "list")
    return get_handle(inst)


def addAbstractorInstancesInterfaceRef(
    abstractorInstancesID: str, componentRef: str, busRef: str
) -> str:
    """Add an interfaceRef to an abstractorInstances container.

    Section: F.7.40.2.
    """
    ai = _resolve_abstractor_instances(abstractorInstancesID)
    if ai is None:
        raise TgiError("Invalid abstractorInstances handle", TgiFaultCode.INVALID_ID)
    ir = DesignConfiguration.InterconnectionConfiguration.AbstractorInstances.InterfaceRef(
        component_ref=componentRef, bus_ref=busRef
    )
    ai.interface_ref.append(ir)  # type: ignore[attr-defined]
    register_parent(ir, ai, ("interface_ref",), "list")
    return get_handle(ir)


def addDesignConfChoice(designConfigurationID: str, name: str) -> str:
    """Add a ``choice`` element to the designConfiguration.

    Section: F.7.40.3.
    """
    dc = _resolve(designConfigurationID)
    if dc is None:
        raise TgiError("Invalid designConfiguration handle", TgiFaultCode.INVALID_ID)
    if dc.choices is None:
        dc.choices = Choices(choice=[])
    ch = Choices.Choice(name=name)
    dc.choices.choice.append(ch)  # type: ignore[attr-defined]
    register_parent(ch, dc, ("choices",), "list")
    return get_handle(ch)


def addDesignConfigurationGeneratorChainConfiguration(
    designConfigurationID: str, vlnv: tuple[str, str, str, str]
) -> str:
    """Append a generatorChainConfiguration reference.

    Section: F.7.40.4.
    """
    dc = _resolve(designConfigurationID)
    if dc is None:
        raise TgiError("Invalid designConfiguration handle", TgiFaultCode.INVALID_ID)
    ref = ConfigurableLibraryRefType(
        vendor=vlnv[0], library=vlnv[1], name=vlnv[2], version=vlnv[3]
    )
    dc.generator_chain_configuration.append(ref)  # type: ignore[attr-defined]
    register_parent(ref, dc, ("generator_chain_configuration",), "list")
    return get_handle(ref)


def addDesignConfigurationInterconnectionConfiguration(
    designConfigurationID: str, interconnectionRef: str
) -> str:
    """Create and append an interconnectionConfiguration with the given ref.

    Section: F.7.40.5.
    """
    dc = _resolve(designConfigurationID)
    if dc is None:
        raise TgiError("Invalid designConfiguration handle", TgiFaultCode.INVALID_ID)
    ic = DesignConfiguration.InterconnectionConfiguration(
        interconnection_ref=interconnectionRef
    )
    dc.interconnection_configuration.append(ic)  # type: ignore[attr-defined]
    register_parent(ic, dc, ("interconnection_configuration",), "list")
    return get_handle(ic)


def addDesignConfigurationViewConfiguration(
    designConfigurationID: str, instanceName: str, viewRef: str
) -> str:
    """Add a viewConfiguration selecting a viewRef for an instance.

    Section: F.7.40.6.
    """
    dc = _resolve(designConfigurationID)
    if dc is None:
        raise TgiError("Invalid designConfiguration handle", TgiFaultCode.INVALID_ID)
    vc = DesignConfiguration.ViewConfiguration(
        instance_name=InstanceName(value=instanceName),
        view=DesignConfiguration.ViewConfiguration.View(view_ref=viewRef),
    )
    dc.view_configuration.append(vc)  # type: ignore[attr-defined]
    register_parent(vc, dc, ("view_configuration",), "list")
    return get_handle(vc)


def addInterconnectionConfigurationAbstractorInstances(
    interconnectionConfigurationID: str,
) -> str:
    """Append an empty ``abstractorInstances`` grouping.

    Section: F.7.40.7.
    """
    ic = _resolve_interconnection_configuration(interconnectionConfigurationID)
    if ic is None:
        raise TgiError("Invalid interconnectionConfiguration handle", TgiFaultCode.INVALID_ID)
    grp = DesignConfiguration.InterconnectionConfiguration.AbstractorInstances()
    ic.abstractor_instances.append(grp)  # type: ignore[attr-defined]
    register_parent(grp, ic, ("abstractor_instances",), "list")
    return get_handle(grp)


def removeAbstractorInstancesAbstractorInstance(abstractorInstanceID: str) -> bool:
    """Remove an abstractorInstance.

    Section: F.7.40.8. Returns False if handle invalid or not found under its parent.
    """
    inst = _resolve_abstractor_instance(abstractorInstanceID)
    if inst is None:
        return False
    return detach_child_by_handle(abstractorInstanceID)


def removeAbstractorInstancesInterfaceRef(interfaceRefID: str) -> bool:
    """Remove an interfaceRef.

    Section: F.7.40.9.
    """
    ir = _resolve_interface_ref(interfaceRefID)
    if ir is None:
        return False
    return detach_child_by_handle(interfaceRefID)


def removeDesignConfChoice(choiceID: str) -> bool:
    """Remove a design configuration choice.

    Section: F.7.40.10.
    """
    obj = resolve_handle(choiceID)
    # Validate it is a Choices.Choice instance
    if not isinstance(obj, Choices.Choice):  # type: ignore[attr-defined]
        return False
    return detach_child_by_handle(choiceID)


def removeDesignConfigurationDesignRef(designConfigurationID: str) -> bool:
    """Remove the designRef element.

    Section: F.7.40.11.
    """
    dc = _resolve(designConfigurationID)
    if dc is None:
        raise TgiError("Invalid designConfiguration handle", TgiFaultCode.INVALID_ID)
    if dc.design_ref is None:
        return False
    dc.design_ref = None
    return True


def removeDesignConfigurationGeneratorChainConfiguration(generatorChainConfigurationID: str) -> bool:
    """Remove a generatorChainConfiguration reference.

    Section: F.7.40.12.
    """
    obj = resolve_handle(generatorChainConfigurationID)
    if not isinstance(obj, ConfigurableLibraryRefType):
        return False
    return detach_child_by_handle(generatorChainConfigurationID)


def removeDesignConfigurationInterconnectionConfiguration(interconnectionConfigurationID: str) -> bool:
    """Remove an interconnectionConfiguration element.

    Section: F.7.40.13.
    """
    ic = _resolve_interconnection_configuration(interconnectionConfigurationID)
    if ic is None:
        return False
    return detach_child_by_handle(interconnectionConfigurationID)


def removeDesignConfigurationViewConfiguration(viewConfigurationID: str) -> bool:
    """Remove a viewConfiguration element.

    Section: F.7.40.14.
    """
    vc = _resolve_view_configuration(viewConfigurationID)
    if vc is None:
        return False
    return detach_child_by_handle(viewConfigurationID)


def removeInterconnectionConfigurationAbstractorInstances(abstractorInstancesID: str) -> bool:
    """Remove an abstractorInstances grouping.

    Section: F.7.40.15.
    """
    ai = _resolve_abstractor_instances(abstractorInstancesID)
    if ai is None:
        return False
    return detach_child_by_handle(abstractorInstancesID)


def removeViewConfigurationConfigurableElementValue(configurableElementValueID: str) -> bool:
    """Remove a configurableElementValue.

    Section: F.7.40.16.
    """
    cev = _resolve_configurable_element_value(configurableElementValueID)
    if cev is None:
        return False
    return detach_child_by_handle(configurableElementValueID)


def setAbstractorInstanceAbstractorRef(
    abstractorInstanceID: str, vlnv: tuple[str, str, str, str]
) -> bool:
    """Set (replace) the abstractorRef of an abstractorInstance.

    Section: F.7.40.17.
    """
    inst = _resolve_abstractor_instance(abstractorInstanceID)
    if inst is None:
        raise TgiError("Invalid abstractorInstance handle", TgiFaultCode.INVALID_ID)
    inst.abstractor_ref = ConfigurableLibraryRefType(
        vendor=vlnv[0], library=vlnv[1], name=vlnv[2], version=vlnv[3]
    )
    return True


def setAbstractorInstanceInstanceName(abstractorInstanceID: str, instanceName: str) -> bool:
    """Set instanceName of an abstractorInstance.

    Section: F.7.40.18.
    """
    inst = _resolve_abstractor_instance(abstractorInstanceID)
    if inst is None:
        raise TgiError("Invalid abstractorInstance handle", TgiFaultCode.INVALID_ID)
    inst.instance_name = instanceName
    return True


def setAbstractorInstanceViewName(abstractorInstanceID: str, viewName: str) -> bool:
    """Set viewName of an abstractorInstance.

    Section: F.7.40.19.
    """
    inst = _resolve_abstractor_instance(abstractorInstanceID)
    if inst is None:
        raise TgiError("Invalid abstractorInstance handle", TgiFaultCode.INVALID_ID)
    inst.view_name = viewName
    return True


def setDesignConfigurationDesignRef(
    designConfigurationID: str, vlnv: tuple[str, str, str, str]
) -> bool:
    """Set (or create) the designRef reference.

    Section: F.7.40.20.
    """
    dc = _resolve(designConfigurationID)
    if dc is None:
        raise TgiError("Invalid designConfiguration handle", TgiFaultCode.INVALID_ID)
    dc.design_ref = LibraryRefType(
        vendor=vlnv[0], library=vlnv[1], name=vlnv[2], version=vlnv[3]
    )
    return True
