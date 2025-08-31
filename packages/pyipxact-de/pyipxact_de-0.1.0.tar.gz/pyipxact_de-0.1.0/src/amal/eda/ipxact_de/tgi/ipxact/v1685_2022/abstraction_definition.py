# ruff: noqa: I001
"""Abstraction definition category TGI functions.

Provides traversal of ports, parameters, choices and basic metadata getters
for :class:`AbstractionDefinition` objects.
"""
from .core import TgiError, TgiFaultCode, get_handle, resolve_handle, register_parent, detach_child_by_handle
from org.accellera.ipxact.v1685_2022 import AbstractionDefinition

__all__ = [
    # BASE (F.7.2)
    "getAbstractionDefBusTypeRefByVLNV",
    "getAbstractionDefChoiceIDs",
    "getAbstractionDefExtendsRefByVLNV",
    "getAbstractionDefPortIDs",
    "getAbstractionDefPortLogicalName",
    "getAbstractionDefPortMatch",
    "getAbstractionDefPortOnSystemIDs",
    "getAbstractionDefPortPacketIDs",
    "getAbstractionDefPortStyle",
    "getAbstractionDefPortTransactionalModeBusWidth",
    "getAbstractionDefPortTransactionalModeBusWidthExpression",
    "getAbstractionDefPortTransactionalModeBusWidthID",
    "getAbstractionDefPortTransactionalModeInitiative",
    "getAbstractionDefPortTransactionalModeKindID",
    "getAbstractionDefPortTransactionalModePresence",
    "getAbstractionDefPortTransactionalModeProtocolID",
    "getAbstractionDefPortTransactionalOnInitiatorID",
    "getAbstractionDefPortTransactionalOnSystemIDs",
    "getAbstractionDefPortTransactionalOnTargetID",
    "getAbstractionDefPortTransactionalQualifierID",
    "getAbstractionDefPortWireDefaultValue",
    "getAbstractionDefPortWireDefaultValueExpression",
    "getAbstractionDefPortWireDefaultValueID",
    "getAbstractionDefPortWireModeDirection",
    "getAbstractionDefPortWireModeMirroredModeConstraintsID",
    "getAbstractionDefPortWireModeModeConstraintsID",
    "getAbstractionDefPortWireModePresence",
    "getAbstractionDefPortWireModeWidth",
    "getAbstractionDefPortWireModeWidthExpression",
    "getAbstractionDefPortWireModeWidthID",
    "getAbstractionDefPortWireOnInitiatorID",
    "getAbstractionDefPortWireOnSystemIDs",
    "getAbstractionDefPortWireOnTargetID",
    "getAbstractionDefPortWireQualifierID",
    "getAbstractionDefPortWireRequiresDriver",
    "getAbstractionDefPortWireRequiresDriverID",
    "getModeConstraintsDriveConstraintCellSpecificationID",
    "getModeConstraintsLoadConstraintID",
    "getModeConstraintsTimingConstraintIDs",
    "getOnSystemGroup",
    "getPacketEndianness",
    "getPacketFieldEndianness",
    "getPacketFieldQualifierID",
    "getPacketFieldValue",
    "getPacketFieldValueExpression",
    "getPacketFieldWidth",
    "getPacketFieldWidthExpression",
    "getPacketFieldWidthID",
    "getPacketPacketFieldIDs",
    # EXTENDED (F.7.3)
    "addAbstractionDefChoice",
    "addAbstractionDefPort",
    "addAbstractionDefPortMode",
    "addAbstractionDefPortPacket",
    "addAbstractionDefPortTransactionalOnSystem",
    "addAbstractionDefPortWireOnSystem",
    "removeAbstractionDefChoice",
    "removeAbstractionDefPort",
    "removeAbstractionDefPortMode",
    "removeAbstractionDefPortTransactionalOnSystem",
    "removeAbstractionDefPortWireOnSystem",
    "setAbstractionDefExtends",
    "removeAbstractionDefPortTransactionalModeBusWidth",
    "removeAbstractionDefPortTransactionalModeInitiative",
    "removeAbstractionDefPortTransactionalModeKind",
    "removeAbstractionDefPortTransactionalModePresence",
    "removeAbstractionDefPortTransactionalModeProtocol",
    "removeAbstractionDefPortTransactionalOnInitiator",
    "removeAbstractionDefPortTransactionalOnTarget",
    "removeAbstractionDefPortTransactionalQualifier",
    "removeAbstractionDefPortWireModeDirection",
    "removeAbstractionDefPortWireModeMirroredModeConstraints",
    "removeAbstractionDefPortWireModeModeConstraints",
    "removeAbstractionDefPortWireModePresence",
    "removeAbstractionDefPortWireModeWidth",
    "removeAbstractionDefPortWireOnInitiator",
    "removeAbstractionDefPortWireOnTarget",
    "removeAbstractionDefPortWireQualifier",
    "removeAbstractionDefPortWireRequiresDriver",
    "setAbstractionDefPortTransactionalModeBusWidth",
    "setAbstractionDefPortTransactionalModeInitiative",
    "setAbstractionDefPortTransactionalModeKind",
    "setAbstractionDefPortTransactionalModePresence",
    "setAbstractionDefPortTransactionalModeProtocol",
    "setAbstractionDefPortTransactionalOnInitiator",
    "setAbstractionDefPortTransactionalOnTarget",
    "setAbstractionDefPortTransactionalQualifier",
    "setAbstractionDefPortTransactional",
    "setAbstractionDefPortWire",
    "setAbstractionDefPortWireDefaultValue",
    "setAbstractionDefPortWireModeDirection",
    "setAbstractionDefPortWireModeMirroredModeConstraints",
    "setAbstractionDefPortWireModeModeConstraints",
    "setAbstractionDefPortWireModePresence",
    "setAbstractionDefPortWireModeWidth",
    "setAbstractionDefPortWireOnInitiator",
    "setAbstractionDefPortWireOnTarget",
    "setAbstractionDefPortWireQualifier",
    "setAbstractionDefPortWireRequiresDriver",
]


def _resolve(abstractionDefinitionID: str) -> AbstractionDefinition | None:
    """Resolve a handle to an :class:`AbstractionDefinition` object.

    Helper (non-spec) used internally by TGI functions.

    Args:
        abstractionDefinitionID: Handle that should reference an abstractionDefinition.

    Returns:
        The resolved :class:`AbstractionDefinition` instance or ``None`` if the
        handle does not reference the expected type.
    """
    obj = resolve_handle(abstractionDefinitionID)
    return obj if isinstance(obj, AbstractionDefinition) else None


def _resolve_port(portID: str) -> AbstractionDefinition.Ports.Port | None:
    """Resolve a handle to an abstraction definition port element.

    Helper (non-spec) used internally.

    Args:
        portID: Handle referencing a logical port inside an abstractionDefinition.

    Returns:
        Port object or ``None`` if the handle is invalid or another type.
    """
    obj = resolve_handle(portID)
    if isinstance(obj, AbstractionDefinition.Ports.Port):  # type: ignore[attr-defined]
        return obj
    return None


def _ensure_transactional(portID: str):
    """Resolve and return the transactional sub-element for a port.

    Section: Annex F helper (not a spec TGI function).

    Args:
        portID: Handle of a transactional abstractionDefPort.

    Returns:
        The transactional object referenced by the port.

    Raises:
        TgiError: If the handle is invalid or the port is not transactional.
    """
    p = _resolve_port(portID)
    if p is None:
        raise TgiError("Invalid abstractionDefPort handle", TgiFaultCode.INVALID_ID)
    if p.transactional is None:
        raise TgiError("Port not transactional", TgiFaultCode.INVALID_ARGUMENT)
    return p.transactional


def _resolve_packet(packetID: str):  # type: ignore[return-type]
    """Resolve a handle to a packet element.

    Helper (non-spec) used internally by packet-related TGI functions.

    Args:
        packetID: Handle referencing a ``packet`` element of a packet style port.

    Returns:
        Resolved packet object or ``None`` if the handle does not reference a
        packet element.
    """
    obj = resolve_handle(packetID)
    from org.accellera.ipxact.v1685_2022.port_packet_type import PortPacketType
    return obj if isinstance(obj, PortPacketType) else None


def _resolve_packet_field(packetFieldID: str):  # type: ignore[return-type]
    """Resolve a handle to a packetField element.

    Helper (non-spec) used internally by packet-related TGI functions.

    Args:
        packetFieldID: Handle referencing a ``packetField`` element.

    Returns:
        Resolved packetField object or ``None`` if the handle is invalid or
        references another type.
    """
    obj = resolve_handle(packetFieldID)
    from org.accellera.ipxact.v1685_2022.port_packet_field_type import PortPacketFieldType
    return obj if isinstance(obj, PortPacketFieldType) else None

# ---------------------------------------------------------------------------
# BASE
# ---------------------------------------------------------------------------

