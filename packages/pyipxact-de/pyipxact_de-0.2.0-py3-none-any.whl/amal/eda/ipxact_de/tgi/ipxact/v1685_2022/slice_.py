"""Slice category TGI functions (IEEE 1685-2022).

Named ``slice_`` to avoid clashing with Python's built-in ``slice``. Implements
BASE (F.7.77) and EXTENDED (F.7.78) Slice functions. BASE getters are tolerant:
invalid handles produce neutral results (``None`` / empty list) rather than
raising, consistent with other category modules. EXTENDED mutators raise
``TgiError`` with ``TgiFaultCode.INVALID_ID`` for invalid handles and
``TgiFaultCode.INVALID_ARGUMENT`` for semantic issues.

The underlying schema objects for slice relationships (e.g. fieldSlice,
portSlice, memoryMapRef, etc.) are represented minimally using existing schema
objects when available or lightweight namespaces when not yet present.
"""
# ruff: noqa: I001
from types import SimpleNamespace
from typing import Any

from .core import (
    TgiError,
    TgiFaultCode,
    resolve_handle,
    get_handle,
    register_parent,
    detach_child_by_handle,
)

__all__ = [
    # BASE (F.7.77)
    "getFieldSliceAddressBlockRefByID",
    "getFieldSliceAddressBlockRefByName",
    "getFieldSliceAddressBlockRefID",
    "getFieldSliceAddressSpaceRefByID",
    "getFieldSliceAddressSpaceRefByName",
    "getFieldSliceAddressSpaceRefID",
    "getFieldSliceAlternateRegisterRefByID",
    "getFieldSliceAlternateRegisterRefByName",
    "getFieldSliceAlternateRegisterRefID",
    "getFieldSliceBankRefByNames",
    "getFieldSliceBankRefIDs",
    "getFieldSliceFieldRefByName",
    "getFieldSliceFieldRefID",
    "getFieldSliceMemoryMapRefByID",
    "getFieldSliceMemoryMapRefByName",
    "getFieldSliceMemoryMapRefID",
    "getFieldSliceMemoryRemapRefByID",
    "getFieldSliceMemoryRemapRefByName",
    "getFieldSliceMemoryRemapRefID",
    "getFieldSliceRange",
    "getFieldSliceRangeLeftID",
    "getFieldSliceRangeRightID",
    # EXTENDED (F.7.78)
    "addFieldSliceBankRef",
    "addFieldSliceRegisterFileRef",
    "addModeFieldSlice",
    "addModePortSlice",
    "addPortSliceSubPortReference",
    "addSlicePathSegment",
    "removeFieldSliceAlternateRegisterRef",
    "removeFieldSliceBankRef",
    "removeFieldSliceMemoryRemapRef",
    "removeFieldSliceRange",
    "removeFieldSliceRegisterFileRef",
    "removeLocationSlice",
    "removeModeFieldSlice",
    "removeModePortSlice",
    "removePortSlicePartSelect",
    "removePortSliceSubPortReference",
    "removeSlicePathSegment",
    "removeSliceRange",
    "setFieldSliceAddressBlockRef",
    "setFieldSliceAddressSpaceRef",
    "setFieldSliceAlternateRegisterRef",
    "setFieldSliceFieldRef",
    "setFieldSliceMemoryMapRef",
    "setFieldSliceMemoryRemapRef",
    "setFieldSliceRange",
    "setFieldSliceRegisterRef",
    "setPortSlicePartSelect",
    "setPortSlicePortRef",
    "setSliceRange",
]


# ---------------------------------------------------------------------------
# Helpers (non-spec)
# ---------------------------------------------------------------------------

def _resolve(objID: str) -> Any | None:
    return resolve_handle(objID)


def _maybe(obj: Any, attr: str) -> Any | None:
    return getattr(obj, attr, None) if obj is not None else None


def _ensure_slice_parent(sliceID: str) -> Any:
    sl = _resolve(sliceID)
    if sl is None:
        raise TgiError("Invalid slice handle", TgiFaultCode.INVALID_ID)
    return sl


def _value_expr(node: Any) -> tuple[Any | None, str | None, str | None]:
    if node is None:
        return (None, None, None)
    v = getattr(node, "value", None)
    expr = getattr(v, "expression", None) if v is not None else None
    val = getattr(v, "value", None) if v is not None else None
    return (val, expr, get_handle(node))


# ---------------------------------------------------------------------------
# BASE (F.7.77)
# ---------------------------------------------------------------------------

