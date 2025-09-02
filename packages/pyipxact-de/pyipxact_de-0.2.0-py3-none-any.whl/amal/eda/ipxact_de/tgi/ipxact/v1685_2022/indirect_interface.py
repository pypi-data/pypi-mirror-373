"""Indirect interface category TGI functions (IEEE 1685-2022).

Implements exactly the BASE (F.7.53) and EXTENDED (F.7.54) indirect
interface functions for manipulating and querying the ``indirectAddressRef``
and ``indirectDataRef`` structures of an :class:`IndirectInterface`.

Error handling: invalid handles raise :class:`TgiError` with
``TgiFaultCode.INVALID_ID``; semantic violations return
``TgiFaultCode.INVALID_ARGUMENT``.
"""
# ruff: noqa: I001
from __future__ import annotations

from org.accellera.ipxact.v1685_2022 import IndirectInterface
from org.accellera.ipxact.v1685_2022.indirect_address_ref import IndirectAddressRef
from org.accellera.ipxact.v1685_2022.indirect_data_ref import IndirectDataRef
from org.accellera.ipxact.v1685_2022.bank_ref import BankRef
from org.accellera.ipxact.v1685_2022.register_file_ref import RegisterFileRef

from .core import (
    TgiError,
    TgiFaultCode,
    resolve_handle,
    get_handle,
    register_parent,
    detach_child_by_handle,
)

__all__ = [
    # BASE (F.7.53)
    "getIndirectAddressRefAddressBlockRefByName",
    "getIndirectAddressRefAddressBlockRefID",
    "getIndirectAddressRefAddressSpaceRefByName",
    "getIndirectAddressRefAddressSpaceRefID",
    "getIndirectAddressRefAlternateRegisterRefByName",
    "getIndirectAddressRefAlternateRegisterRefID",
    "getIndirectAddressRefBankRefByNames",
    "getIndirectAddressRefBankRefIDs",
    "getIndirectAddressRefFieldRefByName",
    "getIndirectAddressRefFieldRefID",
    "getIndirectAddressRefMemoryMapRefByName",
    "getIndirectAddressRefMemoryMapRefID",
    "getIndirectAddressRefMemoryRemapRefByID",
    "getIndirectAddressRefMemoryRemapRefByName",
    "getIndirectAddressRefMemoryRemapRefID",
    "getIndirectAddressRefRegisterFileRefByNames",
    "getIndirectAddressRefRegisterFileRefIDs",
    "getIndirectAddressRefRegisterRefByName",
    "getIndirectAddressRefRegisterRefID",
    "getIndirectDataRefAddressBlockRefByName",
    "getIndirectDataRefAddressBlockRefID",
    "getIndirectDataRefAddressSpaceRefByName",
    "getIndirectDataRefAddressSpaceRefID",
    "getIndirectDataRefAlternateRegisterRefByName",
    "getIndirectDataRefAlternateRegisterRefID",
    "getIndirectDataRefBankRefByNames",
    "getIndirectDataRefBankRefIDs",
    "getIndirectDataRefFieldRefByName",
    "getIndirectDataRefFieldRefID",
    "getIndirectDataRefMemoryMapRefByName",
    "getIndirectDataRefMemoryMapRefID",
    "getIndirectDataRefMemoryRemapRefByID",
    "getIndirectDataRefMemoryRemapRefByName",
    "getIndirectDataRefMemoryRemapRefID",
    "getIndirectDataRefRegisterFileRefByNames",
    "getIndirectDataRefRegisterFileRefIDs",
    "getIndirectDataRefRegisterRefByName",
    "getIndirectDataRefRegisterRefID",
    # EXTENDED (F.7.54)
    "addIndirectAddressRefBankRef",
    "addIndirectAddressRefRegisterFileRef",
    "addIndirectDataRefBankRef",
    "addIndirectDataRefRegisterFileRef",
    "addIndirectInterfaceTransparentBridge",
    "removeAliasOfMemoryRemapRef",
    "removeBroadcastToAddressSpaceRef",
    "removeIndirectAddressRefAddressBlockRef",
    "removeIndirectAddressRefAddressSpaceRef",
    "removeIndirectAddressRefAlternateRegisterRef",
    "removeIndirectAddressRefBankRef",
    "removeIndirectAddressRefMemoryMapRef",
    "removeIndirectAddressRefMemoryRemapRef",
    "removeIndirectAddressRefRegisterFileRef",
    "removeIndirectAddressRefRegisterRef",
    "removeIndirectDataRefAddressBlockRef",
    "removeIndirectDataRefAddressSpaceRef",
    "removeIndirectDataRefAlternateRegisterRef",
    "removeIndirectDataRefBankRef",
    "removeIndirectDataRefMemoryMapRef",
    "removeIndirectDataRefMemoryRemapRef",
    "removeIndirectDataRefRegisterFileRef",
    "removeIndirectDataRefRegisterRef",
]