def getAbstractionDefBusTypeRefByVLNV(
    abstractionDefinitionID: str,
) -> tuple[str | None, str | None, str | None, str | None]:
    """Return busType VLNV tuple.

    Section: F.7.2.1.

    Args:
        abstractionDefinitionID: Handle to an abstractionDefinition (or instance) element.

    Returns:
        Tuple ``(vendor, library, name, version)`` with each item possibly ``None``
        if the busType reference is absent.
    """
    ad = _resolve(abstractionDefinitionID)
    if ad is None:
        raise TgiError("Invalid abstraction definition handle", TgiFaultCode.INVALID_ID)
    bt = ad.bus_type
    if bt is None:
        return (None, None, None, None)
    return (bt.vendor, bt.library, bt.name, bt.version)


def getAbstractionDefChoiceIDs(abstractionDefinitionID: str) -> list[str]:
    """Return handles of all ``choice`` children.

    Section: F.7.2.2.

    Args:
        abstractionDefinitionID: Handle to an abstractionDefinition element.

    Returns:
        List of choice element handles (empty if none defined).
    """
    ad = _resolve(abstractionDefinitionID)
    if ad is None:
        raise TgiError("Invalid abstraction definition handle", TgiFaultCode.INVALID_ID)
    if ad.choices is None:
        return []
    return [get_handle(c) for c in getattr(ad.choices, "choice", [])]


def getAbstractionDefExtendsRefByVLNV(
    abstractionDefinitionID: str,
) -> tuple[str | None, str | None, str | None, str | None]:
    """Return the extends VLNV tuple.

    Section: F.7.2.3.

    Args:
        abstractionDefinitionID: Handle to an abstractionDefinition element.

    Returns:
        Tuple ``(vendor, library, name, version)`` or all ``None`` if no extends present.
    """
    ad = _resolve(abstractionDefinitionID)
    if ad is None:
        raise TgiError("Invalid abstraction definition handle", TgiFaultCode.INVALID_ID)
    ext = ad.extends
    if ext is None:
        return (None, None, None, None)
    return (ext.vendor, ext.library, ext.name, ext.version)


def getAbstractionDefPortIDs(abstractionDefinitionID: str) -> list[str]:
    """Return handles of all logical ports.

    Section: F.7.2.4.

    Args:
        abstractionDefinitionID: Handle to an abstractionDefinition element.

    Returns:
        List of port handles (empty if no ports defined).
    """
    ad = _resolve(abstractionDefinitionID)
    if ad is None:
        raise TgiError("Invalid abstraction definition handle", TgiFaultCode.INVALID_ID)
    if ad.ports is None:
        return []
    return [get_handle(p) for p in ad.ports.port]


def getAbstractionDefPortLogicalName(abstractionDefPortID: str) -> str | None:
    """Return the logicalName of a port.

    Section: F.7.2.5.

    Args:
        abstractionDefPortID: Handle to an abstractionDefPort element.

    Returns:
        Logical name string or ``None`` if not present.
    """
    p = _resolve_port(abstractionDefPortID)
    if p is None:
        raise TgiError("Invalid abstractionDefPort handle", TgiFaultCode.INVALID_ID)
    return p.logical_name


def getAbstractionDefPortMatch(abstractionDefPortID: str) -> bool | None:
    """Return the match flag of a port.

    Section: F.7.2.6.

    Args:
        abstractionDefPortID: Handle to an abstractionDefPort element.

    Returns:
        Boolean value or ``None`` if the element is absent.
    """
    p = _resolve_port(abstractionDefPortID)
    if p is None:
        raise TgiError("Invalid abstractionDefPort handle", TgiFaultCode.INVALID_ID)
    return p.match


def getAbstractionDefPortOnSystemIDs(abstractionDefPortID: str) -> list[str]:
    """Return handles of transactional onSystem elements.

    Section: F.7.2.7 (transactional port context).

    Args:
        abstractionDefPortID: Handle to an abstractionDefPort element.

    Returns:
        List of onSystem handles (empty if none or port not transactional).
    """
    p = _resolve_port(abstractionDefPortID)
    if p is None:
        raise TgiError("Invalid abstractionDefPort handle", TgiFaultCode.INVALID_ID)
    tr = getattr(p, "transactional", None)
    if tr is None:
        return []
    return [get_handle(os) for os in getattr(tr, "on_system", [])]


def getAbstractionDefPortPacketIDs(abstractionDefPortID: str) -> list[str]:
    """Return handles of packet elements under the port.

    Section: F.7.2.8.

    Args:
        abstractionDefPortID: Handle to an abstractionDefPort element.

    Returns:
        List of packet handles (empty if none or not a packet style port).
    """
    p = _resolve_port(abstractionDefPortID)
    if p is None:
        raise TgiError("Invalid abstractionDefPort handle", TgiFaultCode.INVALID_ID)
    pkts = p.packets
    if pkts is None:
        return []
    # Each packet is an element inside packets.packet
    return [get_handle(pkt) for pkt in getattr(pkts, "packet", [])]


def getAbstractionDefPortStyle(abstractionDefPortModeID: str) -> str | None:
    """Return the style of a port (wire, transactional, packet).

    Section: F.7.2.9.

    Args:
        abstractionDefPortModeID: Handle to an abstractionDefPort element.

    Returns:
        Style string or ``None`` if style cannot be determined.
    """
    p = _resolve_port(abstractionDefPortModeID)
    if p is None:
        raise TgiError("Invalid abstractionDefPort handle", TgiFaultCode.INVALID_ID)
    if p.transactional is not None:
        return "transactional"
    if p.wire is not None:
        return "wire"
    if p.packets is not None:
        return "packet"
    return None


def getAbstractionDefPortTransactionalModeBusWidth(abstractionDefPortModeID: str) -> int | None:
    """Return transactional busWidth resolved value.

    Section: F.7.2.10.

    Args:
        abstractionDefPortModeID: Handle to a transactional abstractionDefPort element.

    Returns:
        Integer width or ``None`` if not specified / not transactional.
    """
    p = _resolve_port(abstractionDefPortModeID)
    if p is None:
        raise TgiError("Invalid abstractionDefPort handle", TgiFaultCode.INVALID_ID)
    tr = getattr(p, "transactional", None)
    if tr is None:
        return None
    # On initiator/on target do not carry busWidth; onSystem entries may.
    for os in getattr(tr, "on_system", []):
        bw = getattr(os, "bus_width", None)
        if bw is not None and getattr(bw, "value", None) is not None:
            try:
                return int(bw.value)  # type: ignore[arg-type]
            except Exception:  # pragma: no cover
                return None
    return None


def getAbstractionDefPortTransactionalModeBusWidthExpression(abstractionDefPortModeID: str) -> str | None:
    """Return transactional busWidth expression.

    Section: F.7.2.11.

    Args:
        abstractionDefPortModeID: Handle to a transactional port element.

    Returns:
        Expression string or ``None`` if absent.
    """
    p = _resolve_port(abstractionDefPortModeID)
    if p is None:
        raise TgiError("Invalid abstractionDefPort handle", TgiFaultCode.INVALID_ID)
    tr = getattr(p, "transactional", None)
    if tr is None:
        return None
    for os in getattr(tr, "on_system", []):
        bw = getattr(os, "bus_width", None)
        if bw is not None:
            return getattr(bw, "value", None)
    return None


def getAbstractionDefPortTransactionalModeBusWidthID(abstractionDefPortModeID: str) -> str | None:
    """Return handle to busWidth element.

    Section: F.7.2.12.

    Args:
        abstractionDefPortModeID: Handle to a transactional port element.

    Returns:
        Handle string or ``None`` if not present.
    """
    p = _resolve_port(abstractionDefPortModeID)
    if p is None:
        raise TgiError("Invalid abstractionDefPort handle", TgiFaultCode.INVALID_ID)
    tr = getattr(p, "transactional", None)
    if tr is None:
        return None
    for os in getattr(tr, "on_system", []):
        bw = getattr(os, "bus_width", None)
        if bw is not None:
            return get_handle(bw)
    return None


def getAbstractionDefPortTransactionalModeInitiative(abstractionDefPortModeID: str) -> str | None:
    """Return initiative value across loci.

    Section: F.7.2.13.

    Args:
        abstractionDefPortModeID: Handle to a transactional port element.

    Returns:
        Initiative enumeration value or ``None``.
    """
    p = _resolve_port(abstractionDefPortModeID)
    if p is None:
        raise TgiError("Invalid abstractionDefPort handle", TgiFaultCode.INVALID_ID)
    tr = getattr(p, "transactional", None)
    if tr is None:
        return None
    init = getattr(tr.on_initiator, "initiative", None)
    if init is None:
        init = getattr(tr.on_target, "initiative", None)
    if init is None and getattr(tr, "on_system", None):
        for os in tr.on_system:
            init = getattr(os, "initiative", None)
            if init is not None:
                break
    return getattr(init, "value", None)


def getAbstractionDefPortTransactionalModeKindID(abstractionDefPortModeID: str) -> str | None:
    """Return handle to kind element.

    Section: F.7.2.14.

    Args:
        abstractionDefPortModeID: Handle to a transactional port element.

    Returns:
        Handle string or ``None`` if absent.
    """
    p = _resolve_port(abstractionDefPortModeID)
    if p is None:
        raise TgiError("Invalid abstractionDefPort handle", TgiFaultCode.INVALID_ID)
    tr = getattr(p, "transactional", None)
    if tr is None:
        return None
    for candidate in [getattr(tr.on_initiator, "kind", None), getattr(tr.on_target, "kind", None)]:
        if candidate is not None:
            return get_handle(candidate)
    for os in getattr(tr, "on_system", []):
        kind = getattr(os, "kind", None)
        if kind is not None:
            return get_handle(kind)
    return None


