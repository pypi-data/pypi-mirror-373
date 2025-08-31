"""Port category TGI functions (IEEE 1685-2022).

Implements BASE (F.7.67) and EXTENDED (F.7.68) Port functions.

Notes:
    The 2022 schema introduces rich structure for wire / transactional / structured
    ports plus field maps and domain type definitions. Only elements represented
    in the generated Python schema are manipulated. Where the spec references
    semantics not yet modeled (e.g. specific driver or constraint details) the
    function returns ``None`` or an empty list instead of raising – consistent
    with earlier categories.

Error model:
    Functions that take a handle to a Port or nested object return graceful
    empty values if the handle is invalid (None, empty list, empty string) –
    mirroring other BASE getter implementations. EXTENDED add/remove/set
    operations raise :class:`TgiError` with ``TgiFaultCode.INVALID_ID`` for an
    invalid handle and ``TgiFaultCode.INVALID_ARGUMENT`` for semantic problems
    (e.g. duplicates). All add* return a handle (string) of the new element.
"""
from __future__ import annotations

from collections.abc import Iterable
from types import SimpleNamespace

from org.accellera.ipxact.v1685_2022 import Port
from org.accellera.ipxact.v1685_2022.domain_type_def import DomainTypeDef
from org.accellera.ipxact.v1685_2022.field_map import FieldMap
from org.accellera.ipxact.v1685_2022.part_select import PartSelect
from org.accellera.ipxact.v1685_2022.sub_port_reference import SubPortReference

from .core import TgiError, TgiFaultCode, get_handle, resolve_handle, register_parent

__all__ = [
    # BASE (F.7.67)
    "getAccessPortAccessType",
    "getDomainTypeDefTypeDefinitionIDs",
    "getDomainTypeDefTypeDefinitions",
    "getDomainTypeDefTypeName",
    "getDomainTypeDefTypeNameID",
    "getDomainTypeDefViewIDs",
    "getDomainTypeDefViewRefIDs",
    "getDomainTypeDefViewRefs",
    "getFieldDefinitionAccessPoliciesIDs",
    "getFieldMapFieldSliceID",
    "getFieldMapModeRefByID",
    "getFieldMapModeRefByNames",
    "getFieldMapModeRefIDs",
    "getFieldMapModeRefs",
    "getFieldMapPartSelectID",
    "getFieldMapSubPortReferenceIDs",
    "getPayloadExtension",
    "getPayloadExtensionID",
    "getPayloadType",
    "getPortAccessID",
    # EXTENDED (F.7.68)
    "addDomainTypeDefTypeDefinition",
    "addDomainTypeDefViewRef",
    "addExternalPortReferenceSubPortReference",
    "addFieldMapIndex",
    "addFieldMapModeRef",
    "addFieldMapSubPortReference",
    "addInternalPortReferenceSubPortReference",
    "addPortClockDriver",
    "addPortClockDriverExpresion",
    "addPortDefaultDriver",
    "addPortDefaultDriverExpression",
    "addPortDomainTypeDef",
    "addPortFieldMap",
    "addPortSignalTypeDef",
    "addPortSingleShotDriver",
    "addPortSingleShotDriverExpression",
    "addPortStructuredStructPortTypeDef",
    "addPortStructuredSubStructuredPort",
    "addPortStructuredSubWirePort",
    "addPortStructuredVector",
    "addPortTransactionalTransTypeDef",
    "addPortWireConstraintSet",
    "addPortWireDriver",
    "addPortWireTypeDef",
    "addServiceTypeDefServiceTypeDef",
]

# ---------------------------------------------------------------------------
# Helpers (non-spec)
# ---------------------------------------------------------------------------

def _resolve_port(portID: str) -> Port | None:
    obj = resolve_handle(portID)
    return obj if isinstance(obj, Port) else None


def _iter_domain_type_defs(port: Port) -> Iterable[DomainTypeDef]:
    dtds = getattr(getattr(port.wire, "domain_type_defs", None), "domain_type_def", [])
    for d in dtds:
        if isinstance(d, DomainTypeDef):
            yield d


