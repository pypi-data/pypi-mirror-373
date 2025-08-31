"""Design category TGI functions (IEEE 1685-2022).

Implements BASE (F.7.37) and EXTENDED (F.7.38) Design functions. Only
standard public TGI APIs are exposed – no convenience helpers beyond the
spec list ("no more, no less").

Each getter follows the error model used across the TGI layer:
* Invalid handle -> ``TgiError`` with ``TgiFaultCode.INVALID_ID`` where the
  spec implies the input must be a valid handle. Where the spec permits an
  empty result, invalid child collections yield empty lists / None instead.
* Mutators return ``True`` on success, ``False`` on semantic no-op (e.g. element
  absent for remove*) and raise ``INVALID_ID`` for bad handles.

Created child elements are registered with parent relationships so that
handle lifecycle & reverse traversal remain coherent inside the DE.
"""
# ruff: noqa: I001
from __future__ import annotations

from collections.abc import Iterable

from org.accellera.ipxact.v1685_2022 import (
    Design,
    Interconnection,
    MonitorInterconnection,
)
from org.accellera.ipxact.v1685_2022.active_interface import ActiveInterface
from org.accellera.ipxact.v1685_2022.hier_interface_type import HierInterfaceType
from org.accellera.ipxact.v1685_2022.monitor_interface_type import MonitorInterfaceType
from org.accellera.ipxact.v1685_2022.ad_hoc_connection import AdHocConnection
from org.accellera.ipxact.v1685_2022.external_port_reference import ExternalPortReference
from org.accellera.ipxact.v1685_2022.sub_port_reference import SubPortReference
from org.accellera.ipxact.v1685_2022.part_select import PartSelect
from org.accellera.ipxact.v1685_2022.component_instance import ComponentInstance
from org.accellera.ipxact.v1685_2022.choices import Choices
from org.accellera.ipxact.v1685_2022.complex_tied_value_expression import ComplexTiedValueExpression
from org.accellera.ipxact.v1685_2022.power_domain_links import PowerDomainLinks

from .core import (
    TgiError,
    TgiFaultCode,
    get_handle,
    resolve_handle,
    register_parent,
    detach_child_by_handle,
)
# Note: expression helper imported indirectly via power domain functions if needed

__all__ = [
    # BASE (F.7.37)
    "getActiveinterfaceExcludePortIDs",
    "getAdHocConnectionExternalPortReferenceIDs",
    "getAdHocConnectionInternalPortReferenceIDs",
    "getAdHocConnectionTiedValue",
    "getAdHocConnectionTiedValueExpression",
    "getAdHocConnectionTiedValueID",
    "getInternalPortReferenceComponentInstanceRefByName",
    "getComponentInstanceComponentRefByID",
    "getComponentInstanceComponentRefByVLNV",
    "getComponentInstanceName",
    "getComponentInstancePowerDomainLinkIDs",
    "getDesignAdHocConnectionIDs",
    "getDesignChoiceIDs",
    "getDesignComponentInstanceIDs",
    "getDesignID",
    "getDesignInterconnectionIDs",
    "getDesignMonitorInterconnectionIDs",
    "getExternalPortReferencePartSelectID",
    "getExternalPortReferencePortRefByName",
    "getExternalPortReferenceSubPortReferenceIDs",
    "getInterconnectionActiveInterfaceIDs",
    "getInterconnectionHierInterfaceIDs",
    "getInternalPortReferencePartSelectID",
    "getInternalPortReferencePortRefByName",
    "getInternalPortReferenceSubPortReferenceIDs",
    "getMonitorInterconnectionMonitorInterfaceIDs",
    "getMonitorInterconnectionMonitoredActiveInterfaceID",
    "getPowerDomainLinkExternalPowerDomainRef",
    "getPowerDomainLinkExternalPowerDomainRefByID",
    "getPowerDomainLinkExternalPowerDomainRefByName",
    "getPowerDomainLinkExternalPowerDomainRefID",
    "getPowerDomainLinkInternalPowerDomainRefs",
    # EXTENDED (F.7.38)
    "addActiveInterfaceExcludePort",
    "addAdHocConnectionExternalPortReference",
    "addAdHocConnectionInternalPortReference",
    "addDesignAdHocConnection",
    "addDesignChoice",
    "addDesignComponentInstance",
    "addDesignExternalAdHocConnection",
    "addDesignInterconnection",
    "addDesignMonitorInterconnection",
    "addInterconnectionActiveInterface",
    "addInterconnectionHierInterface",
    "addMonitorInterconnectionMonitorInterface",
    "removeActiveInterfaceExcludePort",
    "removeAdHocConnectionExternalPortReference",
    "removeAdHocConnectionInternalPortReference",
    "removeAdHocConnectionTiedValue",
    "removeDesignAdHocConnection",
    "removeDesignChoice",
    "removeDesignComponentInstance",
    "removeDesignInterconnection",
    "removeDesignMonitorConnection",
    "removeExternalPortReferencePartSelect",
    "removeExternalPortReferenceSubPortReference",
    "removeInterconnectionActiveInterface",
    "removeInterconnectionHierInterface",
    "removeInternalPortReferencePartSelect",
    "removeInternalPortReferenceSubPortReference",
    "removeMonitorInterconnectionMonitorInterface",
    "setAdHocConnectionTiedValue",
    "setComponentInstanceComponentRef",
    "setExternalPortReferencePartSelect",
    "setInternalPortReferencePartSelect",
    "setInterconnectionActiveInterface",
    "setInterconnectionHierInterface",
    "setMonitorInterconnectionMonitoredActiveInterface",
    "setMonitoredActiveInterfacePath",
    "setPowerDomainLinkExternalPowerDomainRef",
]


# ---------------------------------------------------------------------------
# Helpers (internal – not exported)
# ---------------------------------------------------------------------------

def _resolve_design(designID: str) -> Design | None:
    obj = resolve_handle(designID)
    return obj if isinstance(obj, Design) else None


