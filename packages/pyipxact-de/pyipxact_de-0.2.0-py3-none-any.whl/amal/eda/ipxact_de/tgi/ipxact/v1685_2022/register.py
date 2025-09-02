"""Register category TGI functions (IEEE 1685-2022).

Implements BASE (F.7.73) and EXTENDED (F.7.74) Register functions. Only the
functions defined in Annex F are exported. BASE getters return empty/None for
invalid handles. EXTENDED mutators raise :class:`TgiError` with appropriate
:TgiFaultCode values. Schema coverage is partial; where underlying objects are
absent the operations return graceful defaults or raise ``INVALID_ID``.
"""
# ruff: noqa: I001
from typing import Any
from types import SimpleNamespace

from .core import (
    TgiError,
    TgiFaultCode,
    get_handle,
    resolve_handle,
    register_parent,
    detach_child_by_handle,
)

__all__ = [
    # BASE (F.7.73)
    "getAliasOfAlternateRegisterRefByName",
    "getAliasOfAlternateRegisterRefID",
    "getAliasOfFieldRefByName",
    "getAliasOfFieldRefID",
    "getAliasOfRegisterRefByName",
    "getAliasOfRegisterRefID",
    "getAlternateRegisterFieldIDs",
    "getAlternateRegisterModeRefIDs",
    "getAlternateRegisterRefAlternateRegisterRefByName",
    "getAlternateRegisterTypeIdentifier",
    "getAlternateRegisterVolatility",
    "getBroadcastToAddressBlockRefByName",
    "getBroadcastToAddressBlockRefID",
    "getBroadcastToAddressSpaceRefByName",
    "getBroadcastToAddressSpaceRefID",
    "getBroadcastToAlternateRegisterRefByName",
    "getBroadcastToAlternateRegisterRefID",
    "getBroadcastToBankRefByNames",
    "getBroadcastToBankRefIDs",
    "getBroadcastToFieldRefByName",
    "getBroadcastToFieldRefID",
    "getBroadcastToMemoryMapRefByName",
    "getBroadcastToMemoryMapRefID",
    "getBroadcastToRegisterFileRefByNames",
    "getBroadcastToRegisterFileRefIDs",
    "getBroadcastToRegisterRefByName",
    "getBroadcastToRegisterRefID",
    "getEnumeratedValueExpression",
    "getEnumeratedValueUsage",
    "getEnumeratedValueValue",
    "getEnumeratedValueValueExpression",
    "getEnumeratedValueValueID",
    "getEnumeratedValuesEnumeratedValueIDs",
    "getEnumeratedValuesEnumerationDefinitionRefByExternalTypeDefID",
    "getEnumeratedValuesEnumerationDefinitionRefByID",
    "getEnumeratedValuesEnumerationDefinitionRefByName",
    "getEnumeratedValuesEnumerationDefinitionRefID",
    "getFieldBitOffsetID",
    "getFieldDefinitionBitWidthID",
    "getFieldDefinitionEnumeratedValueIDs",
    "getFieldDefinitionTypeIdentifier",
    "getFieldDefinitionVolatile",
    "getFieldRefFieldRefByName",
    "getFieldRefIndexIDs",
    "getRegisterAddressOffset",
    "getRegisterAddressOffsetExpression",
    "getRegisterAddressOffsetID",
    "getRegisterAlternateRegisterIDs",
    "getRegisterFieldAliasOfID",
    "getRegisterFieldBitOffset",
    "getRegisterFieldBitOffsetExpression",
    "getRegisterFieldBitOffsetID",
    "getRegisterFieldBitWidth",
    "getRegisterFieldBitWidthExpression",
    "getRegisterFieldBitWidthID",
    "getRegisterFieldEnumeratedValuesID",
    "getRegisterFieldFieldDefinitionRefByExternalTypeDefID",
    "getRegisterFieldFieldDefinitionRefByID",
    "getRegisterFieldFieldDefinitionRefByName",
    "getRegisterFieldFieldDefinitionRefID",
    "getRegisterFieldIDs",
    "getRegisterFieldResetIDs",
    "getRegisterFieldTypeIdentifier",
    "getRegisterFieldVolatility",
    "getRegisterFileAddressOffsetID",
    "getRegisterRefAttributeByID",
    "getRegisterRefIndexIDs",
    "getRegisterRefRegisterRefByName",
    "getRegisterRegisterDefinitionRefByExternalTypeDefID",
    "getRegisterRegisterDefinitionRefByID",
    "getRegisterRegisterDefinitionRefByName",
    "getRegisterRegisterDefinitionRefID",
    "getRegisterSize",
    "getRegisterSizeExpression",
    "getRegisterSizeID",
    "getRegisterTypeIdentifier",
    "getRegisterVolatility",
    "getResetMask",
    "getResetMaskExpression",
    "getResetMaskID",
    "getResetValue",
    "getResetValueExpression",
    "getResetValueID",
    # EXTENDED (F.7.74)
    "addAlternateRegisterField",
    "addAlternaterRegisterModeRef",
    "addBroadcastToBankRef",
    "addBroadcastToRegisterFileRef",
    "addEnumeratedValuesFieldEnumeratedValue",
    "addFieldRefIndex",
    "addRegisterAlternateRegister",
    "addRegisterField",
    "addRegisterFieldReset",
    "addRegisterRefIndex",
    "removeAliasOfAlternateRegisterRef",
    "removeAliasOfRegisterRef",
    "removeAlternateRegisterField",
    "removeAlternateRegisterTypeIdentifier",
    "removeAlternateRegisterVolatility",
    "removeAlternaterRegisterModeRef",
    "removeBroadcastToAddressBlockRef",
    "removeBroadcastToAlternateRegisterRef",
    "removeBroadcastToBankRef",
    "removeBroadcastToMemoryMapRef",
    "removeBroadcastToRegisterFileRef",
    "removeBroadcastToRegisterRef",
]