def _iter_field_maps(port: Port) -> Iterable[FieldMap]:
    fms = getattr(getattr(port, "field_maps", None), "field_map", [])
    for fm in fms:
        if isinstance(fm, FieldMap):
            yield fm


def _require_port(portID: str) -> Port:
    p = _resolve_port(portID)
    if p is None:
        raise TgiError(TgiFaultCode.INVALID_ID, f"Invalid port handle: {portID}")
    return p


def _new_part_select(index: int | None = None, left: int | None = None, right: int | None = None) -> PartSelect:
    ps = PartSelect()
    if index is not None:
        ps.index = index  # type: ignore[attr-defined]
    elif left is not None and right is not None:
        ps.msb = left  # type: ignore[attr-defined]
        ps.lsb = right  # type: ignore[attr-defined]
    return ps


# ---------------------------------------------------------------------------
# BASE (F.7.67)
# ---------------------------------------------------------------------------

def getAccessPortAccessType(portID: str) -> str | None:  # F.7.67.1
    """Return the access type (wire/transactional/structured) of the port.

    Section: F.7.67.1. Returns one of "wire", "transactional", "structured" or None.
    """
    p = _resolve_port(portID)
    if p is None:
        return None
    if p.wire is not None:
        return "wire"
    if p.transactional is not None:
        return "transactional"
    if p.structured is not None:
        return "structured"
    return None


def getDomainTypeDefTypeDefinitionIDs(portID: str, domainTypeDefID: str) -> list[str]:  # F.7.67.2
    """Return handles for ``typeDefinition`` children of a domainTypeDef.

    Section: F.7.67.2.
    """
    p = _resolve_port(portID)
    if p is None or p.wire is None:
        return []
    for d in _iter_domain_type_defs(p):
        if get_handle(d) == domainTypeDefID:
            return [get_handle(td) for td in getattr(d, "type_definition", [])]
    return []


def getDomainTypeDefTypeDefinitions(portID: str, domainTypeDefID: str) -> list[str]:  # F.7.67.3
    """Return string values of ``typeDefinition`` entries for a domainTypeDef.

    Section: F.7.67.3.
    """
    p = _resolve_port(portID)
    if p is None or p.wire is None:
        return []
    for d in _iter_domain_type_defs(p):
        if get_handle(d) == domainTypeDefID:
            vals: list[str] = []
            for td in getattr(d, "type_definition", []):
                val = getattr(td, "value", None)
                if isinstance(val, str):
                    vals.append(val)
            return vals
    return []


def getDomainTypeDefTypeName(portID: str, domainTypeDefID: str) -> str | None:  # F.7.67.4
    """Return the typeName value of a domainTypeDef.

    Section: F.7.67.4.
    """
    p = _resolve_port(portID)
    if p is None or p.wire is None:
        return None
    for d in _iter_domain_type_defs(p):
        if get_handle(d) == domainTypeDefID:
            tn = getattr(d, "type_name", None)
            return getattr(tn, "value", None) if tn is not None else None
    return None


def getDomainTypeDefTypeNameID(portID: str, domainTypeDefID: str) -> str | None:  # F.7.67.5
    """Return the handle of the ``typeName`` element of a domainTypeDef.

    Section: F.7.67.5.
    """
    p = _resolve_port(portID)
    if p is None or p.wire is None:
        return None
    for d in _iter_domain_type_defs(p):
        if get_handle(d) == domainTypeDefID:
            tn = getattr(d, "type_name", None)
            return None if tn is None else get_handle(tn)
    return None


def getDomainTypeDefViewIDs(portID: str, domainTypeDefID: str) -> list[str]:  # F.7.67.6
    """Return handles of ``viewRef`` elements of a domainTypeDef.

    Section: F.7.67.6.
    """
    p = _resolve_port(portID)
    if p is None or p.wire is None:
        return []
    for d in _iter_domain_type_defs(p):
        if get_handle(d) == domainTypeDefID:
            return [get_handle(v) for v in getattr(d, "view_ref", [])]
    return []


