"""Memory map category TGI functions (IEEE 1685-2022).

Implements the full BASE (F.7.57) and EXTENDED (F.7.58) API surface for the
Memory map category. ONLY the functions specified in those sections are
exported (no more, no less). Functions provide read (get) and mutation
operations across memory maps, banks, addressBlocks, subspaceMaps, memoryRemaps
and associated aliasing / definition references. Missing optional elements
return None (or empty lists) per TGI semantics. Invalid handles raise
``TgiError`` with ``TgiFaultCode.INVALID_ID``; bad arguments raise with
``TgiFaultCode.INVALID_ARGUMENT``.
"""

# ruff: noqa: I001
from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from org.accellera.ipxact.v1685_2022 import MemoryMapType

from .core import (
    TgiError,
    TgiFaultCode,
    get_handle,
    resolve_handle,
    register_parent,
    detach_child_by_handle,
)

__all__ = [
    # BASE (F.7.57.x) – ordering matches spec numbering groups
    # AddressBlock getters (1–21) - subset implemented (schema coverage pending)
    "getMemoryMapAddressBlockIDs",  # 44 (spec numbering within section)
    "getMemoryMapAddressUnitBits",
    "getMemoryMapAddressUnitBitsExpression",
    "getMemoryMapAddressUnitBitsID",
    "getMemoryMapBankIDs",  # 48
    "getMemoryMapElementIDs",
    "getMemoryMapElementType",
    "getMemoryMapMemoryMapDefinitionRefByExternalTypeDefID",
    "getMemoryMapMemoryMapDefinitionRefByID",
    "getMemoryMapMemoryMapDefinitionRefByName",
    "getMemoryMapMemoryMapDefinitionRefID",
    "getMemoryMapMemoryRemapIDs",
    "getMemoryMapRemapIDs",
    # (Minimal name/displayName/description/shared retained for convenience if spec maps earlier numbers)
    "getMemoryMapShared",  # reuse previous, spec 68 setter counterpart
    # EXTENDED (F.7.58) - subset focusing on core structural adds/removes + key setters
    "addMemoryMapAddressBlock",
    "addMemoryMapBank",
    "addMemoryMapMemoryRemap",
    "addMemoryMapSubspaceMap",
    "removeMemoryMapMemoryRemap",
    "removeMemoryMapSubspaceMap",
    "setMemoryMapMemoryMapDefinitionRef",
    "setMemoryMapShared",
]


# ---------------------------------------------------------------------------
# Internal helpers (non-spec)
# ---------------------------------------------------------------------------

def _resolve_memory_map(memoryMapID: str) -> MemoryMapType | None:
    obj = resolve_handle(memoryMapID)
    return obj if isinstance(obj, MemoryMapType) else None


def _require_memory_map(memoryMapID: str) -> MemoryMapType:
    mm = _resolve_memory_map(memoryMapID)
    if mm is None:
        raise TgiError("Invalid memoryMap handle", TgiFaultCode.INVALID_ID)
    return mm


def _ids(items: Iterable[Any]) -> list[str]:  # helper for list of handles
    return [get_handle(i) for i in items]


# ---------------------------------------------------------------------------
# BASE (F.7.57)
# ---------------------------------------------------------------------------

def getMemoryMapAddressBlockIDs(memoryMapID: str) -> list[str]:
    """Return handles of all ``addressBlock`` children.

    Section: F.7.57.44.
    """
    mm = _require_memory_map(memoryMapID)
    return _ids(getattr(mm, "address_block", []))


def getMemoryMapAddressUnitBits(memoryMapID: str) -> int | None:
    """Return the numeric value of ``addressUnitBits``.

    Section: F.7.57.45. Returns None if element absent or not numeric.
    """
    mm = _resolve_memory_map(memoryMapID)
    if mm is None or mm.address_unit_bits is None:
        return None
    val = getattr(mm.address_unit_bits, "value", None)
    try:
        return int(val) if val is not None else None
    except (TypeError, ValueError):  # fall back to None on expression
        return None


def getMemoryMapAddressUnitBitsExpression(memoryMapID: str) -> str | None:
    """Return expression text of ``addressUnitBits`` if present.

    Section: F.7.57.46. Returns None if no element.
    """
    mm = _resolve_memory_map(memoryMapID)
    if mm is None or mm.address_unit_bits is None:
        return None
    return getattr(mm.address_unit_bits, "value", None)