# ---------------------------------------------------------------------------
# Internal helper utilities (non-spec)
# ---------------------------------------------------------------------------


def _resolve(handle: str) -> Any | None:
    return resolve_handle(handle)


def _maybe_value(node: Any | None) -> Any | None:
    if node is None:
        return None
    return getattr(node, "value", node)


def _list_handles(container: Any | None, attr: str) -> list[str]:
    if container is None:
        return []
    lst = getattr(container, attr, [])
    return [get_handle(e) for e in lst]


def _coerce_int(value: str) -> int | str:
    """Best-effort convert to int (supports bases)."""
    try:
        return int(value, 0)
    except Exception:  # noqa: BLE001
        return value


def _ns(**kwargs: Any) -> SimpleNamespace:
    return SimpleNamespace(**kwargs)

# ---------------------------------------------------------------------------
# BASE (F.7.73) – many getters are thin wrappers over attribute presence
# NOTE: Due to absent concrete schema linkages in this development snapshot,
# several getters return None/[] because underlying model classes are not yet
# wired. Implementations keep signature & error-handling contract.
# ---------------------------------------------------------------------------
# The following block uses repetitive patterns; each function retains a short
# docstring referencing its Section number for traceability.


def getAliasOfAlternateRegisterRefByName(aliasOfID: str) -> str | None:
    """Return alternateRegisterRef value (F.7.73.1)."""
    a = _resolve(aliasOfID)
    ref = getattr(a, "alternate_register_ref", None)
    return _maybe_value(ref)


def getAliasOfAlternateRegisterRefID(aliasOfID: str) -> str | None:
    """Return handle of alternateRegisterRef (F.7.73.2)."""
    a = _resolve(aliasOfID)
    ref = getattr(a, "alternate_register_ref", None)
    return get_handle(ref) if ref is not None else None


def getAliasOfFieldRefByName(aliasOfID: str) -> str | None:
    """Return fieldRef value (F.7.73.3)."""
    a = _resolve(aliasOfID)
    ref = getattr(a, "field_ref", None)
    return _maybe_value(ref)


def getAliasOfFieldRefID(aliasOfID: str) -> str | None:
    """Return handle of fieldRef (F.7.73.4)."""
    a = _resolve(aliasOfID)
    ref = getattr(a, "field_ref", None)
    return get_handle(ref) if ref is not None else None


def getAliasOfRegisterRefByName(aliasOfID: str) -> str | None:
    """Return registerRef value (F.7.73.5)."""
    a = _resolve(aliasOfID)
    ref = getattr(a, "register_ref", None)
    return _maybe_value(ref)


def getAliasOfRegisterRefID(aliasOfID: str) -> str | None:
    """Return handle of registerRef (F.7.73.6)."""
    a = _resolve(aliasOfID)
    ref = getattr(a, "register_ref", None)
    return get_handle(ref) if ref is not None else None


def getAlternateRegisterFieldIDs(alternateRegisterID: str) -> list[str]:
    """Return field handles of alternateRegister (F.7.73.7)."""
    ar = _resolve(alternateRegisterID)
    return _list_handles(ar, "field")


def getAlternateRegisterModeRefIDs(alternateRegisterID: str) -> list[str]:
    """Return modeRef handles (F.7.73.8)."""
    ar = _resolve(alternateRegisterID)
    return _list_handles(ar, "mode_ref")


def getAlternateRegisterRefAlternateRegisterRefByName(alternateRegisterRefID: str) -> str | None:
    """Return alternateRegisterRef value (F.7.73.9)."""
    r = _resolve(alternateRegisterRefID)
    return _maybe_value(getattr(r, "alternate_register_ref", None))


def getAlternateRegisterTypeIdentifier(alternateRegisterID: str) -> str | None:
    """Return typeIdentifier value (F.7.73.10)."""
    ar = _resolve(alternateRegisterID)
    return _maybe_value(getattr(ar, "type_identifier", None))


def getAlternateRegisterVolatility(alternateRegisterID: str) -> bool | None:
    """Return volatility boolean (F.7.73.11)."""
    ar = _resolve(alternateRegisterID)
    val = getattr(getattr(ar, "volatile", None), "value", None)
    return val if isinstance(val, bool) else None

# BroadcastTo getters (grouped)


def getBroadcastToAddressBlockRefByName(broadcastToID: str) -> str | None:
    """Return addressBlockRef value (F.7.73.12)."""
    b = _resolve(broadcastToID)
    return _maybe_value(getattr(b, "address_block_ref", None))