# ---------------------------------------------------------------------------
# Helpers (non-spec)
# ---------------------------------------------------------------------------

def _resolve(iiID: str) -> IndirectInterface | None:
    obj = resolve_handle(iiID)
    return obj if isinstance(obj, IndirectInterface) else None


def _resolve_address_ref(addressRefID: str) -> IndirectAddressRef | None:
    obj = resolve_handle(addressRefID)
    return obj if isinstance(obj, IndirectAddressRef) else None


def _resolve_data_ref(dataRefID: str) -> IndirectDataRef | None:
    obj = resolve_handle(dataRefID)
    return obj if isinstance(obj, IndirectDataRef) else None


def _get_address_ref(iiID: str) -> IndirectAddressRef:
    ii = _resolve(iiID)
    if ii is None:
        raise TgiError("Invalid indirectInterface handle", TgiFaultCode.INVALID_ID)
    if ii.indirect_address_ref is None:
        raise TgiError("Missing indirectAddressRef", TgiFaultCode.INVALID_ARGUMENT)
    return ii.indirect_address_ref


def _get_data_ref(iiID: str) -> IndirectDataRef:
    ii = _resolve(iiID)
    if ii is None:
        raise TgiError("Invalid indirectInterface handle", TgiFaultCode.INVALID_ID)
    if ii.indirect_data_ref is None:
        raise TgiError("Missing indirectDataRef", TgiFaultCode.INVALID_ARGUMENT)
    return ii.indirect_data_ref


def _safe_name(obj, attr: str) -> str | None:  # helper for attribute-holding refs
    if obj is None:
        return None
    return getattr(obj, attr, None)


# ---------------------------------------------------------------------------
# BASE (F.7.53) – IndirectAddressRef getters
# ---------------------------------------------------------------------------

def getIndirectAddressRefAddressBlockRefByName(indirectAddressRefID: str) -> str | None:
    """Return addressBlockRef attribute value.

    Section: F.7.53.1.
    """
    ar = _resolve_address_ref(indirectAddressRefID)
    if ar is None:
        raise TgiError("Invalid indirectAddressRef handle", TgiFaultCode.INVALID_ID)
    blk = ar.address_block_ref
    return None if blk is None else blk.address_block_ref


def getIndirectAddressRefAddressBlockRefID(indirectAddressRefID: str) -> str | None:
    """Return handle of addressBlockRef element.

    Section: F.7.53.2.
    """
    ar = _resolve_address_ref(indirectAddressRefID)
    if ar is None:
        raise TgiError("Invalid indirectAddressRef handle", TgiFaultCode.INVALID_ID)
    return None if ar.address_block_ref is None else get_handle(ar.address_block_ref)


def getIndirectAddressRefAddressSpaceRefByName(indirectAddressRefID: str) -> str | None:
    """Return addressSpaceRef attribute value.

    Section: F.7.53.3.
    """
    ar = _resolve_address_ref(indirectAddressRefID)
    if ar is None:
        raise TgiError("Invalid indirectAddressRef handle", TgiFaultCode.INVALID_ID)
    asr = ar.address_space_ref
    return None if asr is None else asr.address_space_ref


def getIndirectAddressRefAddressSpaceRefID(indirectAddressRefID: str) -> str | None:
    """Return handle of addressSpaceRef element.

    Section: F.7.53.4.
    """
    ar = _resolve_address_ref(indirectAddressRefID)
    if ar is None:
        raise TgiError("Invalid indirectAddressRef handle", TgiFaultCode.INVALID_ID)
    return None if ar.address_space_ref is None else get_handle(ar.address_space_ref)