def _resolve_interconnection(interconnectionID: str) -> Interconnection | None:
    obj = resolve_handle(interconnectionID)
    return obj if isinstance(obj, Interconnection) else None


def _resolve_monitor_interconnection(monitorID: str) -> MonitorInterconnection | None:
    obj = resolve_handle(monitorID)
    return obj if isinstance(obj, MonitorInterconnection) else None


def _resolve_component_instance(instID: str) -> ComponentInstance | None:
    obj = resolve_handle(instID)
    return obj if isinstance(obj, ComponentInstance) else None


def _resolve_ad_hoc(adHocID: str) -> AdHocConnection | None:
    obj = resolve_handle(adHocID)
    return obj if isinstance(obj, AdHocConnection) else None


def _iter(seq: Iterable | None) -> list:
    if seq is None:
        return []
    if isinstance(seq, list):
        return seq
    try:
        return list(seq)
    except Exception:  # pragma: no cover
        return []


# ---------------------------------------------------------------------------
# BASE (F.7.37)
# ---------------------------------------------------------------------------

def getActiveinterfaceExcludePortIDs(activeInterfaceID: str) -> list[str]:
    """Return handles of excludePort elements of an activeInterface.

    Section: F.7.37.1.
    """
    obj = resolve_handle(activeInterfaceID)
    if not isinstance(obj, ActiveInterface):
        raise TgiError("Invalid activeInterface handle", TgiFaultCode.INVALID_ID)
    ex = getattr(obj, "exclude_ports", None)
    if ex is None:
        return []
    return [get_handle(ep) for ep in getattr(ex, "exclude_port", [])]


def getAdHocConnectionExternalPortReferenceIDs(adHocConnectionID: str) -> list[str]:
    """Return handles of externalPortReference children.

    Section: F.7.37.2.
    """
    ac = _resolve_ad_hoc(adHocConnectionID)
    if ac is None:
        raise TgiError("Invalid adHocConnection handle", TgiFaultCode.INVALID_ID)
    pr = getattr(ac, "port_references", None)
    if pr is None:
        return []
    return [get_handle(r) for r in getattr(pr, "external_port_reference", [])]


def getAdHocConnectionInternalPortReferenceIDs(adHocConnectionID: str) -> list[str]:
    """Return handles of internalPortReference children.

    Section: F.7.37.3.
    """
    ac = _resolve_ad_hoc(adHocConnectionID)
    if ac is None:
        raise TgiError("Invalid adHocConnection handle", TgiFaultCode.INVALID_ID)
    pr = getattr(ac, "port_references", None)
    if pr is None:
        return []
    return [get_handle(r) for r in getattr(pr, "internal_port_reference", [])]


def getAdHocConnectionTiedValue(adHocConnectionID: str) -> str | None:
    """Return tiedValue value if present.

    Section: F.7.37.4.
    """
    ac = _resolve_ad_hoc(adHocConnectionID)
    if ac is None:
        raise TgiError("Invalid adHocConnection handle", TgiFaultCode.INVALID_ID)
    tv = getattr(ac, "tied_value", None)
    if tv is None:
        return None
    return getattr(tv, "value", tv)


def getAdHocConnectionTiedValueExpression(adHocConnectionID: str) -> str | None:
    """Return tiedValue expression string.

    Section: F.7.37.5.
    """
    ac = _resolve_ad_hoc(adHocConnectionID)
    if ac is None:
        raise TgiError("Invalid adHocConnection handle", TgiFaultCode.INVALID_ID)
    tv = getattr(ac, "tied_value", None)
    if tv is None:
        return None
    return getattr(tv, "value", None)


def getAdHocConnectionTiedValueID(adHocConnectionID: str) -> str | None:
    """Return handle of tiedValue element.

    Section: F.7.37.6.
    """
    ac = _resolve_ad_hoc(adHocConnectionID)
    if ac is None:
        raise TgiError("Invalid adHocConnection handle", TgiFaultCode.INVALID_ID)
    tv = getattr(ac, "tied_value", None)
    return None if tv is None else get_handle(tv)


def getInternalPortReferenceComponentInstanceRefByName(internalPortReferenceID: str) -> str | None:
    """Return componentInstanceRef attribute value.

    Section: F.7.37.7.
    """
    obj = resolve_handle(internalPortReferenceID)
    # internalPortReference is nested dataclass
    if not isinstance(obj, AdHocConnection.PortReferences.InternalPortReference):  # type: ignore[attr-defined]
        raise TgiError("Invalid internalPortReference handle", TgiFaultCode.INVALID_ID)
    return getattr(obj, "component_instance_ref", None)


def getComponentInstanceComponentRefByID(componentInstanceID: str) -> str | None:
    """Return handle of referenced component (componentRef).

    Section: F.7.37.8. (Design currently does not resolve to actual component object – placeholder None)
    """
    inst = _resolve_component_instance(componentInstanceID)
    if inst is None:
        raise TgiError("Invalid componentInstance handle", TgiFaultCode.INVALID_ID)
    # The XML schema holds only VLNV strings; resolution to component object would be DE responsibility.
    return None


def getComponentInstanceComponentRefByVLNV(
    componentInstanceID: str,
) -> tuple[str | None, str | None, str | None, str | None]:
    """Return (vendor, library, name, version) VLNV referenced.

    Section: F.7.37.9.
    """
    inst = _resolve_component_instance(componentInstanceID)
    if inst is None:
        raise TgiError("Invalid componentInstance handle", TgiFaultCode.INVALID_ID)
    comp_ref = getattr(inst, "component_ref", None)
    if comp_ref is None:
        return (None, None, None, None)
    return (
        getattr(comp_ref, "vendor", None),
        getattr(comp_ref, "library", None),
        getattr(comp_ref, "name", None),
        getattr(comp_ref, "version", None),
    )