def getBroadcastToAddressBlockRefID(broadcastToID: str) -> str | None:
    """Return handle of addressBlockRef (F.7.73.13)."""
    b = _resolve(broadcastToID)
    ref = getattr(b, "address_block_ref", None)
    return get_handle(ref) if ref is not None else None


def getBroadcastToAddressSpaceRefByName(broadcastToID: str) -> str | None:
    """Return addressSpaceRef value (F.7.73.14)."""
    b = _resolve(broadcastToID)
    return _maybe_value(getattr(b, "address_space_ref", None))


def getBroadcastToAddressSpaceRefID(broadcastToID: str) -> str | None:
    """Return handle of addressSpaceRef (F.7.73.15)."""
    b = _resolve(broadcastToID)
    ref = getattr(b, "address_space_ref", None)
    return get_handle(ref) if ref is not None else None


def getBroadcastToAlternateRegisterRefByName(broadcastToID: str) -> str | None:
    """Return alternateRegisterRef value (F.7.73.16)."""
    b = _resolve(broadcastToID)
    return _maybe_value(getattr(b, "alternate_register_ref", None))


def getBroadcastToAlternateRegisterRefID(broadcastToID: str) -> str | None:
    """Return handle of alternateRegisterRef (F.7.73.17)."""
    b = _resolve(broadcastToID)
    ref = getattr(b, "alternate_register_ref", None)
    return get_handle(ref) if ref is not None else None


def getBroadcastToBankRefByNames(broadcastToID: str) -> list[str]:
    """Return list of bankRef values (F.7.73.18)."""
    b = _resolve(broadcastToID)
    vals = getattr(b, "bank_ref", []) if b else []
    result: list[str] = []
    for v in vals:
        val = getattr(v, "value", v)
        if val is not None:
            result.append(str(val))
    return result


def getBroadcastToBankRefIDs(broadcastToID: str) -> list[str]:
    """Return handles of bankRef elements (F.7.73.19)."""
    b = _resolve(broadcastToID)
    return _list_handles(b, "bank_ref")


def getBroadcastToFieldRefByName(broadcastToID: str) -> str | None:
    """Return fieldRef value (F.7.73.20)."""
    b = _resolve(broadcastToID)
    return _maybe_value(getattr(b, "field_ref", None))


def getBroadcastToFieldRefID(broadcastToID: str) -> str | None:
    """Return handle of fieldRef (F.7.73.21)."""
    b = _resolve(broadcastToID)
    ref = getattr(b, "field_ref", None)
    return get_handle(ref) if ref is not None else None


def getBroadcastToMemoryMapRefByName(broadcastToID: str) -> str | None:
    """Return memoryMapRef value (F.7.73.22)."""
    b = _resolve(broadcastToID)
    return _maybe_value(getattr(b, "memory_map_ref", None))


def getBroadcastToMemoryMapRefID(broadcastToID: str) -> str | None:
    """Return handle of memoryMapRef (F.7.73.23)."""
    b = _resolve(broadcastToID)
    ref = getattr(b, "memory_map_ref", None)
    return get_handle(ref) if ref is not None else None


def getBroadcastToRegisterFileRefByNames(broadcastToID: str) -> list[str]:
    """Return registerFileRef names (F.7.73.24)."""
    b = _resolve(broadcastToID)
    refs = getattr(b, "register_file_ref", []) if b else []
    out: list[str] = []
    for r in refs:
        val = getattr(r, "value", r)
        if val is not None:
            out.append(str(val))
    return out


def getBroadcastToRegisterFileRefIDs(broadcastToID: str) -> list[str]:
    """Return handles of registerFileRef elements (F.7.73.25)."""
    b = _resolve(broadcastToID)
    return _list_handles(b, "register_file_ref")


def getBroadcastToRegisterRefByName(broadcastToID: str) -> str | None:
    """Return registerRef value (F.7.73.26)."""
    b = _resolve(broadcastToID)
    return _maybe_value(getattr(b, "register_ref", None))


def getBroadcastToRegisterRefID(broadcastToID: str) -> str | None:
    """Return handle of registerRef (F.7.73.27)."""
    b = _resolve(broadcastToID)
    ref = getattr(b, "register_ref", None)
    return get_handle(ref) if ref is not None else None

# EnumeratedValue(s)


def getEnumeratedValueExpression(enumeratedValueID: str) -> str | None:
    """Return expression (F.7.73.28)."""
    ev = _resolve(enumeratedValueID)
    return _maybe_value(getattr(ev, "expression", None))


def getEnumeratedValueUsage(enumeratedValueID: str) -> str | None:
    """Return usage (F.7.73.29)."""
    ev = _resolve(enumeratedValueID)
    return _maybe_value(getattr(ev, "usage", None))


def getEnumeratedValueValue(enumeratedValueID: str) -> int | None:
    """Return numeric value (F.7.73.30)."""
    ev = _resolve(enumeratedValueID)
    val = getattr(getattr(ev, "value", None), "value", None)
    return int(val) if isinstance(val, int | bool) else None