def getIndirectAddressRefAlternateRegisterRefByName(indirectAddressRefID: str) -> str | None:
    """Return alternateRegisterRef attribute value.

    Section: F.7.53.5.
    """
    ar = _resolve_address_ref(indirectAddressRefID)
    if ar is None:
        raise TgiError("Invalid indirectAddressRef handle", TgiFaultCode.INVALID_ID)
    alt = ar.alternate_register_ref
    return None if alt is None else alt.alternate_register_ref


def getIndirectAddressRefAlternateRegisterRefID(indirectAddressRefID: str) -> str | None:
    """Return handle of alternateRegisterRef element.

    Section: F.7.53.6.
    """
    ar = _resolve_address_ref(indirectAddressRefID)
    if ar is None:
        raise TgiError("Invalid indirectAddressRef handle", TgiFaultCode.INVALID_ID)
    return None if ar.alternate_register_ref is None else get_handle(ar.alternate_register_ref)


def getIndirectAddressRefBankRefByNames(indirectAddressRefID: str) -> list[str]:
    """Return list of bankRef attribute values.

    Section: F.7.53.7.
    """
    ar = _resolve_address_ref(indirectAddressRefID)
    if ar is None:
        raise TgiError("Invalid indirectAddressRef handle", TgiFaultCode.INVALID_ID)
    return [b.bank_ref for b in getattr(ar, "bank_ref", []) if b.bank_ref is not None]


def getIndirectAddressRefBankRefIDs(indirectAddressRefID: str) -> list[str]:
    """Return handles of bankRef elements.

    Section: F.7.53.8.
    """
    ar = _resolve_address_ref(indirectAddressRefID)
    if ar is None:
        raise TgiError("Invalid indirectAddressRef handle", TgiFaultCode.INVALID_ID)
    return [get_handle(b) for b in getattr(ar, "bank_ref", [])]


def getIndirectAddressRefFieldRefByName(indirectAddressRefID: str) -> str | None:
    """Return fieldRef attribute value.

    Section: F.7.53.9.
    """
    ar = _resolve_address_ref(indirectAddressRefID)
    if ar is None:
        raise TgiError("Invalid indirectAddressRef handle", TgiFaultCode.INVALID_ID)
    fr = ar.field_ref
    return None if fr is None else fr.field_ref


def getIndirectAddressRefFieldRefID(indirectAddressRefID: str) -> str | None:
    """Return handle of fieldRef element.

    Section: F.7.53.10.
    """
    ar = _resolve_address_ref(indirectAddressRefID)
    if ar is None:
        raise TgiError("Invalid indirectAddressRef handle", TgiFaultCode.INVALID_ID)
    return None if ar.field_ref is None else get_handle(ar.field_ref)


def getIndirectAddressRefMemoryMapRefByName(indirectAddressRefID: str) -> str | None:
    """Return memoryMapRef attribute value.

    Section: F.7.53.11.
    """
    ar = _resolve_address_ref(indirectAddressRefID)
    if ar is None:
        raise TgiError("Invalid indirectAddressRef handle", TgiFaultCode.INVALID_ID)
    mm = ar.memory_map_ref
    return None if mm is None else mm.memory_map_ref


def getIndirectAddressRefMemoryMapRefID(indirectAddressRefID: str) -> str | None:
    """Return handle of memoryMapRef element.

    Section: F.7.53.12.
    """
    ar = _resolve_address_ref(indirectAddressRefID)
    if ar is None:
        raise TgiError("Invalid indirectAddressRef handle", TgiFaultCode.INVALID_ID)
    return None if ar.memory_map_ref is None else get_handle(ar.memory_map_ref)


def getIndirectAddressRefMemoryRemapRefByID(indirectAddressRefID: str) -> str | None:
    """Return memoryRemapRef attribute value (same as ByName for attribute form).

    Section: F.7.53.13.
    """
    ar = _resolve_address_ref(indirectAddressRefID)
    if ar is None:
        raise TgiError("Invalid indirectAddressRef handle", TgiFaultCode.INVALID_ID)
    mr = ar.memory_remap_ref
    return None if mr is None else mr.memory_remap_ref