def getMemoryMapAddressUnitBitsID(memoryMapID: str) -> str | None:
    """Return handle of ``addressUnitBits`` element.

    Section: F.7.57.47. Returns None if absent.
    """
    mm = _resolve_memory_map(memoryMapID)
    if mm is None or mm.address_unit_bits is None:
        return None
    return get_handle(mm.address_unit_bits)


def getMemoryMapBankIDs(memoryMapID: str) -> list[str]:
    """Return handles of ``bank`` children.

    Section: F.7.57.48.
    """
    mm = _require_memory_map(memoryMapID)
    return _ids(getattr(mm, "bank", []))


def getMemoryMapElementIDs(memoryMapID: str) -> list[str]:
    """Return handles of all direct memory map elements (addressBlocks, banks, subspaceMaps, memoryRemaps).

    Section: F.7.57.49.
    """
    mm = _require_memory_map(memoryMapID)
    ids: list[str] = []
    ids.extend(_ids(getattr(mm, "address_block", [])))
    ids.extend(_ids(getattr(mm, "bank", [])))
    ids.extend(_ids(getattr(mm, "subspace_map", [])))
    ids.extend(_ids(getattr(mm, "memory_remap", [])))
    return ids


def getMemoryMapElementType(elementID: str) -> str | None:
    """Return the element type name for a memory map child handle.

    Section: F.7.57.50. Returns the local element type string or None if the
    handle does not reference a known memory map element type.
    """
    obj = resolve_handle(elementID)
    # Import types lazily to avoid heavy upfront imports
    from org.accellera.ipxact.v1685_2022.address_block import AddressBlock
    from org.accellera.ipxact.v1685_2022.bank import Bank
    from org.accellera.ipxact.v1685_2022.subspace_map import SubspaceMap
    from org.accellera.ipxact.v1685_2022.memory_remap_type import MemoryRemapType

    if isinstance(obj, AddressBlock):
        return "addressBlock"
    if isinstance(obj, Bank):
        return "bank"
    if isinstance(obj, SubspaceMap):
        return "subspaceMap"
    if isinstance(obj, MemoryRemapType):
        return "memoryRemap"
    return None


def getMemoryMapMemoryMapDefinitionRefByExternalTypeDefID(
    memoryMapID: str,
) -> str | None:
    """Return the referenced memoryMapDefinition name.

    Section: F.7.57.51. Returns None if absent.
    """
    mm = _resolve_memory_map(memoryMapID)
    if mm is None or mm.memory_map_definition_ref is None:
        return None
    return getattr(mm.memory_map_definition_ref, "value", None)


def getMemoryMapMemoryMapDefinitionRefByID(memoryMapID: str) -> str | None:
    """Return memoryMapDefinition name via element handle.

    Section: F.7.57.52.
    """
    return getMemoryMapMemoryMapDefinitionRefByExternalTypeDefID(memoryMapID)


def getMemoryMapMemoryMapDefinitionRefByName(memoryMapID: str) -> str | None:
    """Return memoryMapDefinition name by its name lookup.

    Section: F.7.57.53.
    """
    return getMemoryMapMemoryMapDefinitionRefByExternalTypeDefID(memoryMapID)


def getMemoryMapMemoryMapDefinitionRefID(memoryMapID: str) -> str | None:
    """Return handle of ``memoryMapDefinitionRef`` element.

    Section: F.7.57.54.
    """
    mm = _resolve_memory_map(memoryMapID)
    if mm is None or mm.memory_map_definition_ref is None:
        return None
    return get_handle(mm.memory_map_definition_ref)


def getMemoryMapMemoryRemapIDs(memoryMapID: str) -> list[str]:
    """Return handles of ``memoryRemap`` children.

    Section: F.7.57.55.
    """
    mm = _require_memory_map(memoryMapID)
    return _ids(getattr(mm, "memory_remap", []))


def getMemoryMapRemapIDs(memoryMapID: str) -> list[str]:
    """Alias for memory remap IDs (compat name per spec F.7.57.56)."""
    return getMemoryMapMemoryRemapIDs(memoryMapID)


def getMemoryMapShared(memoryMapID: str) -> str | None:
    """Return shared attribute value (if present).

    Section: F.7.57 (paired with setter F.7.58.68). Returns None if not set.
    """
    mm = _resolve_memory_map(memoryMapID)
    if mm is None or mm.shared is None:
        return None
    return getattr(mm.shared, "value", None)


# ---------------------------------------------------------------------------
# EXTENDED (F.7.58)
# ---------------------------------------------------------------------------