def getAbstractionDefPortTransactionalModePresence(abstractionDefPortModeID: str) -> str | None:
    """Return presence value.

    Section: F.7.2.15.

    Args:
        abstractionDefPortModeID: Handle to a transactional port element.

    Returns:
        Presence enumeration value or ``None``.
    """
    p = _resolve_port(abstractionDefPortModeID)
    if p is None:
        raise TgiError("Invalid abstractionDefPort handle", TgiFaultCode.INVALID_ID)
    tr = getattr(p, "transactional", None)
    if tr is None:
        return None
    for locus in [getattr(tr, "on_initiator", None), getattr(tr, "on_target", None)]:
        presence = getattr(locus, "presence", None)
        if presence is not None:
            return getattr(presence, "value", None)
    for os in getattr(tr, "on_system", []):
        presence = getattr(os, "presence", None)
        if presence is not None:
            return getattr(presence, "value", None)
    return None


def getAbstractionDefPortTransactionalModeProtocolID(abstractionDefPortModeID: str) -> str | None:
    """Return protocol handle.

    Section: F.7.2.16.

    Args:
        abstractionDefPortModeID: Handle to a transactional port element.

    Returns:
        Handle to protocol element or ``None``.
    """
    p = _resolve_port(abstractionDefPortModeID)
    if p is None:
        raise TgiError("Invalid abstractionDefPort handle", TgiFaultCode.INVALID_ID)
    tr = getattr(p, "transactional", None)
    if tr is None:
        return None
    for locus in [getattr(tr, "on_initiator", None), getattr(tr, "on_target", None)]:
        proto = getattr(locus, "protocol", None)
        if proto is not None:
            return get_handle(proto)
    for os in getattr(tr, "on_system", []):
        proto = getattr(os, "protocol", None)
        if proto is not None:
            return get_handle(proto)
    return None


def getAbstractionDefPortTransactionalOnInitiatorID(abstractionDefPortID: str) -> str | None:
    """Return transactional onInitiator handle.

    Section: F.7.2.17.

    Args:
        abstractionDefPortID: Handle to a transactional port element.

    Returns:
        Handle string or ``None`` if absent.
    """
    p = _resolve_port(abstractionDefPortID)
    if p is None:
        raise TgiError("Invalid abstractionDefPort handle", TgiFaultCode.INVALID_ID)
    tr = getattr(p, "transactional", None)
    if tr is None or tr.on_initiator is None:
        return None
    return get_handle(tr.on_initiator)


def getAbstractionDefPortTransactionalOnSystemIDs(abstractionDefPortID: str) -> list[str]:
    """Return transactional onSystem handles.

    Section: F.7.2.18.

    Args:
        abstractionDefPortID: Handle to a transactional port element.

    Returns:
        List of handles (may be empty).
    """
    return getAbstractionDefPortOnSystemIDs(abstractionDefPortID)


def getAbstractionDefPortTransactionalOnTargetID(abstractionDefPortID: str) -> str | None:
    """Return transactional onTarget handle.

    Section: F.7.2.19.

    Args:
        abstractionDefPortID: Handle to a transactional port element.

    Returns:
        Handle string or ``None``.
    """
    p = _resolve_port(abstractionDefPortID)
    if p is None:
        raise TgiError("Invalid abstractionDefPort handle", TgiFaultCode.INVALID_ID)
    tr = getattr(p, "transactional", None)
    if tr is None or tr.on_target is None:
        return None
    return get_handle(tr.on_target)


def getAbstractionDefPortTransactionalQualifierID(portID: str) -> str | None:
    """Return transactional qualifier handle.

    Section: F.7.2.20.

    Args:
        portID: Handle to a transactional port element.

    Returns:
        Handle string or ``None`` if absent.
    """
    p = _resolve_port(portID)
    if p is None:
        raise TgiError("Invalid abstractionDefPort handle", TgiFaultCode.INVALID_ID)
    tr = getattr(p, "transactional", None)
    if tr is None or tr.qualifier is None:
        return None
    return get_handle(tr.qualifier)


def getAbstractionDefPortWireDefaultValue(abstractionDefPortID: str) -> int | None:
    """Return wire defaultValue numeric value.

    Section: F.7.2.21.

    Args:
        abstractionDefPortID: Handle to a wire port element.

    Returns:
        Integer value or ``None`` if not present / not wire.
    """
    p = _resolve_port(abstractionDefPortID)
    if p is None:
        raise TgiError("Invalid abstractionDefPort handle", TgiFaultCode.INVALID_ID)
    w = getattr(p, "wire", None)
    dv = getattr(w, "default_value", None) if w is not None else None
    if dv is None:
        return None
    try:
        return int(getattr(dv, "value", None))  # type: ignore[arg-type]
    except Exception:  # pragma: no cover
        return None


def getAbstractionDefPortWireDefaultValueExpression(abstractionDefPortID: str) -> str | None:
    """Return wire defaultValue expression.

    Section: F.7.2.22.

    Args:
        abstractionDefPortID: Handle to a wire port element.

    Returns:
        Expression string or ``None``.
    """
    p = _resolve_port(abstractionDefPortID)
    if p is None:
        raise TgiError("Invalid abstractionDefPort handle", TgiFaultCode.INVALID_ID)
    w = getattr(p, "wire", None)
    dv = getattr(w, "default_value", None) if w is not None else None
    return getattr(dv, "value", None) if dv is not None else None


def getAbstractionDefPortWireDefaultValueID(abstractionDefPortModeID: str) -> str | None:
    """Return handle to wire defaultValue element.

    Section: F.7.2.23.

    Args:
        abstractionDefPortModeID: Handle to a wire port element.

    Returns:
        Handle string or ``None`` if absent.
    """
    p = _resolve_port(abstractionDefPortModeID)
    if p is None:
        raise TgiError("Invalid abstractionDefPort handle", TgiFaultCode.INVALID_ID)
    w = getattr(p, "wire", None)
    if w is None:
        return None
    dv = getattr(w, "default_value", None)
    return get_handle(dv) if dv is not None else None


def getAbstractionDefPortWireModeDirection(abstractionDefPortModeID: str) -> str | None:
    """Return wire direction.

    Section: F.7.2.24.

    Args:
        abstractionDefPortModeID: Handle to a wire port element.

    Returns:
        Direction enumeration or ``None``.
    """
    p = _resolve_port(abstractionDefPortModeID)
    if p is None:
        raise TgiError("Invalid abstractionDefPort handle", TgiFaultCode.INVALID_ID)
    w = getattr(p, "wire", None)
    return getattr(getattr(w, "direction", None), "value", None) if w is not None else None


def getAbstractionDefPortWireModeMirroredModeConstraintsID(abstractionDefPortModeID: str) -> str | None:
    """Return handle to mirroredModeConstraints.

    Section: F.7.2.25.

    Args:
        abstractionDefPortModeID: Handle to a wire port element.

    Returns:
        Handle string or ``None`` if absent.
    """
    p = _resolve_port(abstractionDefPortModeID)
    if p is None:
        raise TgiError("Invalid abstractionDefPort handle", TgiFaultCode.INVALID_ID)
    w = getattr(p, "wire", None)
    mmc = getattr(w, "mirrored_mode_constraints", None) if w is not None else None
    return get_handle(mmc) if mmc is not None else None


def getAbstractionDefPortWireModeModeConstraintsID(abstractionDefPortModeID: str) -> str | None:
    """Return handle to modeConstraints.

    Section: F.7.2.26.

    Args:
        abstractionDefPortModeID: Handle to a wire port element.

    Returns:
        Handle string or ``None`` if not present.
    """
    p = _resolve_port(abstractionDefPortModeID)
    if p is None:
        raise TgiError("Invalid abstractionDefPort handle", TgiFaultCode.INVALID_ID)
    w = getattr(p, "wire", None)
    mc = getattr(w, "mode_constraints", None) if w is not None else None
    return get_handle(mc) if mc is not None else None


def getAbstractionDefPortWireModePresence(abstractionDefPortModeID: str) -> str | None:
    """Return wire presence enumeration.

    Section: F.7.2.27.

    Args:
        abstractionDefPortModeID: Handle to a wire port element.

    Returns:
        Presence value string or ``None``.
    """
    p = _resolve_port(abstractionDefPortModeID)
    if p is None:
        raise TgiError("Invalid abstractionDefPort handle", TgiFaultCode.INVALID_ID)
    w = getattr(p, "wire", None)
    presence = getattr(w, "presence", None) if w is not None else None
    return getattr(presence, "value", None) if presence is not None else None