def getIndirectAddressRefMemoryRemapRefByName(indirectAddressRefID: str) -> str | None:
    """Alias returning memoryRemapRef attribute value.

    Section: F.7.53.14.
    """
    return getIndirectAddressRefMemoryRemapRefByID(indirectAddressRefID)


def getIndirectAddressRefMemoryRemapRefID(indirectAddressRefID: str) -> str | None:
    """Return handle of memoryRemapRef element.

    Section: F.7.53.15.
    """
    ar = _resolve_address_ref(indirectAddressRefID)
    if ar is None:
        raise TgiError("Invalid indirectAddressRef handle", TgiFaultCode.INVALID_ID)
    return None if ar.memory_remap_ref is None else get_handle(ar.memory_remap_ref)


def getIndirectAddressRefRegisterFileRefByNames(indirectAddressRefID: str) -> list[str]:
    """Return registerFileRef attribute values.

    Section: F.7.53.16.
    """
    ar = _resolve_address_ref(indirectAddressRefID)
    if ar is None:
        raise TgiError("Invalid indirectAddressRef handle", TgiFaultCode.INVALID_ID)
    return [r.register_file_ref for r in getattr(ar, "register_file_ref", []) if r.register_file_ref is not None]


def getIndirectAddressRefRegisterFileRefIDs(indirectAddressRefID: str) -> list[str]:
    """Return handles of registerFileRef elements.

    Section: F.7.53.17.
    """
    ar = _resolve_address_ref(indirectAddressRefID)
    if ar is None:
        raise TgiError("Invalid indirectAddressRef handle", TgiFaultCode.INVALID_ID)
    return [get_handle(r) for r in getattr(ar, "register_file_ref", [])]


def getIndirectAddressRefRegisterRefByName(indirectAddressRefID: str) -> str | None:
    """Return registerRef attribute value.

    Section: F.7.53.18.
    """
    ar = _resolve_address_ref(indirectAddressRefID)
    if ar is None:
        raise TgiError("Invalid indirectAddressRef handle", TgiFaultCode.INVALID_ID)
    rr = ar.register_ref
    return None if rr is None else rr.register_ref


def getIndirectAddressRefRegisterRefID(indirectAddressRefID: str) -> str | None:
    """Return handle of registerRef element.

    Section: F.7.53.19.
    """
    ar = _resolve_address_ref(indirectAddressRefID)
    if ar is None:
        raise TgiError("Invalid indirectAddressRef handle", TgiFaultCode.INVALID_ID)
    return None if ar.register_ref is None else get_handle(ar.register_ref)


# IndirectDataRef getters (F.7.53.20+)

def getIndirectDataRefAddressBlockRefByName(indirectDataRefID: str) -> str | None:
    """Return addressBlockRef attribute value for data ref.

    Section: F.7.53.20.
    """
    dr = _resolve_data_ref(indirectDataRefID)
    if dr is None:
        raise TgiError("Invalid indirectDataRef handle", TgiFaultCode.INVALID_ID)
    blk = dr.address_block_ref
    return None if blk is None else blk.address_block_ref


def getIndirectDataRefAddressBlockRefID(indirectDataRefID: str) -> str | None:
    """Return handle of addressBlockRef element (data).

    Section: F.7.53.21.
    """
    dr = _resolve_data_ref(indirectDataRefID)
    if dr is None:
        raise TgiError("Invalid indirectDataRef handle", TgiFaultCode.INVALID_ID)
    return None if dr.address_block_ref is None else get_handle(dr.address_block_ref)


def getIndirectDataRefAddressSpaceRefByName(indirectDataRefID: str) -> str | None:
    """Return addressSpaceRef attribute value (data).

    Section: F.7.53.22.
    """
    dr = _resolve_data_ref(indirectDataRefID)
    if dr is None:
        raise TgiError("Invalid indirectDataRef handle", TgiFaultCode.INVALID_ID)
    asr = dr.address_space_ref
    return None if asr is None else asr.address_space_ref