def getComponentInstanceName(componentInstanceID: str) -> str | None:
    """Return componentInstance name.

    Section: F.7.37.10.
    """
    inst = _resolve_component_instance(componentInstanceID)
    if inst is None:
        raise TgiError("Invalid componentInstance handle", TgiFaultCode.INVALID_ID)
    return getattr(inst, "instance_name", None)


def getComponentInstancePowerDomainLinkIDs(componentInstanceID: str) -> list[str]:  # F.7.37.11
    from .power import getComponentInstancePowerDomainLinkIDs as _g

    return _g(componentInstanceID)


def getDesignAdHocConnectionIDs(designID: str) -> list[str]:
    """Return handles of adHocConnection children.

    Section: F.7.37.12.
    """
    d = _resolve_design(designID)
    if d is None:
        raise TgiError("Invalid design handle", TgiFaultCode.INVALID_ID)
    if d.ad_hoc_connections is None:
        return []
    return [get_handle(a) for a in getattr(d.ad_hoc_connections, "ad_hoc_connection", [])]


def getDesignChoiceIDs(designID: str) -> list[str]:
    """Return handles of choice elements.

    Section: F.7.37.13.
    """
    d = _resolve_design(designID)
    if d is None:
        raise TgiError("Invalid design handle", TgiFaultCode.INVALID_ID)
    if d.choices is None:
        return []
    return [get_handle(c) for c in getattr(d.choices, "choice", [])]


def getDesignComponentInstanceIDs(designID: str) -> list[str]:
    """Return handles of componentInstance elements.

    Section: F.7.37.14.
    """
    d = _resolve_design(designID)
    if d is None:
        raise TgiError("Invalid design handle", TgiFaultCode.INVALID_ID)
    if d.component_instances is None:
        return []
    return [get_handle(ci) for ci in getattr(d.component_instances, "component_instance", [])]


def getDesignID(top: bool) -> str | None:
    """Return handle to current or top design.

    Section: F.7.37.15. (Current DE context not tracked; return None.)
    """
    # Without a session manager context we cannot distinguish; placeholder None.
    return None


def getDesignInterconnectionIDs(designID: str) -> list[str]:
    """Return handles of interconnection elements.

    Section: F.7.37.16.
    """
    d = _resolve_design(designID)
    if d is None:
        raise TgiError("Invalid design handle", TgiFaultCode.INVALID_ID)
    if d.interconnections is None:
        return []
    return [get_handle(i) for i in getattr(d.interconnections, "interconnection", [])]


def getDesignMonitorInterconnectionIDs(designID: str) -> list[str]:
    """Return handles of monitorInterconnection elements.

    Section: F.7.37.17.
    """
    d = _resolve_design(designID)
    if d is None:
        raise TgiError("Invalid design handle", TgiFaultCode.INVALID_ID)
    if d.interconnections is None:
        return []
    return [get_handle(mi) for mi in getattr(d.interconnections, "monitor_interconnection", [])]


def getExternalPortReferencePartSelectID(externalPortReferenceID: str) -> str | None:
    """Return handle of partSelect element of externalPortReference.

    Section: F.7.37.18.
    """
    obj = resolve_handle(externalPortReferenceID)
    if not isinstance(obj, ExternalPortReference):
        raise TgiError("Invalid externalPortReference handle", TgiFaultCode.INVALID_ID)
    ps = getattr(obj, "part_select", None)
    return None if ps is None else get_handle(ps)


def getExternalPortReferencePortRefByName(externalPortReferenceID: str) -> str | None:
    """Return portRef attribute of externalPortReference.

    Section: F.7.37.19.
    """
    obj = resolve_handle(externalPortReferenceID)
    if not isinstance(obj, ExternalPortReference):
        raise TgiError("Invalid externalPortReference handle", TgiFaultCode.INVALID_ID)
    return getattr(obj, "port_ref", None)


def getExternalPortReferenceSubPortReferenceIDs(externalPortReferenceID: str) -> list[str]:
    """Return handles of subPortReference elements for externalPortReference.

    Section: F.7.37.20.
    """
    obj = resolve_handle(externalPortReferenceID)
    if not isinstance(obj, ExternalPortReference):
        raise TgiError("Invalid externalPortReference handle", TgiFaultCode.INVALID_ID)
    return [get_handle(sp) for sp in getattr(obj, "sub_port_reference", [])]


def getInterconnectionActiveInterfaceIDs(interconnectionID: str) -> list[str]:
    """Return handles of activeInterface children.

    Section: F.7.37.21.
    """
    ic = _resolve_interconnection(interconnectionID)
    if ic is None:
        raise TgiError("Invalid interconnection handle", TgiFaultCode.INVALID_ID)
    return [get_handle(ai) for ai in getattr(ic, "active_interface", [])]


def getInterconnectionHierInterfaceIDs(interconnectionID: str) -> list[str]:
    """Return handles of hierInterface children.

    Section: F.7.37.22.
    """
    ic = _resolve_interconnection(interconnectionID)
    if ic is None:
        raise TgiError("Invalid interconnection handle", TgiFaultCode.INVALID_ID)
    return [get_handle(hi) for hi in getattr(ic, "hier_interface", [])]


def getInternalPortReferencePartSelectID(internalPortReferenceID: str) -> str | None:
    """Return handle of partSelect element for internalPortReference.

    Section: F.7.37.23.
    """
    obj = resolve_handle(internalPortReferenceID)
    if not isinstance(obj, AdHocConnection.PortReferences.InternalPortReference):  # type: ignore[attr-defined]
        raise TgiError("Invalid internalPortReference handle", TgiFaultCode.INVALID_ID)
    ps = getattr(obj, "part_select", None)
    return None if ps is None else get_handle(ps)


def getInternalPortReferencePortRefByName(internalPortReferenceID: str) -> str | None:
    """Return portRef attribute from internalPortReference.

    Section: F.7.37.24.
    """
    obj = resolve_handle(internalPortReferenceID)
    if not isinstance(obj, AdHocConnection.PortReferences.InternalPortReference):  # type: ignore[attr-defined]
        raise TgiError("Invalid internalPortReference handle", TgiFaultCode.INVALID_ID)
    return getattr(obj, "port_ref", None)