def getAbstractionDefPortWireModeWidth(abstractionDefPortModeID: str) -> int | None:
    """Return wire width numeric value.

    Section: F.7.2.28.

    Args:
        abstractionDefPortModeID: Handle to a wire port element.

    Returns:
        Integer width or ``None``.
    """
    p = _resolve_port(abstractionDefPortModeID)
    if p is None:
        raise TgiError("Invalid abstractionDefPort handle", TgiFaultCode.INVALID_ID)
    w = getattr(p, "wire", None)
    width = getattr(w, "width", None) if w is not None else None
    if width is None:
        return None
    try:
        return int(getattr(width, "value", None))  # type: ignore[arg-type]
    except Exception:  # pragma: no cover
        return None


def getAbstractionDefPortWireModeWidthExpression(abstractionDefPortModeID: str) -> str | None:
    """Return wire width expression.

    Section: F.7.2.29.

    Args:
        abstractionDefPortModeID: Handle to a wire port element.

    Returns:
        Expression string or ``None``.
    """
    p = _resolve_port(abstractionDefPortModeID)
    if p is None:
        raise TgiError("Invalid abstractionDefPort handle", TgiFaultCode.INVALID_ID)
    w = getattr(p, "wire", None)
    width = getattr(w, "width", None) if w is not None else None
    return getattr(width, "value", None) if width is not None else None


def getAbstractionDefPortWireModeWidthID(abstractionDefPortModeID: str) -> str | None:
    """Return handle of wire width element.

    Section: F.7.2.30.

    Args:
        abstractionDefPortModeID: Handle to a wire port element.

    Returns:
        Handle string or ``None`` if absent.
    """
    p = _resolve_port(abstractionDefPortModeID)
    if p is None:
        raise TgiError("Invalid abstractionDefPort handle", TgiFaultCode.INVALID_ID)
    w = getattr(p, "wire", None)
    width = getattr(w, "width", None) if w is not None else None
    return get_handle(width) if width is not None else None


def getAbstractionDefPortWireOnInitiatorID(abstractionDefPortID: str) -> str | None:
    """F.7.2.31 Return handle to the wire onInitiator element.

    Args:
        abstractionDefPortID: Handle to a logical wire port element.

    Returns:
        Handle to the onInitiator element or None if absent / not wire style.
    """
    p = _resolve_port(abstractionDefPortID)
    if p is None:
        raise TgiError("Invalid abstractionDefPort handle", TgiFaultCode.INVALID_ID)
    w = getattr(p, "wire", None)
    if w is None or getattr(w, "on_initiator", None) is None:
        return None
    return get_handle(w.on_initiator)


def getAbstractionDefPortWireOnSystemIDs(portID: str) -> list[str]:
    """F.7.2.32 Return handles to all wire onSystem elements.

    Args:
        portID: Handle to a logical wire port element.

    Returns:
        List of onSystem element handles (may be empty).
    """
    p = _resolve_port(portID)
    if p is None:
        raise TgiError("Invalid abstractionDefPort handle", TgiFaultCode.INVALID_ID)
    w = getattr(p, "wire", None)
    if w is None:
        return []
    return [get_handle(os) for os in getattr(w, "on_system", [])]


def getAbstractionDefPortWireOnTargetID(abstractionDefPortID: str) -> str | None:
    """F.7.2.33 Return handle to the wire onTarget element.

    Args:
        abstractionDefPortID: Handle to a logical wire port element.

    Returns:
        Handle to onTarget element or None if absent / not wire style.
    """
    p = _resolve_port(abstractionDefPortID)
    if p is None:
        raise TgiError("Invalid abstractionDefPort handle", TgiFaultCode.INVALID_ID)
    w = getattr(p, "wire", None)
    if w is None or getattr(w, "on_target", None) is None:
        return None
    return get_handle(w.on_target)


def getAbstractionDefPortWireQualifierID(portID: str) -> str | None:
    """F.7.2.34 Return handle to wire qualifier element.

    Args:
        portID: Handle to a logical wire port element.

    Returns:
        Qualifier element handle or None if absent.
    """
    p = _resolve_port(portID)
    if p is None:
        raise TgiError("Invalid abstractionDefPort handle", TgiFaultCode.INVALID_ID)
    w = getattr(p, "wire", None)
    if w is None or getattr(w, "qualifier", None) is None:
        return None
    return get_handle(w.qualifier)


def getAbstractionDefPortWireRequiresDriver(abstractionDefPortID: str) -> bool | None:
    """Return wire requiresDriver boolean value.

    Section: F.7.2.35.

    Args:
        abstractionDefPortID: Handle to a wire style abstractionDefPort element.

    Returns:
        Boolean value if the ``requiresDriver`` element is present, otherwise
        ``None`` if absent or the port is not wire style.
    """
    p = _resolve_port(abstractionDefPortID)
    if p is None:
        raise TgiError("Invalid abstractionDefPort handle", TgiFaultCode.INVALID_ID)
    w = getattr(p, "wire", None)
    if w is None:
        return None
    req = getattr(w, "requires_driver", None)
    return bool(getattr(req, "value", False)) if req is not None else None


def getAbstractionDefPortWireRequiresDriverID(abstractionDefPortModeID: str) -> str | None:
    """Return handle of wire requiresDriver element.

    Section: F.7.2.36.

    Args:
        abstractionDefPortModeID: Handle to a wire style abstractionDefPort element.

    Returns:
        Handle string if the ``requiresDriver`` element exists, otherwise
        ``None`` if absent or not a wire style port.
    """
    p = _resolve_port(abstractionDefPortModeID)
    if p is None:
        raise TgiError("Invalid abstractionDefPort handle", TgiFaultCode.INVALID_ID)
    w = getattr(p, "wire", None)
    if w is None:
        return None
    req = getattr(w, "requires_driver", None)
    return get_handle(req) if req is not None else None


# ---------------------------------------------------------------------------
# Additional BASE getters not previously implemented (constraints, packets)
# ---------------------------------------------------------------------------

def getModeConstraintsDriveConstraintCellSpecificationID(modeConstraintsID: str) -> str | None:
    """Return handle to driveConstraint/cellSpecification.

    Section: F.7.2.37.

    Args:
        modeConstraintsID: Handle to a modeConstraints element.

    Returns:
        Handle to first cellSpecification element or ``None``.
    """
    obj = resolve_handle(modeConstraintsID)
    from org.accellera.ipxact.v1685_2022.abstraction_def_port_constraints_type import (
        AbstractionDefPortConstraintsType,
    )
    if not isinstance(obj, AbstractionDefPortConstraintsType):  # type: ignore[arg-type]
        raise TgiError("Invalid modeConstraints handle", TgiFaultCode.INVALID_ID)
    for dc in getattr(obj, "drive_constraint", []):  # type: ignore[attr-defined]
        cs = getattr(dc, "cell_specification", None)
        if cs is not None:
            return get_handle(cs)
    return None


def getModeConstraintsLoadConstraintID(modeConstraintsID: str) -> str | None:
    """Return handle to loadConstraint.

    Section: F.7.2.38.

    Args:
        modeConstraintsID: Handle to a modeConstraints element.

    Returns:
        Handle string or ``None`` if absent.
    """
    obj = resolve_handle(modeConstraintsID)
    from org.accellera.ipxact.v1685_2022.abstraction_def_port_constraints_type import (
        AbstractionDefPortConstraintsType,
    )
    if not isinstance(obj, AbstractionDefPortConstraintsType):  # type: ignore[arg-type]
        raise TgiError("Invalid modeConstraints handle", TgiFaultCode.INVALID_ID)
    for lc in getattr(obj, "load_constraint", []):  # type: ignore[attr-defined]
        return get_handle(lc)
    return None


def getModeConstraintsTimingConstraintIDs(modeConstraintsID: str) -> list[str]:
    """Return timingConstraint handles.

    Section: F.7.2.39.

    Args:
        modeConstraintsID: Handle to a modeConstraints element.

    Returns:
        List of timingConstraint handles (possibly empty).
    """
    obj = resolve_handle(modeConstraintsID)
    from org.accellera.ipxact.v1685_2022.abstraction_def_port_constraints_type import (
        AbstractionDefPortConstraintsType,
    )
    if not isinstance(obj, AbstractionDefPortConstraintsType):  # type: ignore[arg-type]
        raise TgiError("Invalid modeConstraints handle", TgiFaultCode.INVALID_ID)
    return [get_handle(tc) for tc in getattr(obj, "timing_constraint", [])]  # type: ignore[attr-defined]


def getOnSystemGroup(onSystemID: str) -> str | None:
    """Return onSystem group attribute.

    Section: F.7.2.40.

    Args:
        onSystemID: Handle to an onSystem element (transactional or wire).

    Returns:
        Group name string or ``None``.
    """
    obj = resolve_handle(onSystemID)
    # onSystem may originate from transactional or wire variants; both expose 'group'
    return getattr(obj, "group", None)


def getPacketEndianness(packetID: str) -> str | None:
    """Return packet endianness.

    Section: F.7.2.41.

    Args:
        packetID: Handle to a packet element.

    Returns:
        Endianness string (big/little) or ``None``.
    """
    pkt = _resolve_packet(packetID)
    if pkt is None:
        raise TgiError("Invalid packet handle", TgiFaultCode.INVALID_ID)
    end = getattr(pkt, "endianness", None)
    return getattr(end, "value", None) if end is not None else None


