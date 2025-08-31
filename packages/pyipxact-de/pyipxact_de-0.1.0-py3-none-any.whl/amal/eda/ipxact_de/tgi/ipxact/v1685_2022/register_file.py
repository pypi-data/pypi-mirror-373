"""Register file category TGI functions (IEEE 1685-2022).

Implements BASE (F.7.75) and EXTENDED (F.7.76) Register file functions. Only
2022 standard APIs defined by Annex F are exported; no vendor extensions or
legacy names are exposed. BASE getters follow the tolerant semantics used in
other categories: invalid handles return neutral values (``None`` / empty
lists) instead of raising, enabling generators to probe. EXTENDED mutators
raise :class:`TgiError` with :class:`TgiFaultCode.INVALID_ID` for invalid
handles and :class:`TgiFaultCode.INVALID_ARGUMENT` for semantic violations.

This module purposefully contains lightweight logic; deeper schema validation
(e.g. uniqueness, overlapping address ranges) can be layered later once the
core API surface is stable.
"""
# ruff: noqa: I001
from collections.abc import Iterable
from typing import Any

from org.accellera.ipxact.v1685_2022 import RegisterFile

from .core import (
    TgiError,
    TgiFaultCode,
    get_handle,
    resolve_handle,
    register_parent,
    detach_child_by_handle,
)

__all__ = [
    # BASE (F.7.75)
    "getAliasOfRegisterFileRefByNames",
    "getAliasOfRegisterFileRefIDs",
    "getRegisterFileAccessHandleIDs",
    "getRegisterFileAccessPolicyIDs",
    "getRegisterFileAddressOffset",
    "getRegisterFileAddressOffsetExpression",
    "getRegisterFileArrayID",
    "getRegisterFileRange",
    "getRegisterFileRangeExpression",
    "getRegisterFileRangeID",
    "getRegisterFileRefIndexIDs",
    "getRegisterFileRegisterFileDefinitionRefByExternalTypeDefID",
    "getRegisterFileRegisterFileDefinitionRefByID",
    "getRegisterFileRegisterFileDefinitionRefByName",
    "getRegisterFileRegisterFileDefinitionRefID",
    "getRegisterFileRegisterFileIDs",
    "getRegisterFileRegisterIDs",
    "getRegisterFileTypeIdentifier",
    # EXTENDED (F.7.76)
    "addAliasOfRegisterFileRef",
    "addRegisterFileDefinitionRegisterFile",
    "addRegisterFileRefIndex",
    "addRegisterFileRegister",
    "removeAliasOfRegisterFileRef",
    "removeRegisterFileAccessHandle",
    "removeRegisterFileRefIndex",
    "removeRegisterFileRegister",
    "removeRegisterFileRegisterFile",
    "removeRegisterFileTypeIdentifier",
    "setRegisterFileAddressOffset",
    "setRegisterFileRange",
    "setRegisterFileRegisterFileDefinitionRef",
    "setRegisterFileTypeIdentifier",
]


# ---------------------------------------------------------------------------
# Helpers (non-spec)
# ---------------------------------------------------------------------------

def _resolve(registerFileID: str) -> RegisterFile | None:
    obj = resolve_handle(registerFileID)
    return obj if isinstance(obj, RegisterFile) else None


def _list_ids(items: Iterable[Any]) -> list[str]:
    return [get_handle(i) for i in items]


def _maybe_expr(node: Any) -> tuple[Any | None, str | None, str | None]:
    """Return (value, expression, idHandle) triple for value-with-expression nodes.

    Many numeric/string simple value elements in IP-XACT can originate from
    a value, an expression or carry an ID handle. We normalise access here.
    """
    if node is None:
        return (None, None, None)
    value_obj = getattr(node, "value", None)
    expr = getattr(value_obj, "expression", None) if value_obj is not None else None
    val = getattr(value_obj, "value", None) if value_obj is not None else None
    return (val, expr, get_handle(node))


# ---------------------------------------------------------------------------
# BASE (F.7.75)
# ---------------------------------------------------------------------------

def getAliasOfRegisterFileRefByNames(
    registerFileID: str,
    vendor: str,
    library: str,
    name: str,
    version: str,
) -> str | None:
    """Return handle of aliasOf registerFile reference matching VLNV names.

    Section: F.7.75.1. Returns ``None`` if not found or handle invalid.
    """
    rf = _resolve(registerFileID)
    alias_of = getattr(rf, "alias_of", None) if rf is not None else None
    if alias_of is None:
        return None
    if (
        getattr(alias_of, "vendor", None),
        getattr(alias_of, "library", None),
        getattr(alias_of, "name", None),
        getattr(alias_of, "version", None),
    ) == (vendor, library, name, version):
        return get_handle(alias_of)
    return None