def getInternalPortReferenceSubPortReferenceIDs(internalPortReferenceID: str) -> list[str]:
    """Return handles of subPortReference elements of internalPortReference.

    Section: F.7.37.25.
    """
    obj = resolve_handle(internalPortReferenceID)
    if not isinstance(obj, AdHocConnection.PortReferences.InternalPortReference):  # type: ignore[attr-defined]
        raise TgiError("Invalid internalPortReference handle", TgiFaultCode.INVALID_ID)
    return [get_handle(sp) for sp in getattr(obj, "sub_port_reference", [])]


def getMonitorInterconnectionMonitorInterfaceIDs(monitorInterconnectionID: str) -> list[str]:
    """Return handles of monitorInterface elements.

    Section: F.7.37.26.
    """
    mi = _resolve_monitor_interconnection(monitorInterconnectionID)
    if mi is None:
        raise TgiError("Invalid monitorInterconnection handle", TgiFaultCode.INVALID_ID)
    return [get_handle(m) for m in getattr(mi, "monitor_interface", [])]


def getMonitorInterconnectionMonitoredActiveInterfaceID(monitorInterconnectionID: str) -> str | None:
    """Return handle of monitoredActiveInterface element.

    Section: F.7.37.27.
    """
    mi = _resolve_monitor_interconnection(monitorInterconnectionID)
    if mi is None:
        raise TgiError("Invalid monitorInterconnection handle", TgiFaultCode.INVALID_ID)
    mai = getattr(mi, "monitored_active_interface", None)
    return None if mai is None else get_handle(mai)


def getPowerDomainLinkExternalPowerDomainRef(powerDomainLinkID: str) -> str | None:
    """Return external power domain value from powerDomainLink.

    Section: F.7.37.28.
    """
    link = resolve_handle(powerDomainLinkID)
    if not isinstance(link, PowerDomainLinks.PowerDomainLink):  # type: ignore[attr-defined]
        raise TgiError("Invalid powerDomainLink handle", TgiFaultCode.INVALID_ID)
    ext = getattr(link, "external_power_domain_reference", None)
    if ext is None:
        return None
    return getattr(ext, "value", ext)


def getPowerDomainLinkExternalPowerDomainRefByID(powerDomainLinkID: str) -> str | None:
    """Return handle to referenced external power domain (not resolved).

    Section: F.7.37.29. (Not resolvable without external library; returns None.)
    """
    link = resolve_handle(powerDomainLinkID)
    if not isinstance(link, PowerDomainLinks.PowerDomainLink):  # type: ignore[attr-defined]
        raise TgiError("Invalid powerDomainLink handle", TgiFaultCode.INVALID_ID)
    return None


def getPowerDomainLinkExternalPowerDomainRefByName(powerDomainLinkID: str) -> str | None:
    """Return external power domain referenced (string).

    Section: F.7.37.30.
    """
    return getPowerDomainLinkExternalPowerDomainRef(powerDomainLinkID)


def getPowerDomainLinkExternalPowerDomainRefID(powerDomainLinkID: str) -> str | None:
    """Return handle of external power domain expression element.

    Section: F.7.37.32.
    """
    link = resolve_handle(powerDomainLinkID)
    if not isinstance(link, PowerDomainLinks.PowerDomainLink):  # type: ignore[attr-defined]
        raise TgiError("Invalid powerDomainLink handle", TgiFaultCode.INVALID_ID)
    ext = getattr(link, "external_power_domain_reference", None)
    return None if ext is None else get_handle(ext)


def getPowerDomainLinkInternalPowerDomainRefs(powerDomainLinkID: str) -> list[str]:
    """Return internal power domain reference expressions (strings).

    Section: F.7.37.33.
    """
    link = resolve_handle(powerDomainLinkID)
    if not isinstance(link, PowerDomainLinks.PowerDomainLink):  # type: ignore[attr-defined]
        raise TgiError("Invalid powerDomainLink handle", TgiFaultCode.INVALID_ID)
    refs: list[str] = []
    for ref in getattr(link, "internal_power_domain_reference", []):
        val = getattr(ref, "value", ref)
        if isinstance(val, str):
            refs.append(val)
    return refs


# ---------------------------------------------------------------------------
# EXTENDED (F.7.38)
# ---------------------------------------------------------------------------

def addActiveInterfaceExcludePort(activeInterfaceID: str, excludePort: str) -> str:
    """Add an excludePort to an activeInterface.

    Section: F.7.38.1.
    """
    ai = resolve_handle(activeInterfaceID)
    if not isinstance(ai, ActiveInterface):
        raise TgiError("Invalid activeInterface handle", TgiFaultCode.INVALID_ID)
    if ai.exclude_ports is None:
        ai.exclude_ports = ActiveInterface.ExcludePorts()  # type: ignore[assignment]
    ep = ActiveInterface.ExcludePorts.ExcludePort(value=excludePort)  # type: ignore[attr-defined]
    ai.exclude_ports.exclude_port.append(ep)  # type: ignore[attr-defined]
    register_parent(ep, ai, ("exclude_ports",), "list")
    return get_handle(ep)


def addAdHocConnectionExternalPortReference(adHocConnectionID: str, portRef: str) -> str:
    """Add externalPortReference with portRef to adHocConnection.

    Section: F.7.38.2.
    """
    ac = _resolve_ad_hoc(adHocConnectionID)
    if ac is None:
        raise TgiError("Invalid adHocConnection handle", TgiFaultCode.INVALID_ID)
    if ac.port_references is None:
        ac.port_references = AdHocConnection.PortReferences()  # type: ignore[assignment]
    epr = ExternalPortReference(port_ref=portRef)
    ac.port_references.external_port_reference.append(epr)  # type: ignore[attr-defined]
    register_parent(epr, ac, ("port_references",), "list")
    return get_handle(epr)