def getFieldSliceAddressBlockRefByID(fieldSliceID: str, addressBlockID: str) -> str | None:  # F.7.77.1
    sl = _resolve(fieldSliceID)
    abr = _maybe(sl, "address_block_ref")
    if abr is None:
        return None
    return get_handle(abr) if get_handle(abr) == addressBlockID else None


def getFieldSliceAddressBlockRefByName(fieldSliceID: str, name: str) -> str | None:  # F.7.77.2
    sl = _resolve(fieldSliceID)
    abr = _maybe(sl, "address_block_ref")
    if abr is None:
        return None
    return get_handle(abr) if getattr(abr, "name", None) == name else None


def getFieldSliceAddressBlockRefID(fieldSliceID: str) -> str | None:  # F.7.77.3
    sl = _resolve(fieldSliceID)
    abr = _maybe(sl, "address_block_ref")
    return None if abr is None else get_handle(abr)


def getFieldSliceAddressSpaceRefByID(fieldSliceID: str, addressSpaceID: str) -> str | None:  # F.7.77.4
    sl = _resolve(fieldSliceID)
    asr = _maybe(sl, "address_space_ref")
    if asr is None:
        return None
    return get_handle(asr) if get_handle(asr) == addressSpaceID else None


def getFieldSliceAddressSpaceRefByName(fieldSliceID: str, name: str) -> str | None:  # F.7.77.5
    sl = _resolve(fieldSliceID)
    asr = _maybe(sl, "address_space_ref")
    if asr is None:
        return None
    return get_handle(asr) if getattr(asr, "name", None) == name else None


def getFieldSliceAddressSpaceRefID(fieldSliceID: str) -> str | None:  # F.7.77.6
    sl = _resolve(fieldSliceID)
    asr = _maybe(sl, "address_space_ref")
    return None if asr is None else get_handle(asr)


def getFieldSliceAlternateRegisterRefByID(fieldSliceID: str, altRegisterID: str) -> str | None:  # F.7.77.7
    sl = _resolve(fieldSliceID)
    arr = _maybe(sl, "alternate_register_ref")
    if arr is None:
        return None
    return get_handle(arr) if get_handle(arr) == altRegisterID else None


def getFieldSliceAlternateRegisterRefByName(fieldSliceID: str, name: str) -> str | None:  # F.7.77.8
    sl = _resolve(fieldSliceID)
    arr = _maybe(sl, "alternate_register_ref")
    if arr is None:
        return None
    return get_handle(arr) if getattr(arr, "name", None) == name else None


def getFieldSliceAlternateRegisterRefID(fieldSliceID: str) -> str | None:  # F.7.77.9
    sl = _resolve(fieldSliceID)
    arr = _maybe(sl, "alternate_register_ref")
    return None if arr is None else get_handle(arr)


def getFieldSliceBankRefByNames(
    fieldSliceID: str,
    vendor: str,
    library: str,
    name: str,
    version: str,
) -> str | None:  # F.7.77.10
    sl = _resolve(fieldSliceID)
    banks = getattr(sl, "bank_ref", []) if sl is not None else []
    for b in banks:
        if (
            getattr(b, "vendor", None),
            getattr(b, "library", None),
            getattr(b, "name", None),
            getattr(b, "version", None),
        ) == (vendor, library, name, version):
            return get_handle(b)
    return None


def getFieldSliceBankRefIDs(fieldSliceID: str) -> list[str]:  # F.7.77.11
    sl = _resolve(fieldSliceID)
    if sl is None:
        return []
    return [get_handle(b) for b in getattr(sl, "bank_ref", [])]


def getFieldSliceFieldRefByName(fieldSliceID: str, name: str) -> str | None:  # F.7.77.12
    sl = _resolve(fieldSliceID)
    fr = _maybe(sl, "field_ref")
    if fr is None:
        return None
    return get_handle(fr) if getattr(fr, "name", None) == name else None


def getFieldSliceFieldRefID(fieldSliceID: str) -> str | None:  # F.7.77.13
    sl = _resolve(fieldSliceID)
    fr = _maybe(sl, "field_ref")
    return None if fr is None else get_handle(fr)


def getFieldSliceMemoryMapRefByID(fieldSliceID: str, memoryMapID: str) -> str | None:  # F.7.77.14
    sl = _resolve(fieldSliceID)
    mm = _maybe(sl, "memory_map_ref")
    if mm is None:
        return None
    return get_handle(mm) if get_handle(mm) == memoryMapID else None


def getFieldSliceMemoryMapRefByName(fieldSliceID: str, name: str) -> str | None:  # F.7.77.15
    sl = _resolve(fieldSliceID)
    mm = _maybe(sl, "memory_map_ref")
    if mm is None:
        return None
    return get_handle(mm) if getattr(mm, "name", None) == name else None