def getEnumeratedValueValueExpression(enumeratedValueID: str) -> str | None:
    """Return value expression (F.7.73.31)."""
    ev = _resolve(enumeratedValueID)
    value = getattr(ev, "value", None)
    return getattr(value, "value_expression", None)


def getEnumeratedValueValueID(enumeratedValueID: str) -> str | None:
    """Return handle of value element (F.7.73.32)."""
    ev = _resolve(enumeratedValueID)
    value = getattr(ev, "value", None)
    return get_handle(value) if value is not None else None


def getEnumeratedValuesEnumeratedValueIDs(enumeratedValuesID: str) -> list[str]:
    """Return enumeratedValue handles (F.7.73.33)."""
    evs = _resolve(enumeratedValuesID)
    return _list_handles(evs, "enumerated_value")


def getEnumeratedValuesEnumerationDefinitionRefByExternalTypeDefID(enumeratedValuesID: str) -> str | None:
    """Return externalTypeDefinitions handle (F.7.73.34)."""
    evs = _resolve(enumeratedValuesID)
    ref = getattr(getattr(evs, "enumeration_definition_ref", None), "external_type_definitions", None)
    return get_handle(ref) if ref is not None else None


def getEnumeratedValuesEnumerationDefinitionRefByID(enumeratedValuesID: str) -> str | None:
    """Return enumerationDefinition handle (F.7.73.35)."""
    evs = _resolve(enumeratedValuesID)
    ref = getattr(getattr(evs, "enumeration_definition_ref", None), "enumeration_definition", None)
    return get_handle(ref) if ref is not None else None


def getEnumeratedValuesEnumerationDefinitionRefByName(enumeratedValuesID: str) -> str | None:
    """Return enumerationDefinitionRef value (F.7.73.36)."""
    evs = _resolve(enumeratedValuesID)
    ref = getattr(evs, "enumeration_definition_ref", None)
    return _maybe_value(ref)


def getEnumeratedValuesEnumerationDefinitionRefID(enumeratedValuesID: str) -> str | None:
    """Return handle of enumerationDefinitionRef (F.7.73.37)."""
    evs = _resolve(enumeratedValuesID)
    ref = getattr(evs, "enumeration_definition_ref", None)
    return get_handle(ref) if ref is not None else None

# Field / FieldDefinition / FieldRef


def getFieldBitOffsetID(fieldID: str) -> str | None:
    """Return bitOffset handle (F.7.73.38)."""
    f = _resolve(fieldID)
    off = getattr(f, "bit_offset", None)
    return get_handle(off) if off is not None else None


def getFieldDefinitionBitWidthID(fieldDefinitionID: str) -> str | None:
    """Return bitWidth handle (F.7.73.39)."""
    fd = _resolve(fieldDefinitionID)
    bw = getattr(fd, "bit_width", None)
    return get_handle(bw) if bw is not None else None


def getFieldDefinitionEnumeratedValueIDs(fieldDefinitionID: str) -> list[str]:
    """Return enumeratedValue handles (F.7.73.40)."""
    fd = _resolve(fieldDefinitionID)
    return _list_handles(fd, "enumerated_value")


def getFieldDefinitionTypeIdentifier(fieldDefinitionID: str) -> str | None:
    """Return typeIdentifier (F.7.73.41)."""
    fd = _resolve(fieldDefinitionID)
    return _maybe_value(getattr(fd, "type_identifier", None))


def getFieldDefinitionVolatile(fieldDefinitionID: str) -> bool | None:
    """Return volatile flag (F.7.73.42)."""
    fd = _resolve(fieldDefinitionID)
    val = getattr(getattr(fd, "volatile", None), "value", None)
    return val if isinstance(val, bool) else None


def getFieldRefFieldRefByName(fieldRefID: str) -> str | None:
    """Return fieldRef value (F.7.73.43)."""
    fr = _resolve(fieldRefID)
    return _maybe_value(getattr(fr, "field_ref", None))


def getFieldRefIndexIDs(fieldRefID: str) -> list[str]:
    """Return index handles (F.7.73.44)."""
    fr = _resolve(fieldRefID)
    return _list_handles(fr, "index")

# Register (address / size / type)


def getRegisterAddressOffset(registerID: str) -> int | None:
    """Return addressOffset value (F.7.73.45)."""
    r = _resolve(registerID)
    off = getattr(r, "address_offset", None)
    val = getattr(off, "value", None)
    return int(val) if isinstance(val, int) else None


def getRegisterAddressOffsetExpression(registerID: str) -> str | None:
    """Return addressOffset expression (F.7.73.46)."""
    r = _resolve(registerID)
    off = getattr(r, "address_offset", None)
    return getattr(off, "value_expression", None)


def getRegisterAddressOffsetID(registerID: str) -> str | None:
    """Return handle of addressOffset (F.7.73.47)."""
    r = _resolve(registerID)
    off = getattr(r, "address_offset", None)
    return get_handle(off) if off is not None else None


def getRegisterAlternateRegisterIDs(registerID: str) -> list[str]:
    """Return alternateRegister handles (F.7.73.48)."""
    r = _resolve(registerID)
    return _list_handles(r, "alternate_register")