def getAliasOfRegisterFileRefIDs(registerFileID: str) -> list[str]:
    """Return list of aliasOf register file reference handles (0 or 1). F.7.75.2."""
    rf = _resolve(registerFileID)
    alias_of = getattr(rf, "alias_of", None) if rf is not None else None
    if alias_of is None:
        return []
    return [get_handle(alias_of)]


def getRegisterFileAccessHandleIDs(registerFileID: str) -> list[str]:  # F.7.75.3
    rf = _resolve(registerFileID)
    if rf is None:
        return []
    ahs = getattr(rf, "access_handles", None)
    if ahs is None:
        return []
    return _list_ids(getattr(ahs, "access_handle", []))


def getRegisterFileAccessPolicyIDs(registerFileID: str) -> list[str]:  # F.7.75.4
    rf = _resolve(registerFileID)
    if rf is None:
        return []
    aps = getattr(rf, "access_policies", None)
    if aps is None:
        return []
    return _list_ids(getattr(aps, "access_policy", []))


def getRegisterFileAddressOffset(registerFileID: str) -> int | None:  # F.7.75.5
    rf = _resolve(registerFileID)
    if rf is None:
        return None
    val, _, _hid = _maybe_expr(getattr(rf, "address_offset", None))
    return val


def getRegisterFileAddressOffsetExpression(registerFileID: str) -> str | None:  # F.7.75.6
    rf = _resolve(registerFileID)
    if rf is None:
        return None
    _, expr, _ = _maybe_expr(getattr(rf, "address_offset", None))
    return expr


def getRegisterFileArrayID(registerFileID: str) -> str | None:  # F.7.75.7
    rf = _resolve(registerFileID)
    if rf is None:
        return None
    arr = getattr(rf, "array", None)
    return None if arr is None else get_handle(arr)


def getRegisterFileRange(registerFileID: str) -> int | None:  # F.7.75.8
    rf = _resolve(registerFileID)
    if rf is None:
        return None
    val, _, _ = _maybe_expr(getattr(rf, "range", None))
    return val


def getRegisterFileRangeExpression(registerFileID: str) -> str | None:  # F.7.75.9
    rf = _resolve(registerFileID)
    if rf is None:
        return None
    _, expr, _ = _maybe_expr(getattr(rf, "range", None))
    return expr


def getRegisterFileRangeID(registerFileID: str) -> str | None:  # F.7.75.10
    rf = _resolve(registerFileID)
    if rf is None:
        return None
    _, _, hid = _maybe_expr(getattr(rf, "range", None))
    return hid


def getRegisterFileRefIndexIDs(registerFileID: str) -> list[str]:  # F.7.75.11
    rf = _resolve(registerFileID)
    if rf is None:
        return []
    rfi = getattr(rf, "ref_indices", None)
    if rfi is None:
        return []
    return _list_ids(getattr(rfi, "ref_index", []))


def getRegisterFileRegisterFileDefinitionRefByExternalTypeDefID(
    registerFileID: str,
    externalTypeDefID: str,
) -> str | None:  # F.7.75.12
    rf = _resolve(registerFileID)
    if rf is None:
        return None
    rfr = getattr(rf, "register_file_definition_ref", None)
    if rfr is None:
        return None
    ext = getattr(rfr, "external_type_def", None)
    if ext is None:
        return None
    return get_handle(rfr) if get_handle(ext) == externalTypeDefID else None


def getRegisterFileRegisterFileDefinitionRefByID(registerFileID: str, byID: str) -> str | None:  # F.7.75.13
    rf = _resolve(registerFileID)
    if rf is None:
        return None
    rfr = getattr(rf, "register_file_definition_ref", None)
    if rfr is None:
        return None
    return get_handle(rfr) if get_handle(rfr) == byID else None


def getRegisterFileRegisterFileDefinitionRefByName(registerFileID: str, name: str) -> str | None:  # F.7.75.14
    rf = _resolve(registerFileID)
    if rf is None:
        return None
    rfr = getattr(rf, "register_file_definition_ref", None)
    if rfr is None:
        return None
    n = getattr(rfr, "name", None)
    return get_handle(rfr) if n == name else None