def getIndirectDataRefAddressSpaceRefID(indirectDataRefID: str) -> str | None:
    """Return handle of addressSpaceRef element (data).

    Section: F.7.53.23.
    """
    dr = _resolve_data_ref(indirectDataRefID)
    if dr is None:
        raise TgiError("Invalid indirectDataRef handle", TgiFaultCode.INVALID_ID)
    return None if dr.address_space_ref is None else get_handle(dr.address_space_ref)


def getIndirectDataRefAlternateRegisterRefByName(indirectDataRefID: str) -> str | None:
    """Return alternateRegisterRef attribute value (data).

    Section: F.7.53.24.
    """
    dr = _resolve_data_ref(indirectDataRefID)
    if dr is None:
        raise TgiError("Invalid indirectDataRef handle", TgiFaultCode.INVALID_ID)
    alt = dr.alternate_register_ref
    return None if alt is None else alt.alternate_register_ref


def getIndirectDataRefAlternateRegisterRefID(indirectDataRefID: str) -> str | None:
    """Return handle of alternateRegisterRef element (data).

    Section: F.7.53.25.
    """
    dr = _resolve_data_ref(indirectDataRefID)
    if dr is None:
        raise TgiError("Invalid indirectDataRef handle", TgiFaultCode.INVALID_ID)
    return None if dr.alternate_register_ref is None else get_handle(dr.alternate_register_ref)


def getIndirectDataRefBankRefByNames(indirectDataRefID: str) -> list[str]:
    """Return bankRef attribute values (data).

    Section: F.7.53.26.
    """
    dr = _resolve_data_ref(indirectDataRefID)
    if dr is None:
        raise TgiError("Invalid indirectDataRef handle", TgiFaultCode.INVALID_ID)
    return [b.bank_ref for b in getattr(dr, "bank_ref", []) if b.bank_ref is not None]


def getIndirectDataRefBankRefIDs(indirectDataRefID: str) -> list[str]:
    """Return handles of bankRef elements (data).

    Section: F.7.53.27.
    """
    dr = _resolve_data_ref(indirectDataRefID)
    if dr is None:
        raise TgiError("Invalid indirectDataRef handle", TgiFaultCode.INVALID_ID)
    return [get_handle(b) for b in getattr(dr, "bank_ref", [])]


def getIndirectDataRefFieldRefByName(indirectDataRefID: str) -> str | None:
    """Return fieldRef attribute value (data).

    Section: F.7.53.28.
    """
    dr = _resolve_data_ref(indirectDataRefID)
    if dr is None:
        raise TgiError("Invalid indirectDataRef handle", TgiFaultCode.INVALID_ID)
    fr = dr.field_ref
    return None if fr is None else fr.field_ref


def getIndirectDataRefFieldRefID(indirectDataRefID: str) -> str | None:
    """Return handle of fieldRef element (data).

    Section: F.7.53.29.
    """
    dr = _resolve_data_ref(indirectDataRefID)
    if dr is None:
        raise TgiError("Invalid indirectDataRef handle", TgiFaultCode.INVALID_ID)
    return None if dr.field_ref is None else get_handle(dr.field_ref)


def getIndirectDataRefMemoryMapRefByName(indirectDataRefID: str) -> str | None:
    """Return memoryMapRef attribute value (data).

    Section: F.7.53.30.
    """
    dr = _resolve_data_ref(indirectDataRefID)
    if dr is None:
        raise TgiError("Invalid indirectDataRef handle", TgiFaultCode.INVALID_ID)
    mm = dr.memory_map_ref
    return None if mm is None else mm.memory_map_ref


def getIndirectDataRefMemoryMapRefID(indirectDataRefID: str) -> str | None:
    """Return handle of memoryMapRef element (data).

    Section: F.7.53.31.
    """
    dr = _resolve_data_ref(indirectDataRefID)
    if dr is None:
        raise TgiError("Invalid indirectDataRef handle", TgiFaultCode.INVALID_ID)
    return None if dr.memory_map_ref is None else get_handle(dr.memory_map_ref)


def getIndirectDataRefMemoryRemapRefByID(indirectDataRefID: str) -> str | None:
    """Return memoryRemapRef attribute value (data).

    Section: F.7.53.32.
    """
    dr = _resolve_data_ref(indirectDataRefID)
    if dr is None:
        raise TgiError("Invalid indirectDataRef handle", TgiFaultCode.INVALID_ID)
    mr = dr.memory_remap_ref
    return None if mr is None else mr.memory_remap_ref