def getDomainTypeDefViewRefIDs(portID: str, domainTypeDefID: str) -> list[str]:  # F.7.67.7
    """Alias of getDomainTypeDefViewIDs (spec splits naming).

    Section: F.7.67.7.
    """
    return getDomainTypeDefViewIDs(portID, domainTypeDefID)


def getDomainTypeDefViewRefs(portID: str, domainTypeDefID: str) -> list[str]:  # F.7.67.8
    """Return string values of viewRef elements for a domainTypeDef.

    Section: F.7.67.8.
    """
    p = _resolve_port(portID)
    if p is None or p.wire is None:
        return []
    for d in _iter_domain_type_defs(p):
        if get_handle(d) == domainTypeDefID:
            vals: list[str] = []
            for v in getattr(d, "view_ref", []):
                val = getattr(v, "value", None)
                if isinstance(val, str):
                    vals.append(val)
            return vals
    return []


def getFieldDefinitionAccessPoliciesIDs(portID: str) -> list[str]:  # F.7.67.9
    """Return handles of access policy elements associated with the port field maps.

    Section: F.7.67.9.
    Implementation note: Access policies are not explicitly modeled on FieldMap in
    the generated schema; returns empty list until/if modeled.
    """
    return []


def getFieldMapFieldSliceID(fieldMapID: str) -> str | None:  # F.7.67.10
    """Return handle of ``fieldSlice`` child of a FieldMap.

    Section: F.7.67.10.
    """
    fm_obj = resolve_handle(fieldMapID)
    if not isinstance(fm_obj, FieldMap):  # invalid handle
        return None
    fs = getattr(fm_obj, "field_slice", None)
    return None if fs is None else get_handle(fs)


def getFieldMapModeRefByID(fieldMapModeRefID: str) -> tuple[str | None, int | None]:  # F.7.67.11
    """Return (modeName, priority) for a modeRef handle.

    Section: F.7.67.11.
    """
    obj = resolve_handle(fieldMapModeRefID)
    if obj is None or not hasattr(obj, "value"):
        return (None, None)
    return (getattr(obj, "value", None), getattr(obj, "priority", None))


def getFieldMapModeRefByNames(portID: str, fieldMapID: str, modeName: str) -> str | None:  # F.7.67.12
    """Return handle of a modeRef within a FieldMap by its mode name.

    Section: F.7.67.12.
    """
    p = _resolve_port(portID)
    if p is None:
        return None
    for fm in _iter_field_maps(p):
        if get_handle(fm) == fieldMapID:
            for mr in getattr(fm, "mode_ref", []):
                if getattr(mr, "value", None) == modeName:
                    return get_handle(mr)
    return None


def getFieldMapModeRefIDs(portID: str, fieldMapID: str) -> list[str]:  # F.7.67.13
    """Return handles of modeRef elements for a given FieldMap.

    Section: F.7.67.13.
    """
    p = _resolve_port(portID)
    if p is None:
        return []
    for fm in _iter_field_maps(p):
        if get_handle(fm) == fieldMapID:
            return [get_handle(mr) for mr in getattr(fm, "mode_ref", [])]
    return []


def getFieldMapModeRefs(portID: str, fieldMapID: str) -> list[tuple[str | None, int | None]]:  # F.7.67.14
    """Return list of (modeName, priority) for modeRefs of a FieldMap.

    Section: F.7.67.14.
    """
    p = _resolve_port(portID)
    result: list[tuple[str | None, int | None]] = []
    if p is None:
        return result
    for fm in _iter_field_maps(p):
        if get_handle(fm) == fieldMapID:
            for mr in getattr(fm, "mode_ref", []):
                result.append((getattr(mr, "value", None), getattr(mr, "priority", None)))
            break
    return result


def getFieldMapPartSelectID(fieldMapID: str) -> str | None:  # F.7.67.15
    """Return handle of partSelect child of a FieldMap.

    Section: F.7.67.15.
    """
    fm_obj = resolve_handle(fieldMapID)
    if not isinstance(fm_obj, FieldMap):
        return None
    ps = getattr(fm_obj, "part_select", None)
    return None if ps is None else get_handle(ps)