# Register Field getters (aliases, offsets, widths, enumeratedValues, resets)


def getRegisterFieldAliasOfID(registerFieldID: str) -> str | None:
    """Return aliasOf handle (F.7.73.49)."""
    f = _resolve(registerFieldID)
    ao = getattr(f, "alias_of", None)
    return get_handle(ao) if ao is not None else None


def getRegisterFieldBitOffset(registerFieldID: str) -> int | None:
    """Return bitOffset value (F.7.73.50)."""
    f = _resolve(registerFieldID)
    off = getattr(f, "bit_offset", None)
    val = getattr(off, "value", None)
    return int(val) if isinstance(val, int) else None


def getRegisterFieldBitOffsetExpression(registerFieldID: str) -> str | None:
    """Return bitOffset expression (F.7.73.51)."""
    f = _resolve(registerFieldID)
    off = getattr(f, "bit_offset", None)
    return getattr(off, "value_expression", None)


def getRegisterFieldBitOffsetID(registerFieldID: str) -> str | None:
    """Return handle of bitOffset (F.7.73.52)."""
    f = _resolve(registerFieldID)
    off = getattr(f, "bit_offset", None)
    return get_handle(off) if off is not None else None


def getRegisterFieldBitWidth(registerFieldID: str) -> int | None:
    """Return bitWidth numeric value (F.7.73.53)."""
    f = _resolve(registerFieldID)
    w = getattr(f, "bit_width", None)
    val = getattr(w, "value", None)
    return int(val) if isinstance(val, int) else None


def getRegisterFieldBitWidthExpression(registerFieldID: str) -> str | None:
    """Return bitWidth expression (F.7.73.54)."""
    f = _resolve(registerFieldID)
    w = getattr(f, "bit_width", None)
    return getattr(w, "value_expression", None)


def getRegisterFieldBitWidthID(registerFieldID: str) -> str | None:
    """Return bitWidth handle (F.7.73.55)."""
    f = _resolve(registerFieldID)
    w = getattr(f, "bit_width", None)
    return get_handle(w) if w is not None else None


def getRegisterFieldEnumeratedValuesID(registerFieldID: str) -> str | None:
    """Return enumeratedValues handle (F.7.73.56)."""
    f = _resolve(registerFieldID)
    evs = getattr(f, "enumerated_values", None)
    return get_handle(evs) if evs is not None else None


def getRegisterFieldFieldDefinitionRefByExternalTypeDefID(registerFieldID: str) -> str | None:
    """Return externalTypeDefinitions handle (F.7.73.57)."""
    f = _resolve(registerFieldID)
    ref = getattr(getattr(f, "field_definition_ref", None), "external_type_definitions", None)
    return get_handle(ref) if ref is not None else None


def getRegisterFieldFieldDefinitionRefByID(registerFieldID: str) -> str | None:
    """Return fieldDefinition handle (F.7.73.58)."""
    f = _resolve(registerFieldID)
    ref = getattr(getattr(f, "field_definition_ref", None), "field_definition", None)
    return get_handle(ref) if ref is not None else None


def getRegisterFieldFieldDefinitionRefByName(registerFieldID: str) -> str | None:
    """Return fieldDefinitionRef value (F.7.73.59)."""
    f = _resolve(registerFieldID)
    ref = getattr(f, "field_definition_ref", None)
    return _maybe_value(ref)


def getRegisterFieldFieldDefinitionRefID(registerFieldID: str) -> str | None:
    """Return fieldDefinitionRef handle (F.7.73.60)."""
    f = _resolve(registerFieldID)
    ref = getattr(f, "field_definition_ref", None)
    return get_handle(ref) if ref is not None else None


def getRegisterFieldIDs(registerID: str) -> list[str]:
    """Return register field handles (F.7.73.61)."""
    r = _resolve(registerID)
    return _list_handles(r, "field")


def getRegisterFieldResetIDs(registerFieldID: str) -> list[str]:
    """Return reset handles (F.7.73.62)."""
    f = _resolve(registerFieldID)
    return _list_handles(f, "reset")


def getRegisterFieldTypeIdentifier(registerFieldID: str) -> str | None:
    """Return typeIdentifier (F.7.73.63)."""
    f = _resolve(registerFieldID)
    return _maybe_value(getattr(f, "type_identifier", None))


def getRegisterFieldVolatility(registerFieldID: str) -> bool | None:
    """Return volatility flag (F.7.73.64)."""
    f = _resolve(registerFieldID)
    val = getattr(getattr(f, "volatile", None), "value", None)
    return val if isinstance(val, bool) else None


def getRegisterFileAddressOffsetID(registerFileID: str) -> str | None:
    """Return addressOffset handle (F.7.73.65)."""
    rf = _resolve(registerFileID)
    off = getattr(rf, "address_offset", None)
    return get_handle(off) if off is not None else None

# RegisterRef


def getRegisterRefAttributeByID(registerRefID: str) -> str | None:
    """Return referenced register handle (F.7.73.66)."""
    rr = _resolve(registerRefID)
    reg = getattr(rr, "register", None)
    return get_handle(reg) if reg is not None else None