def getPacketFieldEndianness(packetFieldID: str) -> str | None:
    """Return packetField endianness.

    Section: F.7.2.42.

    Args:
        packetFieldID: Handle to a packetField element.

    Returns:
        Endianness string or ``None``.
    """
    pf = _resolve_packet_field(packetFieldID)
    if pf is None:
        raise TgiError("Invalid packetField handle", TgiFaultCode.INVALID_ID)
    end = getattr(pf, "endianness", None)
    return getattr(end, "value", None) if end is not None else None


def getPacketFieldQualifierID(packetFieldID: str) -> str | None:
    """Return handle of packetField qualifier.

    Section: F.7.2.43.

    Args:
        packetFieldID: Handle to a packetField element.

    Returns:
        Qualifier handle string or ``None``.
    """
    pf = _resolve_packet_field(packetFieldID)
    if pf is None:
        raise TgiError("Invalid packetField handle", TgiFaultCode.INVALID_ID)
    qual = getattr(pf, "qualifier", None)
    return get_handle(qual) if qual is not None else None


def getPacketFieldValue(packetFieldID: str) -> int | None:
    """Return numeric packetField value.

    Section: F.7.2.44.

    Args:
        packetFieldID: Handle to a packetField element.

    Returns:
        Integer value or ``None``.
    """
    pf = _resolve_packet_field(packetFieldID)
    if pf is None:
        raise TgiError("Invalid packetField handle", TgiFaultCode.INVALID_ID)
    val = getattr(pf, "value", None)
    if val is None:
        return None
    try:
        return int(getattr(val, "value", None))  # type: ignore[arg-type]
    except Exception:  # pragma: no cover
        return None


def getPacketFieldValueExpression(packetFieldID: str) -> str | None:
    """Return packetField value expression.

    Section: F.7.2.45.

    Args:
        packetFieldID: Handle to a packetField element.

    Returns:
        Expression string or ``None``.
    """
    pf = _resolve_packet_field(packetFieldID)
    if pf is None:
        raise TgiError("Invalid packetField handle", TgiFaultCode.INVALID_ID)
    val = getattr(pf, "value", None)
    return getattr(val, "value", None) if val is not None else None


def getPacketFieldWidth(packetFieldID: str) -> int | None:
    """Return packetField width numeric value.

    Section: F.7.2.47.

    Args:
        packetFieldID: Handle to a packetField element.

    Returns:
        Integer width or ``None``.
    """
    pf = _resolve_packet_field(packetFieldID)
    if pf is None:
        raise TgiError("Invalid packetField handle", TgiFaultCode.INVALID_ID)
    width = getattr(pf, "width", None)
    if width is None:
        return None
    try:
        return int(getattr(width, "value", None))  # type: ignore[arg-type]
    except Exception:  # pragma: no cover
        return None


def getPacketFieldWidthExpression(packetFieldID: str) -> str | None:
    """Return packetField width expression.

    Section: F.7.2.48.

    Args:
        packetFieldID: Handle to a packetField element.

    Returns:
        Expression string or ``None``.
    """
    pf = _resolve_packet_field(packetFieldID)
    if pf is None:
        raise TgiError("Invalid packetField handle", TgiFaultCode.INVALID_ID)
    width = getattr(pf, "width", None)
    return getattr(width, "value", None) if width is not None else None


def getPacketFieldWidthID(packetFieldID: str) -> str | None:
    """Return handle of packetField width element.

    Section: F.7.2.49.

    Args:
        packetFieldID: Handle to a packetField element.

    Returns:
        Width handle string or ``None``.
    """
    pf = _resolve_packet_field(packetFieldID)
    if pf is None:
        raise TgiError("Invalid packetField handle", TgiFaultCode.INVALID_ID)
    width = getattr(pf, "width", None)
    return get_handle(width) if width is not None else None


def getPacketPacketFieldIDs(packetID: str) -> list[str]:
    """Return packetField child handles of a packet.

    Section: F.7.2.50.

    Args:
        packetID: Handle to a packet element.

    Returns:
        List of packetField handles (possibly empty).
    """
    pkt = _resolve_packet(packetID)
    if pkt is None:
        raise TgiError("Invalid packet handle", TgiFaultCode.INVALID_ID)
    pf_container = getattr(pkt, "packet_fields", None)
    if pf_container is None:
        return []
    return [get_handle(pf) for pf in getattr(pf_container, "packet_field", [])]


# ---------------------------------------------------------------------------
# EXTENDED
# ---------------------------------------------------------------------------

def addAbstractionDefChoice(abstractionDefinitionID: str, name: str) -> str:  # pragma: no cover - scaffold
    """Add a ``choice`` element.

    Section: F.7.3.1.

    A minimal enumeration entry is created automatically using ``name`` as the
    enumeration value to satisfy schema requirements.

    Args:
        abstractionDefinitionID: Handle of the parent abstractionDefinition.
        name: Choice name.

    Returns:
        Handle of the created ``choice`` element.

    Raises:
        TgiError: If the abstractionDefinition handle is invalid.
    """
    ad = _resolve(abstractionDefinitionID)
    if ad is None:
        raise TgiError("Invalid abstraction definition handle", TgiFaultCode.INVALID_ID)
    from org.accellera.ipxact.v1685_2022.choices import Choices  # local import

    if ad.choices is None:
        ad.choices = Choices(choice=[])  # type: ignore[arg-type]
    # Build required enumeration element
    enum = Choices.Choice.Enumeration(value=name)
    ch = Choices.Choice(name=name, enumeration=[enum])  # type: ignore[arg-type]
    ad.choices.choice.append(ch)  # type: ignore[attr-defined]
    register_parent(ch, ad.choices, ("choice",), "list")
    return get_handle(ch)


def addAbstractionDefPort(
    abstractionDefinitionID: str, logicalName: str, type: str
) -> str:  # pragma: no cover - scaffold
    """Add an abstractionDefPort.

    Section: F.7.3.2.

    Creates a new ``port`` with the requested style. Supported ``type`` values:
    ``wire``, ``transactional`` and ``packet``. For ``packet`` an empty
    packets container is created; packet content must be added separately via
    :func:`addAbstractionDefPortPacket`.

    Args:
        abstractionDefinitionID: Parent abstractionDefinition handle.
        logicalName: Logical port name.
        type: Port style ('wire', 'transactional', 'packet').

    Returns:
        Handle of the created port.

    Raises:
        TgiError: If the abstractionDefinition handle is invalid or the type is unsupported.
    """
    ad = _resolve(abstractionDefinitionID)
    if ad is None:
        raise TgiError("Invalid abstraction definition handle", TgiFaultCode.INVALID_ID)
    if ad.ports is None:
        # Required container
        ad.ports = AbstractionDefinition.Ports(port=[])  # type: ignore[arg-type]
    style = type.lower()
    from org.accellera.ipxact.v1685_2022.wire import Wire  # local import
    if style == "wire":
        port = AbstractionDefinition.Ports.Port(logical_name=logicalName, wire=Wire())
    elif style == "transactional":
        port = AbstractionDefinition.Ports.Port(
            logical_name=logicalName,
            transactional=AbstractionDefinition.Ports.Port.Transactional(),
        )
    elif style == "packet":
        from org.accellera.ipxact.v1685_2022.packets import Packets

        port = AbstractionDefinition.Ports.Port(
            logical_name=logicalName,
            packets=Packets(packet=[]),  # type: ignore[arg-type]
        )
    else:  # unsupported
        raise TgiError("Unsupported port type", TgiFaultCode.INVALID_ARGUMENT)
    ad.ports.port.append(port)  # type: ignore[attr-defined]
    register_parent(port, ad.ports, ("port",), "list")
    return get_handle(port)


def addAbstractionDefPortMode(abstractionDefPortID: str, mode: str) -> str:  # pragma: no cover - scaffold
    """Add a mode (initiator/target) to a port.

    Section: F.7.3.3.

    This helper creates ``onInitiator`` or ``onTarget`` entries for wire and
    transactional styles. System entries use dedicated onSystem add
    functions.

    Args:
        abstractionDefPortID: Port handle.
        mode: 'initiator' or 'target'.

    Returns:
        Handle of the created element (existing one reused if already present).

    Raises:
        TgiError: If the port handle is invalid or mode unsupported.
    """
    p = _resolve_port(abstractionDefPortID)
    if p is None:
        raise TgiError("Invalid abstractionDefPort handle", TgiFaultCode.INVALID_ID)
    m = mode.lower()
    if m not in {"initiator", "target"}:
        raise TgiError("Unsupported mode (use initiator/target)", TgiFaultCode.INVALID_ARGUMENT)
    # Determine style
    if p.transactional is not None:
        tr = p.transactional
        if m == "initiator":
            if tr.on_initiator is not None:
                return get_handle(tr.on_initiator)
            tr.on_initiator = AbstractionDefinition.Ports.Port.Transactional.OnInitiator()  # type: ignore[attr-defined]
            return get_handle(tr.on_initiator)
        if tr.on_target is not None:
            return get_handle(tr.on_target)
        tr.on_target = AbstractionDefinition.Ports.Port.Transactional.OnTarget()  # type: ignore[attr-defined]
        return get_handle(tr.on_target)
    if p.wire is not None:
        w = p.wire
        from org.accellera.ipxact.v1685_2022.wire import Wire as WireClass

        if isinstance(w, WireClass):
            if m == "initiator":
                if w.on_initiator is not None:
                    return get_handle(w.on_initiator)
                w.on_initiator = WireClass.OnInitiator()  # type: ignore[attr-defined]
                return get_handle(w.on_initiator)
            if w.on_target is not None:
                return get_handle(w.on_target)
            w.on_target = WireClass.OnTarget()  # type: ignore[attr-defined]
            return get_handle(w.on_target)
    raise TgiError("Port has neither transactional nor wire style", TgiFaultCode.INVALID_ARGUMENT)