def addAdHocConnectionInternalPortReference(adHocConnectionID: str, componentInstanceRef: str, portRef: str) -> str:
    """Add internalPortReference.

    Section: F.7.38.3.
    """
    ac = _resolve_ad_hoc(adHocConnectionID)
    if ac is None:
        raise TgiError("Invalid adHocConnection handle", TgiFaultCode.INVALID_ID)
    if ac.port_references is None:
        ac.port_references = AdHocConnection.PortReferences()  # type: ignore[assignment]
    ipr = AdHocConnection.PortReferences.InternalPortReference(  # type: ignore[attr-defined]
        component_instance_ref=componentInstanceRef,
        port_ref=portRef,
    )
    ac.port_references.internal_port_reference.append(ipr)  # type: ignore[attr-defined]
    register_parent(ipr, ac, ("port_references",), "list")
    return get_handle(ipr)


def addDesignAdHocConnection(designID: str, name: str, componentInstanceRef: str, portRef: str) -> str:
    """Add adHocConnection with one internalPortReference.

    Section: F.7.38.4.
    """
    d = _resolve_design(designID)
    if d is None:
        raise TgiError("Invalid design handle", TgiFaultCode.INVALID_ID)
    if d.ad_hoc_connections is None:
        from org.accellera.ipxact.v1685_2022.ad_hoc_connections import AdHocConnections

        d.ad_hoc_connections = AdHocConnections()  # type: ignore[assignment]
    ac = AdHocConnection(name=name)
    # init port_references
    ac.port_references = AdHocConnection.PortReferences()  # type: ignore[assignment]
    ipr = AdHocConnection.PortReferences.InternalPortReference(  # type: ignore[attr-defined]
        component_instance_ref=componentInstanceRef,
        port_ref=portRef,
    )
    ac.port_references.internal_port_reference.append(ipr)  # type: ignore[attr-defined]
    d.ad_hoc_connections.ad_hoc_connection.append(ac)  # type: ignore[attr-defined]
    register_parent(ac, d, ("ad_hoc_connections",), "list")
    register_parent(ipr, ac, ("port_references",), "list")
    return get_handle(ac)


def addDesignChoice(designID: str, name: str, enumerations: list[str] | None = None) -> str:
    """Add choice with name and enumerations.

    Section: F.7.38.5.
    """
    d = _resolve_design(designID)
    if d is None:
        raise TgiError("Invalid design handle", TgiFaultCode.INVALID_ID)
    if d.choices is None:
        d.choices = Choices()  # type: ignore[assignment]
    choice = Choices.Choice(name=name)  # type: ignore[attr-defined]
    if enumerations:
        choice.enumeration = list(enumerations)  # type: ignore[attr-defined]
    d.choices.choice.append(choice)  # type: ignore[attr-defined]
    register_parent(choice, d, ("choices",), "list")
    return get_handle(choice)


def addDesignComponentInstance(
    designID: str,
    componentVLNV: tuple[str, str, str, str],
    componentInstanceName: str,
) -> str:
    """Add componentInstance referencing component VLNV.

    Section: F.7.38.6.
    """
    from org.accellera.ipxact.v1685_2022.library_ref_type import LibraryRefType

    d = _resolve_design(designID)
    if d is None:
        raise TgiError("Invalid design handle", TgiFaultCode.INVALID_ID)
    if d.component_instances is None:
        from org.accellera.ipxact.v1685_2022.component_instances import ComponentInstances

        d.component_instances = ComponentInstances()  # type: ignore[assignment]
    ci = ComponentInstance(instance_name=componentInstanceName)  # type: ignore[call-arg]
    # component_ref is ConfigurableLibraryRefType or LibraryRefType in schema; we use LibraryRefType
    ci.component_ref = LibraryRefType(
        vendor=componentVLNV[0],
        library=componentVLNV[1],
        name=componentVLNV[2],
        version=componentVLNV[3],
    )  # type: ignore[attr-defined]
    d.component_instances.component_instance.append(ci)  # type: ignore[attr-defined]
    register_parent(ci, d, ("component_instances",), "list")
    return get_handle(ci)


def addDesignExternalAdHocConnection(designID: str, name: str, portRef: str) -> str:
    """Add adHocConnection with single externalPortReference.

    Section: F.7.38.7.
    """
    d = _resolve_design(designID)
    if d is None:
        raise TgiError("Invalid design handle", TgiFaultCode.INVALID_ID)
    if d.ad_hoc_connections is None:
        from org.accellera.ipxact.v1685_2022.ad_hoc_connections import AdHocConnections

        d.ad_hoc_connections = AdHocConnections()  # type: ignore[assignment]
    ac = AdHocConnection(name=name)
    ac.port_references = AdHocConnection.PortReferences()  # type: ignore[assignment]
    epr = ExternalPortReference(port_ref=portRef)
    ac.port_references.external_port_reference.append(epr)  # type: ignore[attr-defined]
    d.ad_hoc_connections.ad_hoc_connection.append(ac)  # type: ignore[attr-defined]
    register_parent(ac, d, ("ad_hoc_connections",), "list")
    register_parent(epr, ac, ("port_references",), "list")
    return get_handle(ac)


def addDesignInterconnection(
    designID: str,
    name: str,
    componentInstanceRef1: str,
    busInterfaceRef1: str,
    componentInstanceRef2: str,
    busInterfaceRef2: str,
) -> str:
    """Add interconnection with two activeInterface endpoints.

    Section: F.7.38.8.
    """
    d = _resolve_design(designID)
    if d is None:
        raise TgiError("Invalid design handle", TgiFaultCode.INVALID_ID)
    if d.interconnections is None:
        from org.accellera.ipxact.v1685_2022.interconnections import Interconnections as InterconnectionsContainer

        d.interconnections = InterconnectionsContainer()  # type: ignore[assignment]
    ic = Interconnection(name=name)
    ai1 = ActiveInterface(component_interface_ref=componentInstanceRef1, bus_ref=busInterfaceRef1)  # type: ignore[call-arg]
    ai2 = ActiveInterface(component_interface_ref=componentInstanceRef2, bus_ref=busInterfaceRef2)  # type: ignore[call-arg]
    ic.active_interface.extend([ai1, ai2])  # type: ignore[attr-defined]
    d.interconnections.interconnection.append(ic)  # type: ignore[attr-defined]
    register_parent(ic, d, ("interconnections",), "list")
    register_parent(ai1, ic, ("active_interface",), "list")
    register_parent(ai2, ic, ("active_interface",), "list")
    return get_handle(ic)