def getFieldSliceMemoryMapRefID(fieldSliceID: str) -> str | None:  # F.7.77.16
    sl = _resolve(fieldSliceID)
    mm = _maybe(sl, "memory_map_ref")
    return None if mm is None else get_handle(mm)


def getFieldSliceMemoryRemapRefByID(fieldSliceID: str, memoryRemapID: str) -> str | None:  # F.7.77.17
    sl = _resolve(fieldSliceID)
    mr = _maybe(sl, "memory_remap_ref")
    if mr is None:
        return None
    return get_handle(mr) if get_handle(mr) == memoryRemapID else None


def getFieldSliceMemoryRemapRefByName(fieldSliceID: str, name: str) -> str | None:  # F.7.77.18
    sl = _resolve(fieldSliceID)
    mr = _maybe(sl, "memory_remap_ref")
    if mr is None:
        return None
    return get_handle(mr) if getattr(mr, "name", None) == name else None


def getFieldSliceMemoryRemapRefID(fieldSliceID: str) -> str | None:  # F.7.77.19
    sl = _resolve(fieldSliceID)
    mr = _maybe(sl, "memory_remap_ref")
    return None if mr is None else get_handle(mr)


def getFieldSliceRange(fieldSliceID: str) -> int | None:  # F.7.77.20
    sl = _resolve(fieldSliceID)
    rng = _maybe(sl, "range")
    val, _, _ = _value_expr(rng)
    return val


def getFieldSliceRangeLeftID(fieldSliceID: str) -> str | None:  # F.7.77.21
    sl = _resolve(fieldSliceID)
    rng = _maybe(sl, "range")
    left = getattr(rng, "left", None) if rng is not None else None
    return None if left is None else get_handle(left)


def getFieldSliceRangeRightID(fieldSliceID: str) -> str | None:  # F.7.77.22
    sl = _resolve(fieldSliceID)
    rng = _maybe(sl, "range")
    right = getattr(rng, "right", None) if rng is not None else None
    return None if right is None else get_handle(right)


# ---------------------------------------------------------------------------
# EXTENDED (F.7.78)
# ---------------------------------------------------------------------------

def addFieldSliceBankRef(fieldSliceID: str, vlnv: tuple[str, str, str, str]) -> str:  # F.7.78.1
    sl = _ensure_slice_parent(fieldSliceID)
    from org.accellera.ipxact.v1685_2022.library_ref_type import LibraryRefType

    if getattr(sl, "bank_ref", None) is None:
        sl.bank_ref = []  # type: ignore[attr-defined]
    ref = LibraryRefType(
        vendor=vlnv[0], library=vlnv[1], name=vlnv[2], version=vlnv[3]
    )
    sl.bank_ref.append(ref)  # type: ignore[attr-defined]
    register_parent(ref, sl, ("bank_ref",), "list")
    return get_handle(ref)


def addFieldSliceRegisterFileRef(fieldSliceID: str, name: str) -> str:  # F.7.78.2
    sl = _ensure_slice_parent(fieldSliceID)
    rfref = SimpleNamespace(name=name)
    sl.register_file_ref = rfref  # type: ignore[attr-defined]
    register_parent(rfref, sl, ("register_file_ref",), "single")
    return get_handle(rfref)


def addModeFieldSlice(modeID: str, fieldSliceID: str) -> bool:  # F.7.78.3
    mode = _resolve(modeID)
    sl = _resolve(fieldSliceID)
    if mode is None or sl is None:
        raise TgiError("Invalid mode or slice handle", TgiFaultCode.INVALID_ID)
    mode.field_slice = sl  # type: ignore[attr-defined]
    register_parent(sl, mode, ("field_slice",), "single")
    return True


def addModePortSlice(modeID: str, portSliceID: str) -> bool:  # F.7.78.4
    mode = _resolve(modeID)
    ps = _resolve(portSliceID)
    if mode is None or ps is None:
        raise TgiError("Invalid mode or portSlice handle", TgiFaultCode.INVALID_ID)
    mode.port_slice = ps  # type: ignore[attr-defined]
    register_parent(ps, mode, ("port_slice",), "single")
    return True


def addPortSliceSubPortReference(portSliceID: str, subPortName: str) -> str:  # F.7.78.5
    ps = _ensure_slice_parent(portSliceID)
    sub = SimpleNamespace(name=subPortName)
    if getattr(ps, "sub_port_reference", None) is None:
        ps.sub_port_reference = []  # type: ignore[attr-defined]
    ps.sub_port_reference.append(sub)  # type: ignore[attr-defined]
    register_parent(sub, ps, ("sub_port_reference",), "list")
    return get_handle(sub)