def addAbstractionDefPortPacket(
    absDefPortID: str,
    packetName: str,
    packetFieldName: str,
    packetFieldWidth: str,
) -> str:  # pragma: no cover - scaffold
    """Add a port packet with one field.

    Section: F.7.3.4.

    Creates (if necessary) the packets container and adds a new packet with a
    single field.

    Args:
        absDefPortID: Port handle.
        packetName: Packet name.
        packetFieldName: Field name.
        packetFieldWidth: Width expression string.

    Returns:
        Handle of the created packet element.

    Raises:
        TgiError: If the port handle is invalid.
    """
    p = _resolve_port(absDefPortID)
    if p is None:
        raise TgiError("Invalid abstractionDefPort handle", TgiFaultCode.INVALID_ID)
    from org.accellera.ipxact.v1685_2022.packets import Packets
    from org.accellera.ipxact.v1685_2022.port_packet_field_type import PortPacketFieldType
    from org.accellera.ipxact.v1685_2022.port_packet_fields_type import (
        PortPacketFieldsType,
    )
    from org.accellera.ipxact.v1685_2022.port_packet_type import PortPacketType
    from org.accellera.ipxact.v1685_2022.unresolved_unsigned_positive_int_expression import (
        UnresolvedUnsignedPositiveIntExpression,
    )

    if p.packets is None:
        p.packets = Packets(packet=[])  # type: ignore[arg-type]
    field = PortPacketFieldType(
        name=packetFieldName,
        width=UnresolvedUnsignedPositiveIntExpression(value=packetFieldWidth),  # type: ignore[arg-type]
    )
    packet = PortPacketType(
        name=packetName,
        packet_fields=PortPacketFieldsType(packet_field=[field]),  # type: ignore[arg-type]
    )
    p.packets.packet.append(packet)  # type: ignore[attr-defined]
    register_parent(packet, p.packets, ("packet",), "list")
    # Register field relationship
    if packet.packet_fields is not None:  # type: ignore[truthy-bool]
        register_parent(field, packet.packet_fields, ("packet_field",), "list")
    return get_handle(packet)


def addAbstractionDefPortTransactionalOnSystem(portID: str, group: str) -> str:  # pragma: no cover - scaffold
    """Add a transactional onSystem element.

    Section: F.7.3.5.

    Args:
        portID: Transactional port handle.
        group: Group name.

    Returns:
        Handle of the created onSystem element.

    Raises:
        TgiError: If the port is invalid or not transactional.
    """
    p = _resolve_port(portID)
    if p is None:
        raise TgiError("Invalid abstractionDefPort handle", TgiFaultCode.INVALID_ID)
    if p.transactional is None:
        raise TgiError("Port is not transactional", TgiFaultCode.INVALID_ARGUMENT)
    os = AbstractionDefinition.Ports.Port.Transactional.OnSystem(group=group)
    p.transactional.on_system.append(os)  # type: ignore[attr-defined]
    register_parent(os, p.transactional, ("on_system",), "list")
    return get_handle(os)


def addAbstractionDefPortWireOnSystem(portID: str, group: str) -> str:  # pragma: no cover - scaffold
    """Add a wire onSystem element.

    Section: F.7.3.6.

    Args:
        portID: Wire port handle.
        group: Group name.

    Returns:
        Handle of the created onSystem element.

    Raises:
        TgiError: If the port is invalid or not wire style.
    """
    p = _resolve_port(portID)
    if p is None:
        raise TgiError("Invalid abstractionDefPort handle", TgiFaultCode.INVALID_ID)
    if p.wire is None:
        raise TgiError("Port is not wire style", TgiFaultCode.INVALID_ARGUMENT)
    from org.accellera.ipxact.v1685_2022.wire import Wire as WireClass

    os = WireClass.OnSystem(group=group)
    p.wire.on_system.append(os)  # type: ignore[attr-defined]
    register_parent(os, p.wire, ("on_system",), "list")
    return get_handle(os)


def removeAbstractionDefChoice(choiceID: str) -> bool:  # pragma: no cover - scaffold
    """Remove a choice element.

    Section: F.7.3.9.

    Args:
        choiceID: Choice handle.

    Returns:
        True if removed, False otherwise.
    """
    target = resolve_handle(choiceID)
    if target is None:
        return False
    return detach_child_by_handle(choiceID)


def removeAbstractionDefPort(portID: str) -> bool:  # pragma: no cover - scaffold
    """Remove a port.

    Section: F.7.3.11.

    Args:
        portID: Port handle.

    Returns:
        True if removed, False otherwise.
    """
    target = _resolve_port(portID)
    if target is None:
        return False
    return detach_child_by_handle(portID)


def removeAbstractionDefPortMode(portModeID: str) -> bool:  # pragma: no cover - scaffold
    """Remove a port mode element.

    Section: F.7.3.13.

    Args:
        portModeID: Handle of onInitiator/onTarget/onSystem element.

    Returns:
        True if removed, False otherwise.
    """
    obj = resolve_handle(portModeID)
    if obj is None:
        return False
    return detach_child_by_handle(portModeID)


def removeAbstractionDefPortTransactionalOnSystem(onSystemID: str) -> bool:  # pragma: no cover - scaffold
    """Remove a transactional onSystem element.

    Section: F.7.3.20.

    Args:
        onSystemID: onSystem handle.

    Returns:
        True if removed, False otherwise.
    """
    obj = resolve_handle(onSystemID)
    if obj is None:
        return False
    return detach_child_by_handle(onSystemID)


def removeAbstractionDefPortWireOnSystem(onSystemID: str) -> bool:  # pragma: no cover - scaffold
    """Remove a wire onSystem element.

    Section: F.7.3.30.

    Args:
        onSystemID: onSystem handle.

    Returns:
        True if removed, False otherwise.
    """
    obj = resolve_handle(onSystemID)
    if obj is None:
        return False
    return detach_child_by_handle(onSystemID)


def setAbstractionDefExtends(
    abstractionDefinitionID: str, vendor: str, library: str, name: str, version: str
) -> bool:  # pragma: no cover - scaffold
    """Set the extends reference.

    Section: F.7.3.44.

    Args:
        abstractionDefinitionID: Abstraction definition handle.
        vendor: Vendor string.
        library: Library string.
        name: Name string.
        version: Version string.

    Returns:
        True on success.

    Raises:
        TgiError: If the handle is invalid.
    """
    ad = _resolve(abstractionDefinitionID)
    if ad is None:
        raise TgiError("Invalid abstraction definition handle", TgiFaultCode.INVALID_ID)
    from org.accellera.ipxact.v1685_2022.library_ref_type import LibraryRefType

    ad.extends = LibraryRefType(vendor=vendor, library=library, name=name, version=version)  # type: ignore[arg-type]
    return True


def removeAbstractionDefPortTransactionalModeBusWidth(portID: str) -> bool:
    """Remove transactional mode busWidth.

    Section: F.7.3.14.

    Args:
        portID: Handle of a transactional port.

    Returns:
        True if at least one busWidth element was removed, else False.
    """
    tr = _ensure_transactional(portID)
    removed = False
    for os in getattr(tr, "on_system", []):
        if getattr(os, "bus_width", None) is not None:
            os.bus_width = None  # type: ignore[attr-defined]
            removed = True
    return removed


def removeAbstractionDefPortTransactionalModeInitiative(portID: str) -> bool:
    """Remove transactional mode initiative across loci.

    Section: F.7.3.15.

    Args:
        portID: Transactional port handle.

    Returns:
        True if any initiative element cleared.
    """
    tr = _ensure_transactional(portID)
    removed = False
    for locus_name in ["on_initiator", "on_target"]:
        locus = getattr(tr, locus_name, None)
        if locus is not None and getattr(locus, "initiative", None) is not None:
            locus.initiative = None  # type: ignore[attr-defined]
            removed = True
    for os in getattr(tr, "on_system", []):
        if getattr(os, "initiative", None) is not None:
            os.initiative = None  # type: ignore[attr-defined]
            removed = True
    return removed