def getIndirectDataRefMemoryRemapRefByName(indirectDataRefID: str) -> str | None:
    """Alias returning memoryRemapRef attribute value (data).

    Section: F.7.53.33.
    """
    return getIndirectDataRefMemoryRemapRefByID(indirectDataRefID)


def getIndirectDataRefMemoryRemapRefID(indirectDataRefID: str) -> str | None:
    """Return handle of memoryRemapRef element (data).

    Section: F.7.53.34.
    """
    dr = _resolve_data_ref(indirectDataRefID)
    if dr is None:
        raise TgiError("Invalid indirectDataRef handle", TgiFaultCode.INVALID_ID)
    return None if dr.memory_remap_ref is None else get_handle(dr.memory_remap_ref)


def getIndirectDataRefRegisterFileRefByNames(indirectDataRefID: str) -> list[str]:
    """Return registerFileRef attribute values (data).

    Section: F.7.53.35.
    """
    dr = _resolve_data_ref(indirectDataRefID)
    if dr is None:
        raise TgiError("Invalid indirectDataRef handle", TgiFaultCode.INVALID_ID)
    return [r.register_file_ref for r in getattr(dr, "register_file_ref", []) if r.register_file_ref is not None]


def getIndirectDataRefRegisterFileRefIDs(indirectDataRefID: str) -> list[str]:
    """Return handles of registerFileRef elements (data).

    Section: F.7.53.36.
    """
    dr = _resolve_data_ref(indirectDataRefID)
    if dr is None:
        raise TgiError("Invalid indirectDataRef handle", TgiFaultCode.INVALID_ID)
    return [get_handle(r) for r in getattr(dr, "register_file_ref", [])]


def getIndirectDataRefRegisterRefByName(indirectDataRefID: str) -> str | None:
    """Return registerRef attribute value (data).

    Section: F.7.53.37.
    """
    dr = _resolve_data_ref(indirectDataRefID)
    if dr is None:
        raise TgiError("Invalid indirectDataRef handle", TgiFaultCode.INVALID_ID)
    rr = dr.register_ref
    return None if rr is None else rr.register_ref


def getIndirectDataRefRegisterRefID(indirectDataRefID: str) -> str | None:
    """Return handle of registerRef element (data).

    Section: F.7.53.38.
    """
    dr = _resolve_data_ref(indirectDataRefID)
    if dr is None:
        raise TgiError("Invalid indirectDataRef handle", TgiFaultCode.INVALID_ID)
    return None if dr.register_ref is None else get_handle(dr.register_ref)


# ---------------------------------------------------------------------------
# EXTENDED (F.7.54)
# ---------------------------------------------------------------------------

def addIndirectAddressRefBankRef(indirectAddressRefID: str, bankRef: str) -> str:
    """Append a bankRef to indirectAddressRef.

    Section: F.7.54.1.
    """
    ar = _resolve_address_ref(indirectAddressRefID)
    if ar is None:
        raise TgiError("Invalid indirectAddressRef handle", TgiFaultCode.INVALID_ID)
    br = BankRef(bank_ref=bankRef)
    ar.bank_ref.append(br)  # type: ignore[attr-defined]
    register_parent(br, ar, ("bank_ref",), "list")
    return get_handle(br)


def addIndirectAddressRefRegisterFileRef(indirectAddressRefID: str, registerFileRef: str) -> str:
    """Append a registerFileRef to indirectAddressRef.

    Section: F.7.54.2.
    """
    ar = _resolve_address_ref(indirectAddressRefID)
    if ar is None:
        raise TgiError("Invalid indirectAddressRef handle", TgiFaultCode.INVALID_ID)
    rf = RegisterFileRef(register_file_ref=registerFileRef)
    ar.register_file_ref.append(rf)  # type: ignore[attr-defined]
    register_parent(rf, ar, ("register_file_ref",), "list")
    return get_handle(rf)