def getRegisterFileRegisterFileDefinitionRefID(registerFileID: str) -> str | None:  # F.7.75.15
    rf = _resolve(registerFileID)
    if rf is None:
        return None
    rfr = getattr(rf, "register_file_definition_ref", None)
    return None if rfr is None else get_handle(rfr)


def getRegisterFileRegisterFileIDs(registerFileID: str) -> list[str]:  # F.7.75.16
    rf = _resolve(registerFileID)
    if rf is None:
        return []
    return _list_ids(getattr(rf, "register_file", []))


def getRegisterFileRegisterIDs(registerFileID: str) -> list[str]:  # F.7.75.17
    rf = _resolve(registerFileID)
    if rf is None:
        return []
    return _list_ids(getattr(rf, "register", []))


def getRegisterFileTypeIdentifier(registerFileID: str) -> str | None:  # F.7.75.18
    rf = _resolve(registerFileID)
    if rf is None:
        return None
    ti = getattr(rf, "type_identifier", None)
    return getattr(ti, "value", None) if ti is not None else None


# ---------------------------------------------------------------------------
# EXTENDED (F.7.76)
# ---------------------------------------------------------------------------

def addAliasOfRegisterFileRef(registerFileID: str, vlnv: tuple[str, str, str, str]) -> str:
    """Create/replace aliasOf registerFile reference. Section F.7.76.1."""
    rf = _resolve(registerFileID)
    if rf is None:
        raise TgiError("Invalid registerFile handle", TgiFaultCode.INVALID_ID)
    from org.accellera.ipxact.v1685_2022.library_ref_type import LibraryRefType

    ref = LibraryRefType(vendor=vlnv[0], library=vlnv[1], name=vlnv[2], version=vlnv[3])
    rf.alias_of = ref  # type: ignore[attr-defined]
    register_parent(ref, rf, ("alias_of",), "single")  # type: ignore[attr-defined]
    return get_handle(ref)


def addRegisterFileDefinitionRegisterFile(registerFileDefinitionRefID: str, name: str) -> str:
    """Add a contained registerFile to a registerFileDefinition ref target. F.7.76.2.

    Because schema mapping for definition vs instance may differ, we treat the
    provided handle as pointing at a RegisterFile acting as definition root.
    """
    rf = _resolve(registerFileDefinitionRefID)
    if rf is None:
        raise TgiError("Invalid registerFileDefinitionRefID", TgiFaultCode.INVALID_ID)
    child = RegisterFile(name=name)
    rf.register_file.append(child)  # type: ignore[attr-defined]
    register_parent(child, rf, ("register_file",), "list")
    return get_handle(child)


def addRegisterFileRefIndex(registerFileID: str, value: int) -> str:  # F.7.76.3
    rf = _resolve(registerFileID)
    if rf is None:
        raise TgiError("Invalid registerFile handle", TgiFaultCode.INVALID_ID)
    from types import SimpleNamespace

    if getattr(rf, "ref_indices", None) is None:
        rf.ref_indices = SimpleNamespace(ref_index=[])  # type: ignore[attr-defined]
    idx = SimpleNamespace(value=value)
    rf.ref_indices.ref_index.append(idx)  # type: ignore[attr-defined]
    register_parent(idx, rf, ("ref_indices",), "list")
    return get_handle(idx)


def addRegisterFileRegister(registerFileID: str, name: str) -> str:  # F.7.76.4
    rf = _resolve(registerFileID)
    if rf is None:
        raise TgiError("Invalid registerFile handle", TgiFaultCode.INVALID_ID)
    # Import Register type; fallback to simple namespace if not present in schema
    try:  # pragma: no cover - defensive
        from org.accellera.ipxact.v1685_2022 import Register  # type: ignore
        reg = Register(name=name)  # type: ignore[call-arg]
    except Exception:  # pragma: no cover - fallback
        from types import SimpleNamespace
        reg = SimpleNamespace(name=name)
    rf.register.append(reg)  # type: ignore[attr-defined]
    register_parent(reg, rf, ("register",), "list")
    return get_handle(reg)


def removeAliasOfRegisterFileRef(aliasOfRegisterFileRefID: str) -> bool:  # F.7.76.5
    obj = resolve_handle(aliasOfRegisterFileRefID)
    if obj is None:
        raise TgiError("Invalid aliasOfRegisterFileRefID", TgiFaultCode.INVALID_ID)
    return detach_child_by_handle(aliasOfRegisterFileRefID)


def removeRegisterFileAccessHandle(registerFileAccessHandleID: str) -> bool:  # F.7.76.6
    if resolve_handle(registerFileAccessHandleID) is None:
        raise TgiError("Invalid registerFileAccessHandleID", TgiFaultCode.INVALID_ID)
    return detach_child_by_handle(registerFileAccessHandleID)