def removeAbstractionDefPortTransactionalModeKind(portID: str) -> bool:
    """Remove transactional mode kind across loci.

    Section: F.7.3.16.

    Args:
        portID: Transactional port handle.

    Returns:
        True if any kind element cleared.
    """
    tr = _ensure_transactional(portID)
    removed = False
    for locus_name in ["on_initiator", "on_target"]:
        locus = getattr(tr, locus_name, None)
        if locus is not None and getattr(locus, "kind", None) is not None:
            locus.kind = None  # type: ignore[attr-defined]
            removed = True
    for os in getattr(tr, "on_system", []):
        if getattr(os, "kind", None) is not None:
            os.kind = None  # type: ignore[attr-defined]
            removed = True
    return removed


def removeAbstractionDefPortTransactionalModePresence(portID: str) -> bool:
    """Remove transactional mode presence across loci.

    Section: F.7.3.17.

    Args:
        portID: Transactional port handle.

    Returns:
        True if any presence element cleared.
    """
    tr = _ensure_transactional(portID)
    removed = False
    for locus_name in ["on_initiator", "on_target"]:
        locus = getattr(tr, locus_name, None)
        if locus is not None and getattr(locus, "presence", None) is not None:
            locus.presence = None  # type: ignore[attr-defined]
            removed = True
    for os in getattr(tr, "on_system", []):
        if getattr(os, "presence", None) is not None:
            os.presence = None  # type: ignore[attr-defined]
            removed = True
    return removed


def removeAbstractionDefPortTransactionalModeProtocol(portID: str) -> bool:
    """Remove transactional mode protocol across loci.

    Section: F.7.3.18.

    Args:
        portID: Transactional port handle.

    Returns:
        True if any protocol element cleared.
    """
    tr = _ensure_transactional(portID)
    removed = False
    for locus_name in ["on_initiator", "on_target"]:
        locus = getattr(tr, locus_name, None)
        if locus is not None and getattr(locus, "protocol", None) is not None:
            locus.protocol = None  # type: ignore[attr-defined]
            removed = True
    for os in getattr(tr, "on_system", []):
        if getattr(os, "protocol", None) is not None:
            os.protocol = None  # type: ignore[attr-defined]
            removed = True
    return removed


def removeAbstractionDefPortTransactionalOnInitiator(portID: str) -> bool:
    """Remove the transactional onInitiator element.

    Section: F.7.3.19.

    Args:
        portID: Transactional port handle.

    Returns:
        True if removed, False if absent.
    """
    tr = _ensure_transactional(portID)
    if tr.on_initiator is not None:
        tr.on_initiator = None  # type: ignore[attr-defined]
        return True
    return False


def removeAbstractionDefPortTransactionalOnTarget(portID: str) -> bool:
    """Remove the transactional onTarget element.

    Section: F.7.3.20.

    Args:
        portID: Transactional port handle.

    Returns:
        True if removed, else False.
    """
    tr = _ensure_transactional(portID)
    if tr.on_target is not None:
        tr.on_target = None  # type: ignore[attr-defined]
        return True
    return False


def removeAbstractionDefPortTransactionalQualifier(portID: str) -> bool:
    """Remove transactional qualifier element.

    Section: F.7.3.21.

    Args:
        portID: Transactional port handle.

    Returns:
        True if qualifier removed.
    """
    tr = _ensure_transactional(portID)
    if getattr(tr, "qualifier", None) is not None:
        tr.qualifier = None  # type: ignore[attr-defined]
        return True
    return False


def _ensure_wire(portID: str):
    """Resolve and return the wire sub-element for a port.

    Helper (non-spec) used by wire set/remove functions.

    Args:
        portID: Handle of a wire style port.

    Returns:
        Wire style object.

    Raises:
        TgiError: If handle invalid or port not wire style.
    """
    p = _resolve_port(portID)
    if p is None:
        raise TgiError("Invalid abstractionDefPort handle", TgiFaultCode.INVALID_ID)
    if p.wire is None:
        raise TgiError("Port not wire", TgiFaultCode.INVALID_ARGUMENT)
    return p.wire


def removeAbstractionDefPortWireModeDirection(portID: str) -> bool:
    """Remove wire mode direction.

    Section: F.7.3.22.

    Args:
        portID: Wire port handle.

    Returns:
        True if direction removed.
    """
    w = _ensure_wire(portID)
    if getattr(w, "direction", None) is not None:
        w.direction = None  # type: ignore[attr-defined]
        return True
    return False


def removeAbstractionDefPortWireModeMirroredModeConstraints(portID: str) -> bool:
    """Remove mirroredModeConstraints.

    Section: F.7.3.23.

    Args:
        portID: Wire port handle.

    Returns:
        True if element removed.
    """
    w = _ensure_wire(portID)
    if getattr(w, "mirrored_mode_constraints", None) is not None:
        w.mirrored_mode_constraints = None  # type: ignore[attr-defined]
        return True
    return False


def removeAbstractionDefPortWireModeModeConstraints(portID: str) -> bool:
    """Remove modeConstraints.

    Section: F.7.3.24.

    Args:
        portID: Wire port handle.

    Returns:
        True if element removed.
    """
    w = _ensure_wire(portID)
    if getattr(w, "mode_constraints", None) is not None:
        w.mode_constraints = None  # type: ignore[attr-defined]
        return True
    return False


def removeAbstractionDefPortWireModePresence(portID: str) -> bool:
    """Remove wire mode presence.

    Section: F.7.3.25.

    Args:
        portID: Wire port handle.

    Returns:
        True if presence removed.
    """
    w = _ensure_wire(portID)
    if getattr(w, "presence", None) is not None:
        w.presence = None  # type: ignore[attr-defined]
        return True
    return False


def removeAbstractionDefPortWireModeWidth(portID: str) -> bool:
    """Remove wire mode width.

    Section: F.7.3.26.

    Args:
        portID: Wire port handle.

    Returns:
        True if width removed.
    """
    w = _ensure_wire(portID)
    if getattr(w, "width", None) is not None:
        w.width = None  # type: ignore[attr-defined]
        return True
    return False


def removeAbstractionDefPortWireOnInitiator(portID: str) -> bool:
    """Remove wire onInitiator (not explicitly modeled).

    Section: F.7.3.27 (stub – underlying schema lacks explicit element).

    Args:
        portID: Wire port handle.

    Returns:
        Always False (no separate element to remove).
    """
    # Not modeled distinctly; return False.
    return False


def removeAbstractionDefPortWireOnTarget(portID: str) -> bool:
    """Remove wire onTarget (not explicitly modeled).

    Section: F.7.3.28 (stub – underlying schema lacks explicit element).

    Args:
        portID: Wire port handle.

    Returns:
        Always False.
    """
    return False


def removeAbstractionDefPortWireQualifier(portID: str) -> bool:
    """Remove wire qualifier.

    Section: F.7.3.29.

    Args:
        portID: Wire port handle.

    Returns:
        True if qualifier removed.
    """
    w = _ensure_wire(portID)
    if getattr(w, "qualifier", None) is not None:
        w.qualifier = None  # type: ignore[attr-defined]
        return True
    return False


def removeAbstractionDefPortWireRequiresDriver(portID: str) -> bool:
    """Remove requiresDriver.

    Section: F.7.3.30.

    Args:
        portID: Wire port handle.

    Returns:
        True if element removed.
    """
    w = _ensure_wire(portID)
    if getattr(w, "requires_driver", None) is not None:
        w.requires_driver = None  # type: ignore[attr-defined]
        return True
    return False


def setAbstractionDefPortTransactionalModeBusWidth(portID: str, value: int | str) -> bool:
    """Set transactional mode busWidth.

    Section: F.7.3.48.

    Args:
        portID: Transactional port handle.
        value: Integer or expression for width.

    Returns:
        True on success.
    """
    tr = _ensure_transactional(portID)
    # Ensure at least one on_system entry exists to hold bus_width per earlier getter logic.
    if not getattr(tr, "on_system", []):  # type: ignore[truthy-bool]
        tr.on_system.append(AbstractionDefinition.Ports.Port.Transactional.OnSystem(group="default"))  # type: ignore[attr-defined]
    from org.accellera.ipxact.v1685_2022.unresolved_unsigned_positive_int_expression import (
        UnresolvedUnsignedPositiveIntExpression,
    )
    bw_expr = UnresolvedUnsignedPositiveIntExpression(value=str(value))  # type: ignore[arg-type]
    tr.on_system[0].bus_width = bw_expr  # type: ignore[attr-defined]
    return True


def setAbstractionDefPortTransactionalModeInitiative(portID: str, value: str) -> bool:
    """Set transactional mode initiative (stored on initiator locus).

    Section: F.7.3.49.

    Args:
        portID: Transactional port handle.
        value: Initiative enumeration string.

    Returns:
        True on success.
    """
    tr = _ensure_transactional(portID)
    if tr.on_initiator is None:
        tr.on_initiator = AbstractionDefinition.Ports.Port.Transactional.OnInitiator()  # type: ignore[attr-defined]
    from org.accellera.ipxact.v1685_2022.initiative import Initiative
    tr.on_initiator.initiative = Initiative(value=value)  # type: ignore[arg-type]
    return True