def addIndirectDataRefBankRef(indirectDataRefID: str, bankRef: str) -> str:
    """Append a bankRef to indirectDataRef.

    Section: F.7.54.3.
    """
    dr = _resolve_data_ref(indirectDataRefID)
    if dr is None:
        raise TgiError("Invalid indirectDataRef handle", TgiFaultCode.INVALID_ID)
    br = BankRef(bank_ref=bankRef)
    dr.bank_ref.append(br)  # type: ignore[attr-defined]
    register_parent(br, dr, ("bank_ref",), "list")
    return get_handle(br)


def addIndirectDataRefRegisterFileRef(indirectDataRefID: str, registerFileRef: str) -> str:
    """Append a registerFileRef to indirectDataRef.

    Section: F.7.54.4.
    """
    dr = _resolve_data_ref(indirectDataRefID)
    if dr is None:
        raise TgiError("Invalid indirectDataRef handle", TgiFaultCode.INVALID_ID)
    rf = RegisterFileRef(register_file_ref=registerFileRef)
    dr.register_file_ref.append(rf)  # type: ignore[attr-defined]
    register_parent(rf, dr, ("register_file_ref",), "list")
    return get_handle(rf)


def addIndirectInterfaceTransparentBridge(indirectInterfaceID: str, initiatorRef: str) -> str:
    """Add a transparentBridge element to indirectInterface.

    Section: F.7.54.5.
    """
    ii = _resolve(indirectInterfaceID)
    if ii is None:
        raise TgiError("Invalid indirectInterface handle", TgiFaultCode.INVALID_ID)
    from org.accellera.ipxact.v1685_2022.transparent_bridge import TransparentBridge

    tb = TransparentBridge(initiator_ref=initiatorRef)
    ii.transparent_bridge.append(tb)  # type: ignore[attr-defined]
    register_parent(tb, ii, ("transparent_bridge",), "list")
    return get_handle(tb)


# The following remove* functions act on handles of child elements

def removeAliasOfMemoryRemapRef(aliasOfMemoryRemapRefID: str) -> bool:
    """Remove aliasOfMemoryRemapRef (global element reference removal).

    Section: F.7.54.6.
    """
    return detach_child_by_handle(aliasOfMemoryRemapRefID)


def removeBroadcastToAddressSpaceRef(broadcastToAddressSpaceRefID: str) -> bool:
    """Remove broadcastToAddressSpaceRef.

    Section: F.7.54.7.
    """
    return detach_child_by_handle(broadcastToAddressSpaceRefID)


def removeIndirectAddressRefAddressBlockRef(indirectAddressRefID: str) -> bool:
    """Remove addressBlockRef from indirectAddressRef.

    Section: F.7.54.8.
    """
    ar = _resolve_address_ref(indirectAddressRefID)
    if ar is None:
        raise TgiError("Invalid indirectAddressRef handle", TgiFaultCode.INVALID_ID)
    ar.address_block_ref = None
    return True


def removeIndirectAddressRefAddressSpaceRef(indirectAddressRefID: str) -> bool:
    """Remove addressSpaceRef from indirectAddressRef.

    Section: F.7.54.9.
    """
    ar = _resolve_address_ref(indirectAddressRefID)
    if ar is None:
        raise TgiError("Invalid indirectAddressRef handle", TgiFaultCode.INVALID_ID)
    ar.address_space_ref = None
    return True


def removeIndirectAddressRefAlternateRegisterRef(indirectAddressRefID: str) -> bool:
    """Remove alternateRegisterRef from indirectAddressRef.

    Section: F.7.54.10.
    """
    ar = _resolve_address_ref(indirectAddressRefID)
    if ar is None:
        raise TgiError("Invalid indirectAddressRef handle", TgiFaultCode.INVALID_ID)
    ar.alternate_register_ref = None
    return True


def removeIndirectAddressRefBankRef(bankRefID: str) -> bool:
    """Remove a bankRef element (by handle).

    Section: F.7.54.11.
    """
    return detach_child_by_handle(bankRefID)


def removeIndirectAddressRefMemoryMapRef(indirectAddressRefID: str) -> bool:
    """Remove memoryMapRef from indirectAddressRef.

    Section: F.7.54.12.
    """
    ar = _resolve_address_ref(indirectAddressRefID)
    if ar is None:
        raise TgiError("Invalid indirectAddressRef handle", TgiFaultCode.INVALID_ID)
    ar.memory_map_ref = None
    return True