def addSlicePathSegment(sliceID: str, segment: str) -> str:  # F.7.78.6
    sl = _ensure_slice_parent(sliceID)
    seg = SimpleNamespace(value=segment)
    if getattr(sl, "path_segment", None) is None:
        sl.path_segment = []  # type: ignore[attr-defined]
    sl.path_segment.append(seg)  # type: ignore[attr-defined]
    register_parent(seg, sl, ("path_segment",), "list")
    return get_handle(seg)


def removeFieldSliceAlternateRegisterRef(fieldSliceAlternateRegisterRefID: str) -> bool:  # F.7.78.7
    if resolve_handle(fieldSliceAlternateRegisterRefID) is None:
        raise TgiError("Invalid alternateRegisterRef", TgiFaultCode.INVALID_ID)
    return detach_child_by_handle(fieldSliceAlternateRegisterRefID)


def removeFieldSliceBankRef(fieldSliceBankRefID: str) -> bool:  # F.7.78.8
    if resolve_handle(fieldSliceBankRefID) is None:
        raise TgiError("Invalid bankRef handle", TgiFaultCode.INVALID_ID)
    return detach_child_by_handle(fieldSliceBankRefID)


def removeFieldSliceMemoryRemapRef(fieldSliceMemoryRemapRefID: str) -> bool:  # F.7.78.9
    if resolve_handle(fieldSliceMemoryRemapRefID) is None:
        raise TgiError("Invalid memoryRemapRef handle", TgiFaultCode.INVALID_ID)
    return detach_child_by_handle(fieldSliceMemoryRemapRefID)


def removeFieldSliceRange(fieldSliceRangeID: str) -> bool:  # F.7.78.10
    if resolve_handle(fieldSliceRangeID) is None:
        raise TgiError("Invalid range handle", TgiFaultCode.INVALID_ID)
    return detach_child_by_handle(fieldSliceRangeID)


def removeFieldSliceRegisterFileRef(fieldSliceRegisterFileRefID: str) -> bool:  # F.7.78.11
    if resolve_handle(fieldSliceRegisterFileRefID) is None:
        raise TgiError("Invalid registerFileRef handle", TgiFaultCode.INVALID_ID)
    return detach_child_by_handle(fieldSliceRegisterFileRefID)


def removeLocationSlice(locationSliceID: str) -> bool:  # F.7.78.12
    if resolve_handle(locationSliceID) is None:
        raise TgiError("Invalid locationSlice handle", TgiFaultCode.INVALID_ID)
    return detach_child_by_handle(locationSliceID)


def removeModeFieldSlice(modeFieldSliceID: str) -> bool:  # F.7.78.13
    if resolve_handle(modeFieldSliceID) is None:
        raise TgiError("Invalid modeFieldSlice handle", TgiFaultCode.INVALID_ID)
    return detach_child_by_handle(modeFieldSliceID)


def removeModePortSlice(modePortSliceID: str) -> bool:  # F.7.78.14
    if resolve_handle(modePortSliceID) is None:
        raise TgiError("Invalid modePortSlice handle", TgiFaultCode.INVALID_ID)
    return detach_child_by_handle(modePortSliceID)


def removePortSlicePartSelect(portSlicePartSelectID: str) -> bool:  # F.7.78.15
    if resolve_handle(portSlicePartSelectID) is None:
        raise TgiError("Invalid partSelect handle", TgiFaultCode.INVALID_ID)
    return detach_child_by_handle(portSlicePartSelectID)


def removePortSliceSubPortReference(portSliceSubPortReferenceID: str) -> bool:  # F.7.78.16
    if resolve_handle(portSliceSubPortReferenceID) is None:
        raise TgiError("Invalid subPortReference handle", TgiFaultCode.INVALID_ID)
    return detach_child_by_handle(portSliceSubPortReferenceID)


def removeSlicePathSegment(slicePathSegmentID: str) -> bool:  # F.7.78.17
    if resolve_handle(slicePathSegmentID) is None:
        raise TgiError("Invalid slicePathSegment handle", TgiFaultCode.INVALID_ID)
    return detach_child_by_handle(slicePathSegmentID)


def removeSliceRange(sliceRangeID: str) -> bool:  # F.7.78.18
    if resolve_handle(sliceRangeID) is None:
        raise TgiError("Invalid sliceRange handle", TgiFaultCode.INVALID_ID)
    return detach_child_by_handle(sliceRangeID)