def addDesignMonitorInterconnection(
    designID: str,
    name: str,
    componentInstanceRef1: str,
    activeInterfaceBusInterfaceRef: str,
    componentInstanceRef2: str,
    interfaceBusInterfaceRef: str,
) -> str:
    """Add monitorInterconnection with monitoredActiveInterface + monitorInterface.

    Section: F.7.38.9.
    """
    d = _resolve_design(designID)
    if d is None:
        raise TgiError("Invalid design handle", TgiFaultCode.INVALID_ID)
    if d.interconnections is None:
        from org.accellera.ipxact.v1685_2022.interconnections import Interconnections as InterconnectionsContainer

        d.interconnections = InterconnectionsContainer()  # type: ignore[assignment]
    mi = MonitorInterconnection(name=name)
    mai = MonitorInterfaceType(component_interface_ref=componentInstanceRef1, bus_ref=activeInterfaceBusInterfaceRef)  # type: ignore[call-arg]
    mon = MonitorInterfaceType(component_interface_ref=componentInstanceRef2, bus_ref=interfaceBusInterfaceRef)  # type: ignore[call-arg]
    mi.monitored_active_interface = mai  # type: ignore[assignment]
    mi.monitor_interface.append(mon)  # type: ignore[attr-defined]
    d.interconnections.monitor_interconnection.append(mi)  # type: ignore[attr-defined]
    register_parent(mi, d, ("interconnections",), "list")
    register_parent(mai, mi, ("monitored_active_interface",), "single")
    register_parent(mon, mi, ("monitor_interface",), "list")
    return get_handle(mi)


def addInterconnectionActiveInterface(interconnectionID: str, componentInstanceRef: str, busInterfaceRef: str) -> str:
    """Add an activeInterface to an interconnection.

    Section: F.7.38.10.
    """
    ic = _resolve_interconnection(interconnectionID)
    if ic is None:
        raise TgiError("Invalid interconnection handle", TgiFaultCode.INVALID_ID)
    ai = ActiveInterface(component_interface_ref=componentInstanceRef, bus_ref=busInterfaceRef)  # type: ignore[call-arg]
    ic.active_interface.append(ai)  # type: ignore[attr-defined]
    register_parent(ai, ic, ("active_interface",), "list")
    return get_handle(ai)


def addInterconnectionHierInterface(interconnectionID: str, busInterfaceRef: str) -> str:
    """Add a hierInterface to an interconnection.

    Section: F.7.38.11.
    """
    ic = _resolve_interconnection(interconnectionID)
    if ic is None:
        raise TgiError("Invalid interconnection handle", TgiFaultCode.INVALID_ID)
    hi = HierInterfaceType(bus_ref=busInterfaceRef)  # type: ignore[call-arg]
    ic.hier_interface.append(hi)  # type: ignore[attr-defined]
    register_parent(hi, ic, ("hier_interface",), "list")
    return get_handle(hi)


def addMonitorInterconnectionMonitorInterface(
    monitorInterconnectionID: str,
    componentInstanceRef: str,
    busInterfaceRef: str,
) -> str:
    """Add monitorInterface to a monitorInterconnection.

    Section: F.7.38.12.
    """
    mi = _resolve_monitor_interconnection(monitorInterconnectionID)
    if mi is None:
        raise TgiError("Invalid monitorInterconnection handle", TgiFaultCode.INVALID_ID)
    m = MonitorInterfaceType(component_interface_ref=componentInstanceRef, bus_ref=busInterfaceRef)  # type: ignore[call-arg]
    mi.monitor_interface.append(m)  # type: ignore[attr-defined]
    register_parent(m, mi, ("monitor_interface",), "list")
    return get_handle(m)


def removeActiveInterfaceExcludePort(excludePortID: str) -> bool:
    """Remove excludePort element.

    Section: F.7.38.13.
    """
    ep = resolve_handle(excludePortID)
    if not isinstance(ep, ActiveInterface.ExcludePorts.ExcludePort):  # type: ignore[attr-defined]
        raise TgiError("Invalid excludePort handle", TgiFaultCode.INVALID_ID)
    return detach_child_by_handle(excludePortID)


def removeAdHocConnectionExternalPortReference(externalPortReferenceID: str) -> bool:
    """Remove externalPortReference element.

    Section: F.7.38.14.
    """
    obj = resolve_handle(externalPortReferenceID)
    if not isinstance(obj, ExternalPortReference):
        raise TgiError("Invalid externalPortReference handle", TgiFaultCode.INVALID_ID)
    return detach_child_by_handle(externalPortReferenceID)


def removeAdHocConnectionInternalPortReference(internalPortReferenceID: str) -> bool:
    """Remove internalPortReference element.

    Section: F.7.38.15.
    """
    obj = resolve_handle(internalPortReferenceID)
    if not isinstance(obj, AdHocConnection.PortReferences.InternalPortReference):  # type: ignore[attr-defined]
        raise TgiError("Invalid internalPortReference handle", TgiFaultCode.INVALID_ID)
    return detach_child_by_handle(internalPortReferenceID)