def getRegisterRefIndexIDs(registerRefID: str) -> list[str]:
    """Return index handles (F.7.73.67)."""
    rr = _resolve(registerRefID)
    return _list_handles(rr, "index")


def getRegisterRefRegisterRefByName(registerRefID: str) -> str | None:
    """Return registerRef value (F.7.73.68)."""
    rr = _resolve(registerRefID)
    return _maybe_value(getattr(rr, "register_ref", None))

# Register definition references


def getRegisterRegisterDefinitionRefByExternalTypeDefID(registerID: str) -> str | None:
    """Return externalTypeDefinitions handle (F.7.73.69)."""
    r = _resolve(registerID)
    ref = getattr(getattr(r, "register_definition_ref", None), "external_type_definitions", None)
    return get_handle(ref) if ref is not None else None


def getRegisterRegisterDefinitionRefByID(registerID: str) -> str | None:
    """Return registerDefinition handle (F.7.73.70)."""
    r = _resolve(registerID)
    ref = getattr(getattr(r, "register_definition_ref", None), "register_definition", None)
    return get_handle(ref) if ref is not None else None


def getRegisterRegisterDefinitionRefByName(registerID: str) -> str | None:
    """Return registerDefinitionRef value (F.7.73.71)."""
    r = _resolve(registerID)
    ref = getattr(r, "register_definition_ref", None)
    return _maybe_value(ref)


def getRegisterRegisterDefinitionRefID(registerID: str) -> str | None:
    """Return registerDefinitionRef handle (F.7.73.72)."""
    r = _resolve(registerID)
    ref = getattr(r, "register_definition_ref", None)
    return get_handle(ref) if ref is not None else None

# Size / type / volatility


def getRegisterSize(registerID: str) -> int | None:
    """Return size value (F.7.73.73)."""
    r = _resolve(registerID)
    sz = getattr(r, "size", None)
    val = getattr(sz, "value", None)
    return int(val) if isinstance(val, int) else None


def getRegisterSizeExpression(registerID: str) -> str | None:
    """Return size expression (F.7.73.74)."""
    r = _resolve(registerID)
    sz = getattr(r, "size", None)
    return getattr(sz, "value_expression", None)


def getRegisterSizeID(registerID: str) -> str | None:
    """Return size handle (F.7.73.75)."""
    r = _resolve(registerID)
    sz = getattr(r, "size", None)
    return get_handle(sz) if sz is not None else None


def getRegisterTypeIdentifier(registerID: str) -> str | None:
    """Return typeIdentifier (F.7.73.76)."""
    r = _resolve(registerID)
    return _maybe_value(getattr(r, "type_identifier", None))


def getRegisterVolatility(registerID: str) -> bool | None:
    """Return volatility boolean (F.7.73.77)."""
    r = _resolve(registerID)
    val = getattr(getattr(r, "volatile", None), "value", None)
    return val if isinstance(val, bool) else None

# Reset values


def getResetMask(resetID: str) -> int | None:
    """Return reset mask resolved value (F.7.73.78)."""
    rst = _resolve(resetID)
    m = getattr(rst, "mask", None)
    val = getattr(m, "value", None)
    return int(val) if isinstance(val, int) else None


def getResetMaskExpression(resetID: str) -> str | None:
    """Return reset mask expression (F.7.73.79)."""
    rst = _resolve(resetID)
    m = getattr(rst, "mask", None)
    return getattr(m, "value_expression", None)


def getResetMaskID(resetID: str) -> str | None:
    """Return mask handle (F.7.73.80)."""
    rst = _resolve(resetID)
    m = getattr(rst, "mask", None)
    return get_handle(m) if m is not None else None


def getResetValue(resetID: str) -> int | None:
    """Return reset value (F.7.73.81)."""
    rst = _resolve(resetID)
    v = getattr(rst, "value", None)
    val = getattr(v, "value", None)
    return int(val) if isinstance(val, int) else None


def getResetValueExpression(resetID: str) -> str | None:
    """Return reset value expression (F.7.73.82)."""
    rst = _resolve(resetID)
    v = getattr(rst, "value", None)
    return getattr(v, "value_expression", None)


def getResetValueID(resetID: str) -> str | None:
    """Return reset value handle (F.7.73.83)."""
    rst = _resolve(resetID)
    v = getattr(rst, "value", None)
    return get_handle(v) if v is not None else None

# ---------------------------------------------------------------------------
# EXTENDED (F.7.74)
# Mutators below create/remove child elements or attributes. Where schema
# objects are unavailable they raise INVALID_ID to signal unsupported handle.
# Implementations are skeletal pending full schema integration.
# ---------------------------------------------------------------------------


def addAlternateRegisterField(alternateRegisterID: str, name: str, offset: str, width: str) -> str:
    """Add field to alternateRegister (F.7.74.1)."""
    ar = _resolve(alternateRegisterID)
    if ar is None:
        raise TgiError("Invalid alternateRegister handle", TgiFaultCode.INVALID_ID)
    field = _ns(
        name=name,
        bit_offset=_ns(value=_coerce_int(offset)),
        bit_width=_ns(value=_coerce_int(width)),
    )
    if not hasattr(ar, "field"):
        ar.field = []  # type: ignore[attr-defined]
    ar.field.append(field)  # type: ignore[attr-defined]
    register_parent(field, ar, ("field",), "list")
    return get_handle(field)