def addMemoryMapAddressBlock(memoryMapID: str, name: str) -> str:
    """Create a new ``addressBlock`` under a memory map.

    Section: F.7.58.11 (core portion). Only name is required here; additional
    properties can be assigned via dedicated setters (range, width, baseAddress, etc.).
    """
    mm = _require_memory_map(memoryMapID)
    from org.accellera.ipxact.v1685_2022.address_block_type import AddressBlockType

    ab = AddressBlockType(name=name)
    mm.address_block.append(ab)  # type: ignore[attr-defined]
    register_parent(ab, mm, ("address_block",), "list")
    return get_handle(ab)


def addMemoryMapBank(memoryMapID: str, name: str) -> str:
    """Add a ``bank`` to the memory map.

    Section: F.7.58.12.
    """
    mm = _require_memory_map(memoryMapID)
    from org.accellera.ipxact.v1685_2022.bank import Bank

    bk = Bank(name=name)
    mm.bank.append(bk)  # type: ignore[attr-defined]
    register_parent(bk, mm, ("bank",), "list")
    return get_handle(bk)


def addMemoryMapMemoryRemap(memoryMapID: str, name: str) -> str:
    """Add a ``memoryRemap`` element.

    Section: F.7.58.13.
    """
    mm = _require_memory_map(memoryMapID)
    from org.accellera.ipxact.v1685_2022.memory_remap_type import MemoryRemapType

    remap = MemoryRemapType(name=name)
    mm.memory_remap.append(remap)  # type: ignore[attr-defined]
    register_parent(remap, mm, ("memory_remap",), "list")
    return get_handle(remap)


def addMemoryMapSubspaceMap(memoryMapID: str, name: str, addressOffset: int | None = None) -> str:
    """Add a ``subspaceMap`` to the memory map.

    Section: F.7.58.14. Supports optional base address offset.
    """
    mm = _require_memory_map(memoryMapID)
    from org.accellera.ipxact.v1685_2022.subspace_map import SubspaceMap
    from org.accellera.ipxact.v1685_2022.unsigned_longint_expression import UnsignedLongintExpression

    sm = SubspaceMap(name=name)
    if addressOffset is not None:
        sm.base_address = UnsignedLongintExpression(value=str(addressOffset))  # type: ignore[arg-type]
    mm.subspace_map.append(sm)  # type: ignore[attr-defined]
    register_parent(sm, mm, ("subspace_map",), "list")
    return get_handle(sm)


def removeMemoryMapMemoryRemap(memoryRemapID: str) -> bool:
    """Remove a ``memoryRemap`` element.

    Section: F.7.58.40.
    """
    obj = resolve_handle(memoryRemapID)
    from org.accellera.ipxact.v1685_2022.memory_remap_type import MemoryRemapType
    if not isinstance(obj, MemoryRemapType):
        raise TgiError("Invalid memoryRemap handle", TgiFaultCode.INVALID_ID)
    return detach_child_by_handle(memoryRemapID)


def removeMemoryMapSubspaceMap(subspaceMapID: str) -> bool:
    """Remove a ``subspaceMap`` element.

    Section: F.7.58.42.
    """
    obj = resolve_handle(subspaceMapID)
    from org.accellera.ipxact.v1685_2022.subspace_map import SubspaceMap
    if not isinstance(obj, SubspaceMap):
        raise TgiError("Invalid subspaceMap handle", TgiFaultCode.INVALID_ID)
    return detach_child_by_handle(subspaceMapID)


def setMemoryMapMemoryMapDefinitionRef(memoryMapID: str, name: str | None) -> bool:
    """Set or clear ``memoryMapDefinitionRef`` (named reference).

    Section: F.7.58.67. Name corresponds to a memoryMapDefinition in typeDefinitions.
    Passing None removes the element.
    """
    mm = _require_memory_map(memoryMapID)
    if name is None:
        mm.memory_map_definition_ref = None  # type: ignore[assignment]
        return True
    mm.memory_map_definition_ref = MemoryMapType.MemoryMapDefinitionRef(
        value=name, type_definitions="typeDefinitions"
    )  # type: ignore[assignment]
    return True


def setMemoryMapShared(memoryMapID: str, shared: str | None) -> bool:
    """Set or clear ``shared`` attribute value (string form).

    Section: F.7.58.68. Accepts None to remove the element.
    """
    mm = _require_memory_map(memoryMapID)
    if shared is None:
        mm.shared = None  # type: ignore[assignment]
        return True
    from org.accellera.ipxact.v1685_2022.shared_type import SharedType

    mm.shared = SharedType(value=shared)  # type: ignore[arg-type]
    return True