def removeAdHocConnectionTiedValue(adHocConnectionID: str) -> bool:
    """Remove tiedValue element from adHocConnection.

    Section: F.7.38.16.
    """
    ac = _resolve_ad_hoc(adHocConnectionID)
    if ac is None:
        raise TgiError("Invalid adHocConnection handle", TgiFaultCode.INVALID_ID)
    if getattr(ac, "tied_value", None) is None:
        return False
    ac.tied_value = None
    return True


def removeDesignAdHocConnection(adHocConnectionID: str) -> bool:
    """Remove adHocConnection element.

    Section: F.7.38.17.
    """
    obj = resolve_handle(adHocConnectionID)
    if not isinstance(obj, AdHocConnection):
        raise TgiError("Invalid adHocConnection handle", TgiFaultCode.INVALID_ID)
    return detach_child_by_handle(adHocConnectionID)


def removeDesignChoice(choiceID: str) -> bool:
    """Remove choice element.

    Section: F.7.38.18.
    """
    ch = resolve_handle(choiceID)
    if not isinstance(ch, Choices.Choice):  # type: ignore[attr-defined]
        raise TgiError("Invalid choice handle", TgiFaultCode.INVALID_ID)
    return detach_child_by_handle(choiceID)


def removeDesignComponentInstance(componentInstanceID: str) -> bool:
    """Remove componentInstance element.

    Section: F.7.38.19.
    """
    ci = _resolve_component_instance(componentInstanceID)
    if ci is None:
        raise TgiError("Invalid componentInstance handle", TgiFaultCode.INVALID_ID)
    return detach_child_by_handle(componentInstanceID)


def removeDesignInterconnection(interconnectionID: str) -> bool:
    """Remove interconnection element.

    Section: F.7.38.20.
    """
    ic = _resolve_interconnection(interconnectionID)
    if ic is None:
        raise TgiError("Invalid interconnection handle", TgiFaultCode.INVALID_ID)
    return detach_child_by_handle(interconnectionID)


def removeDesignMonitorConnection(monitorInterconnectionID: str) -> bool:
    """Remove monitorInterconnection element.

    Section: F.7.38.21.
    """
    mi = _resolve_monitor_interconnection(monitorInterconnectionID)
    if mi is None:
        raise TgiError("Invalid monitorInterconnection handle", TgiFaultCode.INVALID_ID)
    return detach_child_by_handle(monitorInterconnectionID)


def removeExternalPortReferencePartSelect(externalPortReferenceID: str) -> bool:
    """Remove partSelect from externalPortReference.

    Section: F.7.38.22.
    """
    obj = resolve_handle(externalPortReferenceID)
    if not isinstance(obj, ExternalPortReference):
        raise TgiError("Invalid externalPortReference handle", TgiFaultCode.INVALID_ID)
    if getattr(obj, "part_select", None) is None:
        return False
    obj.part_select = None
    return True


def removeExternalPortReferenceSubPortReference(subPortRefID: str) -> bool:
    """Remove a subPortReference element (external).

    Section: F.7.38.23.
    """
    spr = resolve_handle(subPortRefID)
    if not isinstance(spr, SubPortReference):
        raise TgiError("Invalid subPortReference handle", TgiFaultCode.INVALID_ID)
    return detach_child_by_handle(subPortRefID)


def removeInterconnectionActiveInterface(activeInterfaceID: str) -> bool:
    """Remove activeInterface element.

    Section: F.7.38.24.
    """
    ai = resolve_handle(activeInterfaceID)
    if not isinstance(ai, ActiveInterface):
        raise TgiError("Invalid activeInterface handle", TgiFaultCode.INVALID_ID)
    return detach_child_by_handle(activeInterfaceID)


def removeInterconnectionHierInterface(hierInterfaceID: str) -> bool:
    """Remove hierInterface element.

    Section: F.7.38.25.
    """
    hi = resolve_handle(hierInterfaceID)
    if not isinstance(hi, HierInterfaceType):
        raise TgiError("Invalid hierInterface handle", TgiFaultCode.INVALID_ID)
    return detach_child_by_handle(hierInterfaceID)


def removeInternalPortReferencePartSelect(internalPortReferenceID: str) -> bool:
    """Remove partSelect from internalPortReference.

    Section: F.7.38.26.
    """
    obj = resolve_handle(internalPortReferenceID)
    if not isinstance(obj, AdHocConnection.PortReferences.InternalPortReference):  # type: ignore[attr-defined]
        raise TgiError("Invalid internalPortReference handle", TgiFaultCode.INVALID_ID)
    if getattr(obj, "part_select", None) is None:
        return False
    obj.part_select = None
    return True


def removeInternalPortReferenceSubPortReference(subPortRefID: str) -> bool:
    """Remove subPortReference element (internal).

    Section: F.7.38.27.
    """
    spr = resolve_handle(subPortRefID)
    if not isinstance(spr, SubPortReference):
        raise TgiError("Invalid subPortReference handle", TgiFaultCode.INVALID_ID)
    return detach_child_by_handle(subPortRefID)


def removeMonitorInterconnectionMonitorInterface(monitorInterfaceID: str) -> bool:
    """Remove monitorInterface element.

    Section: F.7.38.28.
    """
    m = resolve_handle(monitorInterfaceID)
    if not isinstance(m, MonitorInterfaceType):
        raise TgiError("Invalid monitorInterface handle", TgiFaultCode.INVALID_ID)
    return detach_child_by_handle(monitorInterfaceID)


def setAdHocConnectionTiedValue(adHocConnectionID: str, tiedValue: str) -> bool:
    """Set tiedValue value (creates element if absent).

    Section: F.7.38.29.
    """
    ac = _resolve_ad_hoc(adHocConnectionID)
    if ac is None:
        raise TgiError("Invalid adHocConnection handle", TgiFaultCode.INVALID_ID)
    if ac.tied_value is None:
        ac.tied_value = ComplexTiedValueExpression(value=tiedValue)  # type: ignore[assignment]
    else:
        ac.tied_value.value = tiedValue  # type: ignore[attr-defined]
    return True