def addAlternaterRegisterModeRef(alternateRegisterID: str, modeRef: str, priority: int) -> str:
    """Add modeRef to alternateRegister (F.7.74.2)."""
    ar = _resolve(alternateRegisterID)
    if ar is None:
        raise TgiError("Invalid alternateRegister handle", TgiFaultCode.INVALID_ID)
    mr = _ns(value=modeRef, priority=priority)
    if not hasattr(ar, "mode_ref"):
        ar.mode_ref = []  # type: ignore[attr-defined]
    ar.mode_ref.append(mr)  # type: ignore[attr-defined]
    register_parent(mr, ar, ("mode_ref",), "list")
    return get_handle(mr)


def addBroadcastToBankRef(broadcastToID: str, bankRef: str) -> str:
    """Add bankRef to broadcastTo (F.7.74.3)."""
    b = _resolve(broadcastToID)
    if b is None:
        raise TgiError("Invalid broadcastTo handle", TgiFaultCode.INVALID_ID)
    br = _ns(value=bankRef)
    if not hasattr(b, "bank_ref"):
        b.bank_ref = []  # type: ignore[attr-defined]
    b.bank_ref.append(br)  # type: ignore[attr-defined]
    register_parent(br, b, ("bank_ref",), "list")
    return get_handle(br)


def addBroadcastToRegisterFileRef(broadcastToID: str, registerFileRef: str) -> str:
    """Add registerFileRef (F.7.74.4)."""
    b = _resolve(broadcastToID)
    if b is None:
        raise TgiError("Invalid broadcastTo handle", TgiFaultCode.INVALID_ID)
    rf = _ns(value=registerFileRef)
    if not hasattr(b, "register_file_ref"):
        b.register_file_ref = []  # type: ignore[attr-defined]
    b.register_file_ref.append(rf)  # type: ignore[attr-defined]
    register_parent(rf, b, ("register_file_ref",), "list")
    return get_handle(rf)


def addEnumeratedValuesFieldEnumeratedValue(enumeratedValuesID: str, name: str, value: str) -> str:
    """Add enumeratedValue (F.7.74.5)."""
    evs = _resolve(enumeratedValuesID)
    if evs is None:
        raise TgiError("Invalid enumeratedValues handle", TgiFaultCode.INVALID_ID)
    ev = _ns(name=name, value=_ns(value=_coerce_int(value)))
    if not hasattr(evs, "enumerated_value"):
        evs.enumerated_value = []  # type: ignore[attr-defined]
    evs.enumerated_value.append(ev)  # type: ignore[attr-defined]
    register_parent(ev, evs, ("enumerated_value",), "list")
    return get_handle(ev)


def addFieldRefIndex(fieldRefID: str, value: str) -> str:
    """Add index to fieldRef (F.7.74.6)."""
    fr = _resolve(fieldRefID)
    if fr is None:
        raise TgiError("Invalid fieldRef handle", TgiFaultCode.INVALID_ID)
    idx = _ns(value=_coerce_int(value))
    if not hasattr(fr, "index"):
        fr.index = []  # type: ignore[attr-defined]
    fr.index.append(idx)  # type: ignore[attr-defined]
    register_parent(idx, fr, ("index",), "list")
    return get_handle(idx)


def addRegisterAlternateRegister(
    registerID: str,
    name: str,
    modeRef: str,
    priority: int,
    fieldName: str,
    fieldOffset: str,
    fieldWidth: str,
) -> str:
    """Add alternateRegister (F.7.74.7)."""
    r = _resolve(registerID)
    if r is None:
        raise TgiError("Invalid register handle", TgiFaultCode.INVALID_ID)
    mr = _ns(value=modeRef, priority=priority)
    fld = _ns(
        name=fieldName,
        bit_offset=_ns(value=_coerce_int(fieldOffset)),
        bit_width=_ns(value=_coerce_int(fieldWidth)),
    )
    ar = _ns(name=name, mode_ref=[mr], field=[fld])
    if not hasattr(r, "alternate_register"):
        r.alternate_register = []  # type: ignore[attr-defined]
    r.alternate_register.append(ar)  # type: ignore[attr-defined]
    register_parent(ar, r, ("alternate_register",), "list")
    register_parent(mr, ar, ("mode_ref",), "list")
    register_parent(fld, ar, ("field",), "list")
    return get_handle(ar)


def addRegisterField(registerID: str, name: str, offset: str, width: str) -> str:
    """Add field to register (F.7.74.8)."""
    r = _resolve(registerID)
    if r is None:
        raise TgiError("Invalid register handle", TgiFaultCode.INVALID_ID)
    f = _ns(
        name=name,
        bit_offset=_ns(value=_coerce_int(offset)),
        bit_width=_ns(value=_coerce_int(width)),
    )
    if not hasattr(r, "field"):
        r.field = []  # type: ignore[attr-defined]
    r.field.append(f)  # type: ignore[attr-defined]
    register_parent(f, r, ("field",), "list")
    return get_handle(f)