def setFieldSliceAddressBlockRef(fieldSliceID: str, name: str) -> bool:  # F.7.78.19
    sl = _ensure_slice_parent(fieldSliceID)
    sl.address_block_ref = SimpleNamespace(name=name)  # type: ignore[attr-defined]
    register_parent(sl.address_block_ref, sl, ("address_block_ref",), "single")  # type: ignore[attr-defined]
    return True


def setFieldSliceAddressSpaceRef(fieldSliceID: str, name: str) -> bool:  # F.7.78.20
    sl = _ensure_slice_parent(fieldSliceID)
    sl.address_space_ref = SimpleNamespace(name=name)  # type: ignore[attr-defined]
    register_parent(sl.address_space_ref, sl, ("address_space_ref",), "single")  # type: ignore[attr-defined]
    return True


def setFieldSliceAlternateRegisterRef(fieldSliceID: str, name: str) -> bool:  # F.7.78.21
    sl = _ensure_slice_parent(fieldSliceID)
    sl.alternate_register_ref = SimpleNamespace(name=name)  # type: ignore[attr-defined]
    register_parent(sl.alternate_register_ref, sl, ("alternate_register_ref",), "single")  # type: ignore[attr-defined]
    return True


def setFieldSliceFieldRef(fieldSliceID: str, name: str) -> bool:  # F.7.78.22
    sl = _ensure_slice_parent(fieldSliceID)
    sl.field_ref = SimpleNamespace(name=name)  # type: ignore[attr-defined]
    register_parent(sl.field_ref, sl, ("field_ref",), "single")  # type: ignore[attr-defined]
    return True


def setFieldSliceMemoryMapRef(fieldSliceID: str, name: str) -> bool:  # F.7.78.23
    sl = _ensure_slice_parent(fieldSliceID)
    sl.memory_map_ref = SimpleNamespace(name=name)  # type: ignore[attr-defined]
    register_parent(sl.memory_map_ref, sl, ("memory_map_ref",), "single")  # type: ignore[attr-defined]
    return True


def setFieldSliceMemoryRemapRef(fieldSliceID: str, name: str) -> bool:  # F.7.78.24
    sl = _ensure_slice_parent(fieldSliceID)
    sl.memory_remap_ref = SimpleNamespace(name=name)  # type: ignore[attr-defined]
    register_parent(sl.memory_remap_ref, sl, ("memory_remap_ref",), "single")  # type: ignore[attr-defined]
    return True


def setFieldSliceRange(fieldSliceID: str, value: int | None = None, expression: str | None = None) -> bool:  # F.7.78.25
    if value is None and expression is None:
        raise TgiError("value or expression required", TgiFaultCode.INVALID_ARGUMENT)
    sl = _ensure_slice_parent(fieldSliceID)
    sl.range = SimpleNamespace(value=SimpleNamespace(value=value, expression=expression))  # type: ignore[attr-defined]
    register_parent(sl.range, sl, ("range",), "single")  # type: ignore[attr-defined]
    return True


def setFieldSliceRegisterRef(fieldSliceID: str, name: str) -> bool:  # F.7.78.26
    sl = _ensure_slice_parent(fieldSliceID)
    sl.register_ref = SimpleNamespace(name=name)  # type: ignore[attr-defined]
    register_parent(sl.register_ref, sl, ("register_ref",), "single")  # type: ignore[attr-defined]
    return True


def setPortSlicePartSelect(portSliceID: str, leftExpression: str, rightExpression: str) -> bool:  # F.7.78.27
    ps = _ensure_slice_parent(portSliceID)
    ps.part_select = SimpleNamespace(
        left=SimpleNamespace(value=leftExpression),
        right=SimpleNamespace(value=rightExpression),
    )  # type: ignore[attr-defined]
    register_parent(ps.part_select, ps, ("part_select",), "single")  # type: ignore[attr-defined]
    return True


def setPortSlicePortRef(portSliceID: str, name: str) -> bool:  # F.7.78.28
    ps = _ensure_slice_parent(portSliceID)
    ps.port_ref = SimpleNamespace(name=name)  # type: ignore[attr-defined]
    register_parent(ps.port_ref, ps, ("port_ref",), "single")  # type: ignore[attr-defined]
    return True


def setSliceRange(sliceID: str, leftExpression: str, rightExpression: str) -> bool:  # F.7.78.29
    sl = _ensure_slice_parent(sliceID)
    sl.left = SimpleNamespace(value=leftExpression)  # type: ignore[attr-defined]
    sl.right = SimpleNamespace(value=rightExpression)  # type: ignore[attr-defined]
    # parent registration for left/right not strictly necessary if slice object already registered
    return True