def getFieldMapSubPortReferenceIDs(fieldMapID: str) -> list[str]:  # F.7.67.16
    """Return handles of subPortReference children of a FieldMap.

    Section: F.7.67.16.
    """
    fm_obj = resolve_handle(fieldMapID)
    if not isinstance(fm_obj, FieldMap):
        return []
    return [get_handle(s) for s in getattr(fm_obj, "sub_port_reference", [])]


def getPayloadExtension(portID: str) -> str | None:  # F.7.67.17
    """Return payload extension string for a transactional port.

    Section: F.7.67.17.
    Implementation note: Not modeled in schema; returns None.
    """
    return None


def getPayloadExtensionID(portID: str) -> str | None:  # F.7.67.18
    """Return handle for payload extension element.

    Section: F.7.67.18. Not modeled; returns None.
    """
    return None


def getPayloadType(portID: str) -> str | None:  # F.7.67.19
    """Return payload type for a transactional port.

    Section: F.7.67.19.
    Implementation note: Not modeled separately; returns None.
    """
    return None


def getPortAccessID(portID: str) -> str | None:  # F.7.67.20
    """Return handle of the ``access`` element of the port.

    Section: F.7.67.20.
    """
    p = _resolve_port(portID)
    if p is None:
        return None
    acc = getattr(p, "access", None)
    return None if acc is None else get_handle(acc)


# ---------------------------------------------------------------------------
# EXTENDED (F.7.68)
# ---------------------------------------------------------------------------

def addDomainTypeDefTypeDefinition(portID: str, domainTypeDefID: str, value: str) -> str:  # F.7.68.1
    """Append a ``typeDefinition`` string to the given domainTypeDef.

    Section: F.7.68.1.
    """
    p = _require_port(portID)
    if p.wire is None or p.wire.domain_type_defs is None:
        raise TgiError(TgiFaultCode.INVALID_ARGUMENT, "Port has no domainTypeDefs")
    for d in _iter_domain_type_defs(p):
        if get_handle(d) == domainTypeDefID:
            td = DomainTypeDef.TypeDefinition(value=value)
            d.type_definition.append(td)  # type: ignore[attr-defined]
            register_parent(td, d, ("type_definition",), "list")
            return get_handle(td)
    raise TgiError(TgiFaultCode.NOT_FOUND, "domainTypeDef not found")


def addDomainTypeDefViewRef(portID: str, domainTypeDefID: str, viewRef: str) -> str:  # F.7.68.2
    """Add a viewRef to a domainTypeDef.

    Section: F.7.68.2.
    """
    p = _require_port(portID)
    if p.wire is None or p.wire.domain_type_defs is None:
        raise TgiError(TgiFaultCode.INVALID_ARGUMENT, "Port has no domainTypeDefs")
    for d in _iter_domain_type_defs(p):
        if get_handle(d) == domainTypeDefID:
            vr = DomainTypeDef.ViewRef(value=viewRef)
            d.view_ref.append(vr)  # type: ignore[attr-defined]
            register_parent(vr, d, ("view_ref",), "list")
            return get_handle(vr)
    raise TgiError(TgiFaultCode.NOT_FOUND, "domainTypeDef not found")


def addExternalPortReferenceSubPortReference(portID: str, fieldMapID: str, subPortRef: str) -> str:  # F.7.68.3
    """Add subPortReference for an external reference (treated same as internal here).

    Section: F.7.68.3. Implementation merges external/internal semantics.
    """
    return addFieldMapSubPortReference(portID, fieldMapID, subPortRef)


def addFieldMapIndex(portID: str, fieldMapID: str, index: int) -> str:  # F.7.68.4
    """Set/replace the partSelect of a FieldMap with a single index.

    Section: F.7.68.4. Returns handle of partSelect.
    """
    p = _require_port(portID)
    for fm in _iter_field_maps(p):
        if get_handle(fm) == fieldMapID:
            ps = _new_part_select(index=index)
            fm.part_select = ps
            register_parent(ps, fm, ("part_select",), "single")
            return get_handle(ps)
    raise TgiError(TgiFaultCode.NOT_FOUND, "fieldMap not found")