def removeIndirectAddressRefMemoryRemapRef(indirectAddressRefID: str) -> bool:
    """Remove memoryRemapRef from indirectAddressRef.

    Section: F.7.54.13.
    """
    ar = _resolve_address_ref(indirectAddressRefID)
    if ar is None:
        raise TgiError("Invalid indirectAddressRef handle", TgiFaultCode.INVALID_ID)
    ar.memory_remap_ref = None
    return True


def removeIndirectAddressRefRegisterFileRef(registerFileRefID: str) -> bool:
    """Remove a registerFileRef element (by handle) from indirectAddressRef.

    Section: F.7.54.14.
    """
    return detach_child_by_handle(registerFileRefID)


def removeIndirectAddressRefRegisterRef(indirectAddressRefID: str) -> bool:
    """Remove registerRef from indirectAddressRef.

    Section: F.7.54.15.
    """
    ar = _resolve_address_ref(indirectAddressRefID)
    if ar is None:
        raise TgiError("Invalid indirectAddressRef handle", TgiFaultCode.INVALID_ID)
    ar.register_ref = None
    return True


def removeIndirectDataRefAddressBlockRef(indirectDataRefID: str) -> bool:
    """Remove addressBlockRef from indirectDataRef.

    Section: F.7.54.16.
    """
    dr = _resolve_data_ref(indirectDataRefID)
    if dr is None:
        raise TgiError("Invalid indirectDataRef handle", TgiFaultCode.INVALID_ID)
    dr.address_block_ref = None
    return True


def removeIndirectDataRefAddressSpaceRef(indirectDataRefID: str) -> bool:
    """Remove addressSpaceRef from indirectDataRef.

    Section: F.7.54.17.
    """
    dr = _resolve_data_ref(indirectDataRefID)
    if dr is None:
        raise TgiError("Invalid indirectDataRef handle", TgiFaultCode.INVALID_ID)
    dr.address_space_ref = None
    return True


def removeIndirectDataRefAlternateRegisterRef(indirectDataRefID: str) -> bool:
    """Remove alternateRegisterRef from indirectDataRef.

    Section: F.7.54.18.
    """
    dr = _resolve_data_ref(indirectDataRefID)
    if dr is None:
        raise TgiError("Invalid indirectDataRef handle", TgiFaultCode.INVALID_ID)
    dr.alternate_register_ref = None
    return True


def removeIndirectDataRefBankRef(bankRefID: str) -> bool:
    """Remove a bankRef (data) by handle.

    Section: F.7.54.19.
    """
    return detach_child_by_handle(bankRefID)


def removeIndirectDataRefMemoryMapRef(indirectDataRefID: str) -> bool:
    """Remove memoryMapRef from indirectDataRef.

    Section: F.7.54.20.
    """
    dr = _resolve_data_ref(indirectDataRefID)
    if dr is None:
        raise TgiError("Invalid indirectDataRef handle", TgiFaultCode.INVALID_ID)
    dr.memory_map_ref = None
    return True


def removeIndirectDataRefMemoryRemapRef(indirectDataRefID: str) -> bool:
    """Remove memoryRemapRef from indirectDataRef.

    Section: F.7.54.21.
    """
    dr = _resolve_data_ref(indirectDataRefID)
    if dr is None:
        raise TgiError("Invalid indirectDataRef handle", TgiFaultCode.INVALID_ID)
    dr.memory_remap_ref = None
    return True


def removeIndirectDataRefRegisterFileRef(registerFileRefID: str) -> bool:
    """Remove registerFileRef element (data) by handle.

    Section: F.7.54.22.
    """
    return detach_child_by_handle(registerFileRefID)


def removeIndirectDataRefRegisterRef(indirectDataRefID: str) -> bool:
    """Remove registerRef from indirectDataRef.

    Section: F.7.54.23.
    """
    dr = _resolve_data_ref(indirectDataRefID)
    if dr is None:
        raise TgiError("Invalid indirectDataRef handle", TgiFaultCode.INVALID_ID)
    dr.register_ref = None
    return True