def setAbstractionDefPortTransactionalModeKind(portID: str, value: str) -> bool:
    """Set transactional mode kind (stored on initiator locus or raw string).

    Section: F.7.3.50.

    Args:
        portID: Transactional port handle.
        value: Kind enumeration string.

    Returns:
        True on success.
    """
    tr = _ensure_transactional(portID)
    if tr.on_initiator is None:
        tr.on_initiator = AbstractionDefinition.Ports.Port.Transactional.OnInitiator()  # type: ignore[attr-defined]
    # KIND maps to 'kind' simple element; underlying xsdata class 'Kind' if present else store raw string
    try:  # pragma: no cover - defensive
        from org.accellera.ipxact.v1685_2022.kind import Kind  # type: ignore
        tr.on_initiator.kind = Kind(value=value)  # type: ignore[arg-type]
    except Exception:  # pragma: no cover
        tr.on_initiator.kind = value  # type: ignore[assignment]
    return True


def setAbstractionDefPortTransactionalModePresence(portID: str, value: str) -> bool:
    """Set transactional mode presence (initiator locus).

    Section: F.7.3.51.

    Args:
        portID: Transactional port handle.
        value: Presence enumeration string.

    Returns:
        True on success.
    """
    tr = _ensure_transactional(portID)
    if tr.on_initiator is None:
        tr.on_initiator = AbstractionDefinition.Ports.Port.Transactional.OnInitiator()  # type: ignore[attr-defined]
    from org.accellera.ipxact.v1685_2022.presence import Presence
    tr.on_initiator.presence = Presence(value=value)  # type: ignore[arg-type]
    return True


def setAbstractionDefPortTransactionalModeProtocol(portID: str, protocol: str) -> bool:
    """Set transactional mode protocol (initiator locus).

    Section: F.7.3.52.

    Args:
        portID: Transactional port handle.
        protocol: Protocol enumeration / identifier string.

    Returns:
        True on success.
    """
    tr = _ensure_transactional(portID)
    if tr.on_initiator is None:
        tr.on_initiator = AbstractionDefinition.Ports.Port.Transactional.OnInitiator()  # type: ignore[attr-defined]
    from org.accellera.ipxact.v1685_2022.protocol import Protocol
    tr.on_initiator.protocol = Protocol(value=protocol)  # type: ignore[arg-type]
    return True


def setAbstractionDefPortTransactionalOnInitiator(portID: str) -> bool:
    """Ensure presence of onInitiator element.

    Section: F.7.3.53.

    Args:
        portID: Transactional port handle.

    Returns:
        True (idempotent).
    """
    tr = _ensure_transactional(portID)
    if tr.on_initiator is None:
        tr.on_initiator = AbstractionDefinition.Ports.Port.Transactional.OnInitiator()  # type: ignore[attr-defined]
    return True


def setAbstractionDefPortTransactionalOnTarget(portID: str) -> bool:
    """Ensure presence of onTarget element.

    Section: F.7.3.54.

    Args:
        portID: Transactional port handle.

    Returns:
        True (idempotent).
    """
    tr = _ensure_transactional(portID)
    if tr.on_target is None:
        tr.on_target = AbstractionDefinition.Ports.Port.Transactional.OnTarget()  # type: ignore[attr-defined]
    return True


def setAbstractionDefPortTransactionalQualifier(portID: str, qualifier: str) -> bool:
    """Set transactional qualifier.

    Section: F.7.3.55.

    Args:
        portID: Transactional port handle.
        qualifier: Qualifier string.

    Returns:
        True on success.
    """
    tr = _ensure_transactional(portID)
    from org.accellera.ipxact.v1685_2022.qualifier_type import QualifierType
    tr.qualifier = QualifierType(value=qualifier)  # type: ignore[arg-type]
    return True


def setAbstractionDefPortTransactional(portID: str) -> bool:
    """Ensure port has transactional style container.

    Section: F.7.3.56.

    Args:
        portID: Port handle.

    Returns:
        True (idempotent create).
    """
    p = _resolve_port(portID)
    if p is None:
        raise TgiError("Invalid abstractionDefPort handle", TgiFaultCode.INVALID_ID)
    if p.transactional is None:
        p.transactional = AbstractionDefinition.Ports.Port.Transactional()  # type: ignore[attr-defined]
    return True


def setAbstractionDefPortWire(portID: str) -> bool:
    """Ensure port has wire style container.

    Section: F.7.3.57.

    Args:
        portID: Port handle.

    Returns:
        True (idempotent create).
    """
    p = _resolve_port(portID)
    if p is None:
        raise TgiError("Invalid abstractionDefPort handle", TgiFaultCode.INVALID_ID)
    if p.wire is None:
        from org.accellera.ipxact.v1685_2022.wire import Wire
        p.wire = Wire()  # type: ignore[arg-type]
    return True


def setAbstractionDefPortWireDefaultValue(portID: str, value: int | str) -> bool:
    """Set wire defaultValue.

    Section: F.7.3.58.

    Args:
        portID: Wire port handle.
        value: Integer or expression string.

    Returns:
        True on success.
    """
    w = _ensure_wire(portID)
    from org.accellera.ipxact.v1685_2022.value import Value as ValueClass
    w.default_value = ValueClass(value=str(value))  # type: ignore[arg-type]
    return True


def setAbstractionDefPortWireModeDirection(portID: str, direction: str) -> bool:
    """Set wire mode direction.

    Section: F.7.3.59.

    Args:
        portID: Wire port handle.
        direction: Direction enumeration string.

    Returns:
        True on success.
    """
    w = _ensure_wire(portID)
    from org.accellera.ipxact.v1685_2022.direction import Direction
    w.direction = Direction(value=direction)  # type: ignore[arg-type]
    return True


def setAbstractionDefPortWireModeMirroredModeConstraints(portID: str) -> bool:
    """Create mirroredModeConstraints container.

    Section: F.7.3.60.

    Args:
        portID: Wire port handle.

    Returns:
        True on success.
    """
    w = _ensure_wire(portID)
    from org.accellera.ipxact.v1685_2022.abstraction_def_port_constraints_type import (
        AbstractionDefPortConstraintsType,
    )
    w.mirrored_mode_constraints = AbstractionDefPortConstraintsType()  # type: ignore[arg-type]
    return True


def setAbstractionDefPortWireModeModeConstraints(portID: str) -> bool:
    """Create modeConstraints container.

    Section: F.7.3.61.

    Args:
        portID: Wire port handle.

    Returns:
        True on success.
    """
    w = _ensure_wire(portID)
    from org.accellera.ipxact.v1685_2022.abstraction_def_port_constraints_type import (
        AbstractionDefPortConstraintsType,
    )
    w.mode_constraints = AbstractionDefPortConstraintsType()  # type: ignore[arg-type]
    return True


def setAbstractionDefPortWireModePresence(portID: str, value: str) -> bool:
    """Set wire mode presence.

    Section: F.7.3.62.

    Args:
        portID: Wire port handle.
        value: Presence enumeration string.

    Returns:
        True on success.
    """
    w = _ensure_wire(portID)
    from org.accellera.ipxact.v1685_2022.presence import Presence
    w.presence = Presence(value=value)  # type: ignore[arg-type]
    return True


def setAbstractionDefPortWireModeWidth(portID: str, value: int | str) -> bool:
    """Set wire mode width.

    Section: F.7.3.63.

    Args:
        portID: Wire port handle.
        value: Integer or expression string.

    Returns:
        True on success.
    """
    w = _ensure_wire(portID)
    from org.accellera.ipxact.v1685_2022.unresolved_unsigned_positive_int_expression import (
        UnresolvedUnsignedPositiveIntExpression,
    )
    w.width = UnresolvedUnsignedPositiveIntExpression(value=str(value))  # type: ignore[arg-type]
    return True


def setAbstractionDefPortWireOnInitiator(portID: str) -> bool:  # Not distinct in model
    """Stub: ensure wire onInitiator (no-op).

    Section: F.7.3.64 (schema does not expose a distinct element).

    Args:
        portID: Wire port handle.

    Returns:
        True (no-op).
    """
    return True


def setAbstractionDefPortWireOnTarget(portID: str) -> bool:  # Not distinct in model
    """Stub: ensure wire onTarget (no-op).

    Section: F.7.3.65 (schema does not expose a distinct element).

    Args:
        portID: Wire port handle.

    Returns:
        True (no-op).
    """
    return True


def setAbstractionDefPortWireQualifier(portID: str, qualifier: str) -> bool:
    """Set wire qualifier.

    Section: F.7.3.66.

    Args:
        portID: Wire port handle.
        qualifier: Qualifier string.

    Returns:
        True on success.
    """
    w = _ensure_wire(portID)
    from org.accellera.ipxact.v1685_2022.qualifier_type import QualifierType
    w.qualifier = QualifierType(value=qualifier)  # type: ignore[arg-type]
    return True


def setAbstractionDefPortWireRequiresDriver(portID: str, flag: bool) -> bool:
    """Set requiresDriver flag.

    Section: F.7.3.67.

    Args:
        portID: Wire port handle.
        flag: Boolean value.

    Returns:
        True on success.
    """
    w = _ensure_wire(portID)
    from org.accellera.ipxact.v1685_2022.requires_driver import RequiresDriver
    w.requires_driver = RequiresDriver(value=flag)  # type: ignore[arg-type]
    return True