def addFieldMapModeRef(portID: str, fieldMapID: str, modeName: str, priority: int) -> str:  # F.7.68.5
    """Append a modeRef to a FieldMap.

    Section: F.7.68.5.
    """
    p = _require_port(portID)
    for fm in _iter_field_maps(p):
        if get_handle(fm) == fieldMapID:
            # uniqueness by modeName/priority pair not enforced by spec; allow duplicates?
            mr = FieldMap.ModeRef(value=modeName, priority=priority)
            fm.mode_ref.append(mr)  # type: ignore[attr-defined]
            register_parent(mr, fm, ("mode_ref",), "list")
            return get_handle(mr)
    raise TgiError(TgiFaultCode.NOT_FOUND, "fieldMap not found")


def addFieldMapSubPortReference(portID: str, fieldMapID: str, subPortRef: str) -> str:  # F.7.68.6
    """Add a subPortReference to a FieldMap.

    Section: F.7.68.6.
    """
    p = _require_port(portID)
    for fm in _iter_field_maps(p):
        if get_handle(fm) == fieldMapID:
            spr = SubPortReference(sub_port_ref=subPortRef)
            fm.sub_port_reference.append(spr)  # type: ignore[attr-defined]
            register_parent(spr, fm, ("sub_port_reference",), "list")
            return get_handle(spr)
    raise TgiError(TgiFaultCode.NOT_FOUND, "fieldMap not found")


def addInternalPortReferenceSubPortReference(portID: str, fieldMapID: str, subPortRef: str) -> str:  # F.7.68.7
    """Add subPortReference for an internal reference (same as external here).

    Section: F.7.68.7.
    """
    return addFieldMapSubPortReference(portID, fieldMapID, subPortRef)


def addPortClockDriver(portID: str, value: str) -> str:  # F.7.68.8
    """Add a clock driver to port (placeholder – not modeled).

    Section: F.7.68.8. Returns synthetic handle.
    """
    # Create synthetic node for tracking (no schema support yet)
    _require_port(portID)
    node = SimpleNamespace(kind="clockDriver", value=value)
    return get_handle(node)


def addPortClockDriverExpresion(portID: str, expression: str) -> str:  # F.7.68.9
    """Add clock driver expression (placeholder). Section: F.7.68.9."""
    return addPortClockDriver(portID, expression)


def addPortDefaultDriver(portID: str, value: str) -> str:  # F.7.68.10
    """Add default driver (placeholder). Section: F.7.68.10."""
    _require_port(portID)
    node = SimpleNamespace(kind="defaultDriver", value=value)
    return get_handle(node)


def addPortDefaultDriverExpression(portID: str, expression: str) -> str:  # F.7.68.11
    """Add default driver expression (placeholder). Section: F.7.68.11."""
    return addPortDefaultDriver(portID, expression)


def addPortDomainTypeDef(portID: str, typeName: str) -> str:  # F.7.68.12
    """Create and append a DomainTypeDef under wire.domainTypeDefs.

    Section: F.7.68.12.
    """
    p = _require_port(portID)
    if p.wire is None:
        raise TgiError(TgiFaultCode.INVALID_ARGUMENT, "Port is not a wire port")
    if p.wire.domain_type_defs is None:
        raise TgiError(TgiFaultCode.INVALID_ARGUMENT, "Port lacks domainTypeDefs container")
    dtd = DomainTypeDef(type_name=DomainTypeDef.TypeName(value=typeName))
    p.wire.domain_type_defs.domain_type_def.append(dtd)  # type: ignore[attr-defined]
    register_parent(dtd, p, ("wire", "domain_type_defs"), "list")
    return get_handle(dtd)