def removeRegisterFileRefIndex(registerFileRefIndexID: str) -> bool:  # F.7.76.7
    if resolve_handle(registerFileRefIndexID) is None:
        raise TgiError("Invalid registerFileRefIndexID", TgiFaultCode.INVALID_ID)
    return detach_child_by_handle(registerFileRefIndexID)


def removeRegisterFileRegister(registerFileRegisterID: str) -> bool:  # F.7.76.8
    if resolve_handle(registerFileRegisterID) is None:
        raise TgiError("Invalid registerFileRegisterID", TgiFaultCode.INVALID_ID)
    return detach_child_by_handle(registerFileRegisterID)


def removeRegisterFileRegisterFile(registerFileRegisterFileID: str) -> bool:  # F.7.76.9
    if resolve_handle(registerFileRegisterFileID) is None:
        raise TgiError("Invalid registerFileRegisterFileID", TgiFaultCode.INVALID_ID)
    return detach_child_by_handle(registerFileRegisterFileID)


def removeRegisterFileTypeIdentifier(registerFileID: str) -> bool:  # F.7.76.10
    rf = _resolve(registerFileID)
    if rf is None:
        raise TgiError("Invalid registerFileID", TgiFaultCode.INVALID_ID)
    if getattr(rf, "type_identifier", None) is None:
        return True
    rf.type_identifier = None  # type: ignore[attr-defined]
    return True


def setRegisterFileAddressOffset(
    registerFileID: str,
    value: int | None = None,
    expression: str | None = None,
) -> bool:  # F.7.76.11
    rf = _resolve(registerFileID)
    if rf is None:
        raise TgiError("Invalid registerFileID", TgiFaultCode.INVALID_ID)
    from types import SimpleNamespace

    if value is None and expression is None:
        raise TgiError("Either value or expression required", TgiFaultCode.INVALID_ARGUMENT)
    rf.address_offset = SimpleNamespace(value=SimpleNamespace(value=value, expression=expression))  # type: ignore[attr-defined]
    register_parent(rf.address_offset, rf, ("address_offset",), "single")  # type: ignore[attr-defined]
    return True


def setRegisterFileRange(
    registerFileID: str,
    value: int | None = None,
    expression: str | None = None,
) -> bool:  # F.7.76.12
    rf = _resolve(registerFileID)
    if rf is None:
        raise TgiError("Invalid registerFileID", TgiFaultCode.INVALID_ID)
    from types import SimpleNamespace

    if value is None and expression is None:
        raise TgiError("Either value or expression required", TgiFaultCode.INVALID_ARGUMENT)
    rf.range = SimpleNamespace(value=SimpleNamespace(value=value, expression=expression))  # type: ignore[attr-defined]
    register_parent(rf.range, rf, ("range",), "single")  # type: ignore[attr-defined]
    return True


def setRegisterFileRegisterFileDefinitionRef(
    registerFileID: str,
    name: str | None = None,
    vlnv: tuple[str, str, str, str] | None = None,
) -> bool:  # F.7.76.13
    rf = _resolve(registerFileID)
    if rf is None:
        raise TgiError("Invalid registerFileID", TgiFaultCode.INVALID_ID)
    if name is None and vlnv is None:
        raise TgiError("Either name or vlnv required", TgiFaultCode.INVALID_ARGUMENT)
    from types import SimpleNamespace

    if vlnv is not None:
        from org.accellera.ipxact.v1685_2022.library_ref_type import LibraryRefType

        ref = LibraryRefType(vendor=vlnv[0], library=vlnv[1], name=vlnv[2], version=vlnv[3])
    else:
        ref = SimpleNamespace(name=name)
    rf.register_file_definition_ref = ref  # type: ignore[attr-defined]
    register_parent(ref, rf, ("register_file_definition_ref",), "single")
    return True


def setRegisterFileTypeIdentifier(registerFileID: str, typeIdentifier: str) -> bool:  # F.7.76.14
    rf = _resolve(registerFileID)
    if rf is None:
        raise TgiError("Invalid registerFileID", TgiFaultCode.INVALID_ID)
    from types import SimpleNamespace

    rf.type_identifier = SimpleNamespace(value=typeIdentifier)  # type: ignore[attr-defined]
    register_parent(rf.type_identifier, rf, ("type_identifier",), "single")  # type: ignore[attr-defined]
    return True