def addRegisterFieldReset(registerFieldID: str, value: str) -> str:
    """Add reset to register field (F.7.74.9)."""
    f = _resolve(registerFieldID)
    if f is None:
        raise TgiError("Invalid register field handle", TgiFaultCode.INVALID_ID)
    rst = _ns(value=_ns(value=_coerce_int(value)))
    if not hasattr(f, "reset"):
        f.reset = []  # type: ignore[attr-defined]
    f.reset.append(rst)  # type: ignore[attr-defined]
    register_parent(rst, f, ("reset",), "list")
    return get_handle(rst)


def addRegisterRefIndex(registerRefID: str, value: str) -> str:
    """Add index to registerRef (F.7.74.10)."""
    rr = _resolve(registerRefID)
    if rr is None:
        raise TgiError("Invalid registerRef handle", TgiFaultCode.INVALID_ID)
    idx = _ns(value=_coerce_int(value))
    if not hasattr(rr, "index"):
        rr.index = []  # type: ignore[attr-defined]
    rr.index.append(idx)  # type: ignore[attr-defined]
    register_parent(idx, rr, ("index",), "list")
    return get_handle(idx)

# Removes


def removeAliasOfAlternateRegisterRef(aliasOfID: str) -> bool:
    """Remove alternateRegisterRef (F.7.74.11)."""
    a = _resolve(aliasOfID)
    if a is None:
        raise TgiError("Invalid aliasOf handle", TgiFaultCode.INVALID_ID)
    if getattr(a, "alternate_register_ref", None) is None:
        return False
    a.alternate_register_ref = None  # type: ignore[attr-defined]
    return True


def removeAliasOfRegisterRef(aliasOfID: str) -> bool:
    """Remove registerRef (F.7.74.12)."""
    a = _resolve(aliasOfID)
    if a is None:
        raise TgiError("Invalid aliasOf handle", TgiFaultCode.INVALID_ID)
    if getattr(a, "register_ref", None) is None:
        return False
    a.register_ref = None  # type: ignore[attr-defined]
    return True


def removeAlternateRegisterField(regFieldID: str) -> bool:
    """Remove alternate register field (F.7.74.13)."""
    return detach_child_by_handle(regFieldID)


def removeAlternateRegisterTypeIdentifier(alternateRegisterID: str) -> bool:
    """Remove typeIdentifier (F.7.74.14)."""
    ar = _resolve(alternateRegisterID)
    if ar is None:
        raise TgiError("Invalid alternateRegister handle", TgiFaultCode.INVALID_ID)
    if getattr(ar, "type_identifier", None) is None:
        return False
    ar.type_identifier = None  # type: ignore[attr-defined]
    return True


def removeAlternateRegisterVolatility(alternateRegisterID: str) -> bool:
    """Remove volatility (F.7.74.15)."""
    ar = _resolve(alternateRegisterID)
    if ar is None:
        raise TgiError("Invalid alternateRegister handle", TgiFaultCode.INVALID_ID)
    if getattr(ar, "volatile", None) is None:
        return False
    ar.volatile = None  # type: ignore[attr-defined]
    return True


def removeAlternaterRegisterModeRef(modeRefID: str) -> bool:
    """Remove modeRef element (F.7.74.16)."""
    return detach_child_by_handle(modeRefID)


def removeBroadcastToAddressBlockRef(broadcastToID: str) -> bool:
    """Remove addressBlockRef (F.7.74.17)."""
    b = _resolve(broadcastToID)
    if b is None:
        raise TgiError("Invalid broadcastTo handle", TgiFaultCode.INVALID_ID)
    if getattr(b, "address_block_ref", None) is None:
        return False
    b.address_block_ref = None  # type: ignore[attr-defined]
    return True


def removeBroadcastToAlternateRegisterRef(broadcastToID: str) -> bool:
    """Remove alternateRegisterRef (F.7.74.18)."""
    b = _resolve(broadcastToID)
    if b is None:
        raise TgiError("Invalid broadcastTo handle", TgiFaultCode.INVALID_ID)
    if getattr(b, "alternate_register_ref", None) is None:
        return False
    b.alternate_register_ref = None  # type: ignore[attr-defined]
    return True


def removeBroadcastToBankRef(bankRefID: str) -> bool:
    """Remove bankRef by element handle (F.7.74.19)."""
    return detach_child_by_handle(bankRefID)


def removeBroadcastToMemoryMapRef(broadcastToID: str) -> bool:
    """Remove memoryMapRef (F.7.74.20)."""
    b = _resolve(broadcastToID)
    if b is None:
        raise TgiError("Invalid broadcastTo handle", TgiFaultCode.INVALID_ID)
    if getattr(b, "memory_map_ref", None) is None:
        return False
    b.memory_map_ref = None  # type: ignore[attr-defined]
    return True


def removeBroadcastToRegisterFileRef(registerRefID: str) -> bool:
    """Remove registerFileRef (F.7.74.21)."""
    return detach_child_by_handle(registerRefID)


def removeBroadcastToRegisterRef(registerRefID: str) -> bool:
    """Remove registerRef (F.7.74.22)."""
    return detach_child_by_handle(registerRefID)