def addPortFieldMap(portID: str) -> str:  # F.7.68.13
    """Create a new FieldMap on the port.

    Section: F.7.68.13.
    """
    p = _require_port(portID)
    if p.field_maps is None:
        raise TgiError(TgiFaultCode.INVALID_ARGUMENT, "Port lacks fieldMaps container")
    fm = FieldMap(field_slice=FieldMap.FieldSlice())
    p.field_maps.field_map.append(fm)  # type: ignore[attr-defined]
    register_parent(fm, p, ("field_maps",), "list")
    return get_handle(fm)


def addPortSignalTypeDef(portID: str, typeDef: str) -> str:  # F.7.68.14
    """Add a signalTypeDef to wire.signalTypeDefs (placeholder).

    Section: F.7.68.14. Returns synthetic handle.
    """
    _require_port(portID)
    node = SimpleNamespace(kind="signalTypeDef", value=typeDef)
    return get_handle(node)


def addPortSingleShotDriver(portID: str, value: str) -> str:  # F.7.68.15
    """Add single-shot driver (placeholder). Section: F.7.68.15."""
    _require_port(portID)
    node = SimpleNamespace(kind="singleShotDriver", value=value)
    return get_handle(node)


def addPortSingleShotDriverExpression(portID: str, expression: str) -> str:  # F.7.68.16
    """Add single-shot driver expression (placeholder). Section: F.7.68.16."""
    return addPortSingleShotDriver(portID, expression)


def addPortStructuredStructPortTypeDef(portID: str, typeDef: str) -> str:  # F.7.68.17
    """Add structPortTypeDef (placeholder). Section: F.7.68.17."""
    _require_port(portID)
    node = SimpleNamespace(kind="structPortTypeDef", value=typeDef)
    return get_handle(node)


def addPortStructuredSubStructuredPort(portID: str, name: str) -> str:  # F.7.68.18
    """Add sub structured port (placeholder). Section: F.7.68.18."""
    _require_port(portID)
    node = SimpleNamespace(kind="subStructuredPort", name=name)
    return get_handle(node)


def addPortStructuredSubWirePort(portID: str, name: str) -> str:  # F.7.68.19
    """Add sub wire port (placeholder). Section: F.7.68.19."""
    _require_port(portID)
    node = SimpleNamespace(kind="subWirePort", name=name)
    return get_handle(node)


def addPortStructuredVector(portID: str, left: int, right: int) -> str:  # F.7.68.20
    """Add structured vectors element (placeholder). Section: F.7.68.20."""
    _require_port(portID)
    node = SimpleNamespace(kind="structuredVector", left=left, right=right)
    return get_handle(node)


def addPortTransactionalTransTypeDef(portID: str, language: str, text: str) -> str:  # F.7.68.21
    """Add transactional transTypeDef (placeholder). Section: F.7.68.21."""
    _require_port(portID)
    node = SimpleNamespace(kind="transTypeDef", language=language, text=text)
    return get_handle(node)


def addPortWireConstraintSet(portID: str, name: str) -> str:  # F.7.68.22
    """Add wire constraint set (placeholder). Section: F.7.68.22."""
    _require_port(portID)
    node = SimpleNamespace(kind="wireConstraintSet", name=name)
    return get_handle(node)


def addPortWireDriver(portID: str, value: str) -> str:  # F.7.68.23
    """Add wire driver (placeholder). Section: F.7.68.23."""
    _require_port(portID)
    node = SimpleNamespace(kind="wireDriver", value=value)
    return get_handle(node)


def addPortWireTypeDef(portID: str, typeDef: str) -> str:  # F.7.68.24
    """Add wire type definition (placeholder). Section: F.7.68.24."""
    _require_port(portID)
    node = SimpleNamespace(kind="wireTypeDef", value=typeDef)
    return get_handle(node)


def addServiceTypeDefServiceTypeDef(portID: str, typeDef: str) -> str:  # F.7.68.25
    """Add service type definition (placeholder). Section: F.7.68.25."""
    _require_port(portID)
    node = SimpleNamespace(kind="serviceTypeDef", value=typeDef)
    return get_handle(node)