def setComponentInstanceComponentRef(componentInstanceID: str, componentVLNV: tuple[str, str, str, str]) -> bool:
    """Set componentRef VLNV on componentInstance.

    Section: F.7.38.30.
    """
    from org.accellera.ipxact.v1685_2022.library_ref_type import LibraryRefType

    inst = _resolve_component_instance(componentInstanceID)
    if inst is None:
        raise TgiError("Invalid componentInstance handle", TgiFaultCode.INVALID_ID)
    inst.component_ref = LibraryRefType(
        vendor=componentVLNV[0],
        library=componentVLNV[1],
        name=componentVLNV[2],
        version=componentVLNV[3],
    )  # type: ignore[assignment]
    return True


def setExternalPortReferencePartSelect(
    externalPortReferenceID: str,
    range: tuple[str, str] | None,
    indices: list[str] | None,
) -> bool:
    """Set partSelect on externalPortReference (replaces existing).

    Section: F.7.38.31.
    """
    obj = resolve_handle(externalPortReferenceID)
    if not isinstance(obj, ExternalPortReference):
        raise TgiError("Invalid externalPortReference handle", TgiFaultCode.INVALID_ID)
    ps = PartSelect()
    if range:
        ps.left = range[0]  # type: ignore[attr-defined]
        ps.right = range[1]  # type: ignore[attr-defined]
    if indices:
        ps.index = list(indices)  # type: ignore[attr-defined]
    obj.part_select = ps
    register_parent(ps, obj, ("part_select",), "single")
    return True


def setInternalPortReferencePartSelect(
    internalPortReferenceID: str,
    range: tuple[str, str] | None,
    indices: list[str] | None,
) -> bool:
    """Set partSelect on internalPortReference.

    Section: F.7.38.32.
    """
    obj = resolve_handle(internalPortReferenceID)
    if not isinstance(obj, AdHocConnection.PortReferences.InternalPortReference):  # type: ignore[attr-defined]
        raise TgiError("Invalid internalPortReference handle", TgiFaultCode.INVALID_ID)
    ps = PartSelect()
    if range:
        ps.left = range[0]  # type: ignore[attr-defined]
        ps.right = range[1]  # type: ignore[attr-defined]
    if indices:
        ps.index = list(indices)  # type: ignore[attr-defined]
    obj.part_select = ps
    register_parent(ps, obj, ("part_select",), "single")
    return True


def setInterconnectionActiveInterface(interconnectionID: str, componentInstanceRef: str, busRef: str) -> bool:
    """Set (replace) first activeInterface of interconnection.

    Section: F.7.38.33.
    """
    ic = _resolve_interconnection(interconnectionID)
    if ic is None:
        raise TgiError("Invalid interconnection handle", TgiFaultCode.INVALID_ID)
    interfaces = list(getattr(ic, "active_interface", []))
    new_ai = ActiveInterface(component_interface_ref=componentInstanceRef, bus_ref=busRef)  # type: ignore[call-arg]
    if interfaces:
        # Replace first
        old = interfaces[0]
        interfaces[0] = new_ai
        ic.active_interface = interfaces  # type: ignore[assignment]
        detach_child_by_handle(get_handle(old))
    else:  # Ensure list
        interfaces.append(new_ai)
        ic.active_interface = interfaces  # type: ignore[assignment]
    register_parent(new_ai, ic, ("active_interface",), "list")
    return True


def setInterconnectionHierInterface(interconnectionID: str, busRef: str) -> bool:
    """Set (replace) first hierInterface entry.

    Section: F.7.38.34.
    """
    ic = _resolve_interconnection(interconnectionID)
    if ic is None:
        raise TgiError("Invalid interconnection handle", TgiFaultCode.INVALID_ID)
    current = list(getattr(ic, "hier_interface", []))
    hi = HierInterfaceType(bus_ref=busRef)  # type: ignore[call-arg]
    if current:
        old = current[0]
        current[0] = hi
        ic.hier_interface = current  # type: ignore[assignment]
        detach_child_by_handle(get_handle(old))
    else:
        current.append(hi)
        ic.hier_interface = current  # type: ignore[assignment]
    register_parent(hi, ic, ("hier_interface",), "list")
    return True


def setMonitorInterconnectionMonitoredActiveInterface(
    monitorInterconnectionID: str,
    componentInstanceRef: str,
    busRef: str,
) -> bool:
    """Set monitoredActiveInterface element.

    Section: F.7.38.35.
    """
    mi = _resolve_monitor_interconnection(monitorInterconnectionID)
    if mi is None:
        raise TgiError("Invalid monitorInterconnection handle", TgiFaultCode.INVALID_ID)
    mai = MonitorInterfaceType(component_interface_ref=componentInstanceRef, bus_ref=busRef)  # type: ignore[call-arg]
    mi.monitored_active_interface = mai  # type: ignore[assignment]
    register_parent(mai, mi, ("monitored_active_interface",), "single")
    return True


def setMonitoredActiveInterfacePath(monitoredActiveInterfaceID: str, path: str) -> bool:
    """Set path attribute on monitoredActiveInterface.

    Section: F.7.38.36.
    """
    mai = resolve_handle(monitoredActiveInterfaceID)
    if not isinstance(mai, MonitorInterfaceType):
        raise TgiError("Invalid monitoredActiveInterface handle", TgiFaultCode.INVALID_ID)
    mai.path = path
    return True


def setPowerDomainLinkExternalPowerDomainRef(powerDomainLinkID: str, expression: str) -> bool:
    """Set external power domain reference expression.

    Section: F.7.38.37.
    """
    link = resolve_handle(powerDomainLinkID)
    if not isinstance(link, PowerDomainLinks.PowerDomainLink):  # type: ignore[attr-defined]
        raise TgiError("Invalid powerDomainLink handle", TgiFaultCode.INVALID_ID)
    from org.accellera.ipxact.v1685_2022.string_expression import StringExpression

    link.external_power_domain_reference = StringExpression(value=expression)  # type: ignore[assignment]
    return True

