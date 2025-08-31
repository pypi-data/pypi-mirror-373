# ruff: noqa: I001
"""Address space category TGI functions (IEEE 1685-2022).

Implements BASE (F.7.11) and EXTENDED (F.7.12) Address space functions.
Only the 2022 schema is supported. Functions raise :class:`TgiError` with
``TgiFaultCode.INVALID_ID`` for invalid handles and ``TgiFaultCode.INVALID_ARGUMENT``
for semantic violations.

Returned numeric getters follow the project convention of returning ``int | None``
for resolved numeric value and separate *Expression* getters returning the (string)
expression as ``str | None``. ID getters return a child handle or ``None`` and list
traversal getters return an empty list if no children of the requested type exist.

Creation / mutation helpers create missing optional container elements where
allowed by the schema.
"""

from org.accellera.ipxact.v1685_2022 import AddressSpaces
from org.accellera.ipxact.v1685_2022.address_spaces import AddressSpaces as AddressSpacesClass  # noqa: F401  (retained for potential future use)
from org.accellera.ipxact.v1685_2022.local_memory_map_type import LocalMemoryMapType
from org.accellera.ipxact.v1685_2022.unsigned_longint_expression import (
    UnsignedLongintExpression,
)
from org.accellera.ipxact.v1685_2022.unsigned_positive_int_expression import (
    UnsignedPositiveIntExpression,
)
from org.accellera.ipxact.v1685_2022.unsigned_positive_longint_expression import (
    UnsignedPositiveLongintExpression,
)

from .core import (
    TgiError,
    TgiFaultCode,
    get_handle,
    resolve_handle,
    register_parent,
    detach_child_by_handle,
)

__all__ = [  # BASE + EXTENDED exports
    # BASE (F.7.11)
    "getAddressSpaceAddressUnitBits",
    "getAddressSpaceAddressUnitBitsExpression",
    "getAddressSpaceAddressUnitBitsID",
    "getAddressSpaceLocalMemoryMapID",
    "getAddressSpaceRange",
    "getAddressSpaceRangeExpression",
    "getAddressSpaceRangeID",
    "getAddressSpaceSegmentIDs",
    "getAddressSpaceWidth",
    "getAddressSpaceWidthExpression",
    "getAddressSpaceWidthID",
    "getAliasOfAddressSpaceRefByName",
    "getAliasOfAddressSpaceRefID",
    "getLocalMemoryMapAddressBlockIDs",
    "getLocalMemoryMapBankIDs",
    "getRegionAddressOffset",
    "getRegionAddressOffsetExpression",
    "getRegionAddressOffsetID",
    "getRegionRange",
    "getRegionRangeExpression",
    "getRegionRangeID",
    # EXTENDED (F.7.12)
    "addAddressSpaceSegment",
    "addExecutableImageFileSetRef",
    "addLocalMemoryMapAddressBlock",
    "removeAddressSpaceAddressUnitBits",
    "removeAddressSpaceLocalMemoryMap",
    "removeAddressSpaceSegment",
    "removeExecutableImageFileSetRef",
    "removeLinkerCommandFileGenerator",
    "removeLocalMemoryMapAddressBlock",
    "removeLocalMemoryMapBank",
    "setAddressSpaceAddressUnitBits",
    "setAddressSpaceLocalMemoryMap",
    "setAddressSpaceRange",
    "setAddressSpaceWidth",
    "setSegmentAddressOffset",
    "setSegmentRange",
]


# ----------------------------------------------------------------------------
# Helpers (non-spec)
# ----------------------------------------------------------------------------

def _resolve_address_space(addressSpaceID: str) -> AddressSpaces.AddressSpace | None:
    """Resolve a handle to an ``addressSpace`` element.

    Helper (non-spec) used internally by Address space TGI functions.

    Args:
        addressSpaceID: Handle referencing an ``addressSpace`` element.

    Returns:
        AddressSpaces.AddressSpace | None: Resolved object or ``None`` if the
        handle does not reference the expected type.
    """
    obj = resolve_handle(addressSpaceID)
    if isinstance(obj, AddressSpaces.AddressSpace):  # type: ignore[attr-defined]
        return obj
    return None


def _resolve_segment(segmentID: str) -> AddressSpaces.AddressSpace.Segments.Segment | None:  # type: ignore[return-type]
    """Resolve a handle to a ``segment`` element.

    Helper (non-spec).

    Args:
        segmentID: Handle referencing a ``segment`` element of an addressSpace.

    Returns:
        AddressSpaces.AddressSpace.Segments.Segment | None: Resolved segment or
        ``None`` if the handle is invalid / different type.
    """
    obj = resolve_handle(segmentID)
    if isinstance(obj, AddressSpaces.AddressSpace.Segments.Segment):  # type: ignore[attr-defined]
        return obj
    return None


def _resolve_local_memory_map(localMemoryMapID: str) -> LocalMemoryMapType | None:
    """Resolve a handle to a ``localMemoryMap`` element.

    Helper (non-spec).

    Args:
        localMemoryMapID: Handle referencing a ``localMemoryMap``.

    Returns:
        LocalMemoryMapType | None: Resolved object or ``None`` when invalid.
    """
    obj = resolve_handle(localMemoryMapID)
    return obj if isinstance(obj, LocalMemoryMapType) else None


# ----------------------------------------------------------------------------
# BASE (F.7.11)
# ----------------------------------------------------------------------------

def getAddressSpaceAddressUnitBits(addressSpaceID: str) -> int | None:
    """Get the evaluated integer value of ``addressUnitBits``.

    Section: F.7.11.1.

    Args:
        addressSpaceID: Handle referencing an ``addressSpace`` element.

    Returns:
        int | None: Evaluated numeric value, or ``None`` when the element is
        absent or not numerically evaluable.

    Raises:
        TgiError: If ``addressSpaceID`` is invalid.
    """
    as_ = _resolve_address_space(addressSpaceID)
    if as_ is None:
        raise TgiError("Invalid addressSpace handle", TgiFaultCode.INVALID_ID)
    aub = getattr(as_, "address_unit_bits", None)
    if aub is None:
        return None
    try:
        return int(getattr(aub, "value", None))  # type: ignore[arg-type]
    except Exception:  # pragma: no cover
        return None


def getAddressSpaceAddressUnitBitsExpression(addressSpaceID: str) -> str | None:
    """Get the (string) expression of ``addressUnitBits``.

    Section: F.7.11.2.

    Args:
        addressSpaceID: Handle of the parent addressSpace.

    Returns:
        str | None: Original expression string (not evaluated) or ``None`` if
        absent.

    Raises:
        TgiError: If ``addressSpaceID`` is invalid.
    """
    as_ = _resolve_address_space(addressSpaceID)
    if as_ is None:
        raise TgiError("Invalid addressSpace handle", TgiFaultCode.INVALID_ID)
    aub = getattr(as_, "address_unit_bits", None)
    return getattr(aub, "value", None) if aub is not None else None


def getAddressSpaceAddressUnitBitsID(addressSpaceID: str) -> str | None:
    """Get the handle of the ``addressUnitBits`` element.

    Section: F.7.11.3.

    Args:
        addressSpaceID: Handle referencing an addressSpace.

    Returns:
        str | None: Child handle or ``None`` if element absent.

    Raises:
        TgiError: If the parent handle is invalid.
    """
    as_ = _resolve_address_space(addressSpaceID)
    if as_ is None:
        raise TgiError("Invalid addressSpace handle", TgiFaultCode.INVALID_ID)
    aub = getattr(as_, "address_unit_bits", None)
    return get_handle(aub) if aub is not None else None


def getAddressSpaceLocalMemoryMapID(addressSpaceID: str) -> str | None:
    """Get the handle of the ``localMemoryMap`` element.

    Section: F.7.11.4.

    Args:
        addressSpaceID: Handle referencing an addressSpace.

    Returns:
        str | None: Handle of the ``localMemoryMap`` child or ``None`` if absent.

    Raises:
        TgiError: If the parent handle is invalid.
    """
    as_ = _resolve_address_space(addressSpaceID)
    if as_ is None:
        raise TgiError("Invalid addressSpace handle", TgiFaultCode.INVALID_ID)
    lmm = getattr(as_, "local_memory_map", None)
    return get_handle(lmm) if lmm is not None else None


def _range_numeric(expr_obj) -> int | None:  # helper
    if expr_obj is None:
        return None
    try:
        return int(getattr(expr_obj, "value", None))  # type: ignore[arg-type]
    except Exception:  # pragma: no cover
        return None


def getAddressSpaceRange(addressSpaceID: str) -> int | None:
    """Get evaluated numeric value of ``range``.

    Section: F.7.11.5.

    Args:
        addressSpaceID: Handle of the addressSpace.

    Returns:
        int | None: Numeric value or ``None`` if absent or not evaluable.

    Raises:
        TgiError: If the addressSpace handle is invalid.
    """
    as_ = _resolve_address_space(addressSpaceID)
    if as_ is None:
        raise TgiError("Invalid addressSpace handle", TgiFaultCode.INVALID_ID)
    return _range_numeric(getattr(as_, "range", None))


def getAddressSpaceRangeExpression(addressSpaceID: str) -> str | None:
    """Get expression string for ``range``.

    Section: F.7.11.6.

    Args:
        addressSpaceID: Address space handle.

    Returns:
        str | None: Expression or ``None`` if absent.

    Raises:
        TgiError: If handle invalid.
    """
    as_ = _resolve_address_space(addressSpaceID)
    if as_ is None:
        raise TgiError("Invalid addressSpace handle", TgiFaultCode.INVALID_ID)
    r = getattr(as_, "range", None)
    return getattr(r, "value", None) if r is not None else None


def getAddressSpaceRangeID(addressSpaceID: str) -> str | None:
    """Get handle of the ``range`` element.

    Section: F.7.11.7.

    Args:
        addressSpaceID: Handle referencing an addressSpace.

    Returns:
        str | None: Child handle or ``None`` when absent.

    Raises:
        TgiError: If parent handle invalid.
    """
    as_ = _resolve_address_space(addressSpaceID)
    if as_ is None:
        raise TgiError("Invalid addressSpace handle", TgiFaultCode.INVALID_ID)
    r = getattr(as_, "range", None)
    return get_handle(r) if r is not None else None


def getAddressSpaceSegmentIDs(addressSpaceID: str) -> list[str]:
    """List handles of ``segment`` children.

    Section: F.7.11.8.

    Args:
        addressSpaceID: Address space handle.

    Returns:
        list[str]: List (possibly empty) of segment handles.

    Raises:
        TgiError: If parent handle invalid.
    """
    as_ = _resolve_address_space(addressSpaceID)
    if as_ is None:
        raise TgiError("Invalid addressSpace handle", TgiFaultCode.INVALID_ID)
    segs = getattr(as_, "segments", None)
    if segs is None:
        return []
    return [get_handle(s) for s in getattr(segs, "segment", [])]


def getAddressSpaceWidth(addressSpaceID: str) -> int | None:
    """Get evaluated numeric ``width`` value.

    Section: F.7.11.9.

    Args:
        addressSpaceID: Address space handle.

    Returns:
        int | None: Numeric width or ``None`` if absent or not evaluable.

    Raises:
        TgiError: If handle invalid.
    """
    as_ = _resolve_address_space(addressSpaceID)
    if as_ is None:
        raise TgiError("Invalid addressSpace handle", TgiFaultCode.INVALID_ID)
    w = getattr(as_, "width", None)
    if w is None:
        return None
    try:
        return int(getattr(w, "value", None))  # type: ignore[arg-type]
    except Exception:  # pragma: no cover
        return None


def getAddressSpaceWidthExpression(addressSpaceID: str) -> str | None:
    """Get expression string for ``width``.

    Section: F.7.11.10.

    Args:
        addressSpaceID: Address space handle.

    Returns:
        str | None: Expression or ``None`` when absent.

    Raises:
        TgiError: If handle invalid.
    """
    as_ = _resolve_address_space(addressSpaceID)
    if as_ is None:
        raise TgiError("Invalid addressSpace handle", TgiFaultCode.INVALID_ID)
    w = getattr(as_, "width", None)
    return getattr(w, "value", None) if w is not None else None


def getAddressSpaceWidthID(addressSpaceID: str) -> str | None:
    """Get handle of the ``width`` element.

    Section: F.7.11.11.

    Args:
        addressSpaceID: Address space handle.

    Returns:
        str | None: Child handle or ``None`` if absent.

    Raises:
        TgiError: If parent handle invalid.
    """
    as_ = _resolve_address_space(addressSpaceID)
    if as_ is None:
        raise TgiError("Invalid addressSpace handle", TgiFaultCode.INVALID_ID)
    w = getattr(as_, "width", None)
    return get_handle(w) if w is not None else None


def getAliasOfAddressSpaceRefByName(addressSpaceID: str) -> str | None:  # F.7.11.12
    """Get the name of the referenced addressSpace when this one is an alias.

    Section: F.7.11.12.

    Note:
        The 2022 generated schema currently exposes no ``aliasOf`` element for
        addressSpace; this function therefore returns ``None`` (stub).

    Args:
        addressSpaceID: Address space handle (validated for existence only).

    Returns:
        str | None: Referenced addressSpace name or ``None`` (schema gap).
    """
    _ = _resolve_address_space(addressSpaceID)  # validation
    if _ is None:
        raise TgiError("Invalid addressSpace handle", TgiFaultCode.INVALID_ID)
    return None


def getAliasOfAddressSpaceRefID(addressSpaceID: str) -> str | None:  # F.7.11.13
    """Get the handle of the alias reference element.

    Section: F.7.11.13.

    Note:
        Not present in current schema; always returns ``None`` (stub).

    Args:
        addressSpaceID: Address space handle (validated for existence).

    Returns:
        str | None: Always ``None`` until schema models ``aliasOf``.
    """
    _ = _resolve_address_space(addressSpaceID)
    if _ is None:
        raise TgiError("Invalid addressSpace handle", TgiFaultCode.INVALID_ID)
    return None


def getLocalMemoryMapAddressBlockIDs(localMemoryMapID: str) -> list[str]:
    """List ``addressBlock`` handles in a localMemoryMap.

    Section: F.7.11.14.

    Args:
        localMemoryMapID: Handle referencing a ``localMemoryMap``.

    Returns:
        list[str]: Handles of contained ``addressBlock`` elements (empty if none).

    Raises:
        TgiError: If handle invalid.
    """
    lmm = _resolve_local_memory_map(localMemoryMapID)
    if lmm is None:
        raise TgiError("Invalid localMemoryMap handle", TgiFaultCode.INVALID_ID)
    return [get_handle(ab) for ab in getattr(lmm, "address_block", [])]


def getLocalMemoryMapBankIDs(localMemoryMapID: str) -> list[str]:
    """List bank handles within a localMemoryMap.

    Section: F.7.11.15.

    Args:
        localMemoryMapID: Handle referencing a ``localMemoryMap``.

    Returns:
        list[str]: Bank handles (empty list if none present).

    Raises:
        TgiError: If handle invalid.
    """
    lmm = _resolve_local_memory_map(localMemoryMapID)
    if lmm is None:
        raise TgiError("Invalid localMemoryMap handle", TgiFaultCode.INVALID_ID)
    return [get_handle(b) for b in getattr(lmm, "bank", [])]


def getRegionAddressOffset(segmentID: str) -> int | None:
    """Get numeric value of a region (segment) ``addressOffset``.

    Section: F.7.11.16.

    Args:
        segmentID: Handle referencing a ``segment``.

    Returns:
        int | None: Evaluated offset or ``None`` if absent or not evaluable.

    Raises:
        TgiError: If segment handle invalid.
    """
    seg = _resolve_segment(segmentID)
    if seg is None:
        raise TgiError("Invalid segment handle", TgiFaultCode.INVALID_ID)
    ao = getattr(seg, "address_offset", None)
    if ao is None:
        return None
    try:
        return int(getattr(ao, "value", None))  # type: ignore[arg-type]
    except Exception:  # pragma: no cover
        return None


def getRegionAddressOffsetExpression(segmentID: str) -> str | None:
    """Get expression string of a segment ``addressOffset``.

    Section: F.7.11.17.

    Args:
        segmentID: Segment handle.

    Returns:
        str | None: Expression string or ``None`` if missing.

    Raises:
        TgiError: If handle invalid.
    """
    seg = _resolve_segment(segmentID)
    if seg is None:
        raise TgiError("Invalid segment handle", TgiFaultCode.INVALID_ID)
    ao = getattr(seg, "address_offset", None)
    return getattr(ao, "value", None) if ao is not None else None


def getRegionAddressOffsetID(segmentID: str) -> str | None:
    """Get handle of the segment ``addressOffset`` element.

    Section: F.7.11.18.

    Args:
        segmentID: Segment handle.

    Returns:
        str | None: Child handle or ``None`` when element absent.

    Raises:
        TgiError: If handle invalid.
    """
    seg = _resolve_segment(segmentID)
    if seg is None:
        raise TgiError("Invalid segment handle", TgiFaultCode.INVALID_ID)
    ao = getattr(seg, "address_offset", None)
    return get_handle(ao) if ao is not None else None


def getRegionRange(segmentID: str) -> int | None:
    """Get numeric value of a segment ``range``.

    Section: F.7.11.19.

    Args:
        segmentID: Segment handle.

    Returns:
        int | None: Numeric range value or ``None`` if absent/not evaluable.

    Raises:
        TgiError: If handle invalid.
    """
    seg = _resolve_segment(segmentID)
    if seg is None:
        raise TgiError("Invalid segment handle", TgiFaultCode.INVALID_ID)
    r = getattr(seg, "range", None)
    if r is None:
        return None
    try:
        return int(getattr(r, "value", None))  # type: ignore[arg-type]
    except Exception:  # pragma: no cover
        return None


def getRegionRangeExpression(segmentID: str) -> str | None:
    """Get expression string for a segment ``range``.

    Section: F.7.11.20.

    Args:
        segmentID: Segment handle.

    Returns:
        str | None: Expression or ``None`` if element absent.

    Raises:
        TgiError: If handle invalid.
    """
    seg = _resolve_segment(segmentID)
    if seg is None:
        raise TgiError("Invalid segment handle", TgiFaultCode.INVALID_ID)
    r = getattr(seg, "range", None)
    return getattr(r, "value", None) if r is not None else None


def getRegionRangeID(segmentID: str) -> str | None:
    """Get handle of the segment ``range`` element.

    Section: F.7.11.21.

    Args:
        segmentID: Segment handle.

    Returns:
        str | None: Child handle or ``None`` when element absent.

    Raises:
        TgiError: If handle invalid.
    """
    seg = _resolve_segment(segmentID)
    if seg is None:
        raise TgiError("Invalid segment handle", TgiFaultCode.INVALID_ID)
    r = getattr(seg, "range", None)
    return get_handle(r) if r is not None else None


# ----------------------------------------------------------------------------
# EXTENDED (F.7.12)
# ----------------------------------------------------------------------------

def addAddressSpaceSegment(addressSpaceID: str, name: str, addressOffsetExpr: str, rangeExpr: str) -> str:
    """Create and append a ``segment`` to an addressSpace.

    Section: F.7.12.1.

    Args:
        addressSpaceID: Parent ``addressSpace`` handle.
        name: New segment name.
        addressOffsetExpr: Expression for ``addressOffset``.
        rangeExpr: Expression for ``range``.

    Returns:
        str: Handle of the newly created segment.

    Raises:
        TgiError: If the parent handle is invalid.
    """
    as_ = _resolve_address_space(addressSpaceID)
    if as_ is None:
        raise TgiError("Invalid addressSpace handle", TgiFaultCode.INVALID_ID)
    if as_.segments is None:
        as_.segments = AddressSpaces.AddressSpace.Segments(segment=[])  # type: ignore[arg-type]
    from org.accellera.ipxact.v1685_2022.unsigned_longint_expression import (
        UnsignedLongintExpression as ULIE,
    )
    from org.accellera.ipxact.v1685_2022.unsigned_positive_longint_expression import (
        UnsignedPositiveLongintExpression as UPLE,
    )
    seg = AddressSpaces.AddressSpace.Segments.Segment(  # type: ignore[attr-defined]
        name=name,
        address_offset=ULIE(value=addressOffsetExpr),  # type: ignore[arg-type]
        range=UPLE(value=rangeExpr),  # type: ignore[arg-type]
    )
    as_.segments.segment.append(seg)  # type: ignore[attr-defined]
    register_parent(seg, as_.segments, ("segment",), "list")
    return get_handle(seg)


def addExecutableImageFileSetRef(addressSpaceID: str, fileSetName: str) -> str | None:  # pragma: no cover - schema gap
    """Add an executableImage ``fileSetRef`` (stub).

    Section: F.7.12.2.

    The 2022 generated schema in this project does not include the executable
    image container; this function therefore validates the parent handle and
    returns ``None``.

    Args:
        addressSpaceID: Address space handle.
        fileSetName: Name of the fileSet to reference (unused in stub).

    Returns:
        None: Always ``None`` until schema support is added.

    Raises:
        TgiError: If the addressSpace handle is invalid.
    """
    if _resolve_address_space(addressSpaceID) is None:
        raise TgiError("Invalid addressSpace handle", TgiFaultCode.INVALID_ID)
    return None


def addLocalMemoryMapAddressBlock(
    localMemoryMapID: str,
    name: str,
    baseAddressExpr: str,
    rangeExpr: str,
    widthExpr: str,
) -> str:
    """Create and append an ``addressBlock`` to a localMemoryMap.

    Section: F.7.12.3.

    Args:
        localMemoryMapID: Parent localMemoryMap handle.
        name: New addressBlock name.
        baseAddressExpr: Expression for baseAddress.
        rangeExpr: Expression for range.
        widthExpr: Expression for width.

    Returns:
        str: Handle of the newly created addressBlock.

    Raises:
        TgiError: If the localMemoryMap handle is invalid.
    """
    lmm = _resolve_local_memory_map(localMemoryMapID)
    if lmm is None:
        raise TgiError("Invalid localMemoryMap handle", TgiFaultCode.INVALID_ID)
    from org.accellera.ipxact.v1685_2022.address_block import AddressBlock
    from org.accellera.ipxact.v1685_2022.base_address import BaseAddress

    ab = AddressBlock(  # type: ignore[call-arg]
        name=name,
        base_address=BaseAddress(value=baseAddressExpr),  # type: ignore[arg-type]
        range=UnsignedPositiveLongintExpression(value=rangeExpr),  # type: ignore[arg-type]
        width=UnsignedPositiveIntExpression(value=widthExpr),  # type: ignore[arg-type]
    )
    lmm.address_block.append(ab)  # type: ignore[attr-defined]
    register_parent(ab, lmm, ("address_block",), "list")
    return get_handle(ab)


def removeAddressSpaceAddressUnitBits(addressSpaceID: str) -> bool:
    """Remove the ``addressUnitBits`` element if present.

    Section: F.7.12.4.

    Args:
        addressSpaceID: Address space handle.

    Returns:
        bool: ``True`` if removed, ``False`` if it was absent.

    Raises:
        TgiError: If handle invalid.
    """
    as_ = _resolve_address_space(addressSpaceID)
    if as_ is None:
        raise TgiError("Invalid addressSpace handle", TgiFaultCode.INVALID_ID)
    if getattr(as_, "address_unit_bits", None) is None:
        return False
    as_.address_unit_bits = None  # type: ignore[attr-defined]
    return True


def removeAddressSpaceLocalMemoryMap(addressSpaceID: str) -> bool:
    """Remove the ``localMemoryMap`` element if present.

    Section: F.7.12.5.

    Args:
        addressSpaceID: Address space handle.

    Returns:
        bool: ``True`` if removed, else ``False``.

    Raises:
        TgiError: If handle invalid.
    """
    as_ = _resolve_address_space(addressSpaceID)
    if as_ is None:
        raise TgiError("Invalid addressSpace handle", TgiFaultCode.INVALID_ID)
    if getattr(as_, "local_memory_map", None) is None:
        return False
    as_.local_memory_map = None  # type: ignore[attr-defined]
    return True


def removeAddressSpaceSegment(segmentID: str) -> bool:
    """Remove a ``segment`` element.

    Section: F.7.12.6.

    Args:
        segmentID: Segment handle.

    Returns:
        bool: ``True`` if removed, ``False`` if not found.
    """
    seg = _resolve_segment(segmentID)
    if seg is None:
        return False
    return detach_child_by_handle(segmentID)


def removeExecutableImageFileSetRef(fileSetRefID: str) -> bool:  # pragma: no cover - schema gap
    """Remove an executableImage fileSetRef (stub).

    Section: F.7.12.7.

    Returns:
        bool: Always ``False`` (schema gap).
    """
    return False


def removeLinkerCommandFileGenerator(generatorID: str) -> bool:  # pragma: no cover - schema gap
    """Remove a linkerCommandFile generator (stub).

    Section: F.7.12.8.

    Returns:
        bool: Always ``False`` (schema gap).
    """
    return False


def removeLocalMemoryMapAddressBlock(addressBlockID: str) -> bool:
    """Remove an ``addressBlock``.

    Section: F.7.12.9.

    Args:
        addressBlockID: AddressBlock handle.

    Returns:
        bool: ``True`` if removed, ``False`` otherwise.
    """
    obj = resolve_handle(addressBlockID)
    if obj is None:
        return False
    return detach_child_by_handle(addressBlockID)


def removeLocalMemoryMapBank(bankID: str) -> bool:
    """Remove a bank element.

    Section: F.7.12.10.

    Args:
        bankID: Bank handle.

    Returns:
        bool: ``True`` if removed, ``False`` otherwise.
    """
    obj = resolve_handle(bankID)
    if obj is None:
        return False
    return detach_child_by_handle(bankID)


def setAddressSpaceAddressUnitBits(addressSpaceID: str, value: int | str) -> bool:
    """Set or create ``addressUnitBits``.

    Section: F.7.12.11.

    Args:
        addressSpaceID: Address space handle.
        value: Integer or expression string.

    Returns:
        bool: ``True`` on success.

    Raises:
        TgiError: If handle invalid.
    """
    as_ = _resolve_address_space(addressSpaceID)
    if as_ is None:
        raise TgiError("Invalid addressSpace handle", TgiFaultCode.INVALID_ID)
    from org.accellera.ipxact.v1685_2022.address_unit_bits import AddressUnitBits

    as_.address_unit_bits = AddressUnitBits(value=str(value))  # type: ignore[arg-type]
    return True


def setAddressSpaceLocalMemoryMap(addressSpaceID: str, name: str | None = None) -> bool:
    """Create or replace the ``localMemoryMap`` element.

    Section: F.7.12.12.

    Args:
        addressSpaceID: Parent addressSpace handle.
        name: Optional name for the new localMemoryMap.

    Returns:
        bool: ``True`` on success.

    Raises:
        TgiError: If handle invalid.
    """
    as_ = _resolve_address_space(addressSpaceID)
    if as_ is None:
        raise TgiError("Invalid addressSpace handle", TgiFaultCode.INVALID_ID)
    as_.local_memory_map = LocalMemoryMapType(name=name)  # type: ignore[arg-type]
    return True


def setAddressSpaceRange(addressSpaceID: str, value: int | str) -> bool:
    """Set or create the ``range`` element.

    Section: F.7.12.13.

    Args:
        addressSpaceID: Address space handle.
        value: Integer or expression string.

    Returns:
        bool: ``True`` on success.

    Raises:
        TgiError: If handle invalid.
    """
    as_ = _resolve_address_space(addressSpaceID)
    if as_ is None:
        raise TgiError("Invalid addressSpace handle", TgiFaultCode.INVALID_ID)
    as_.range = UnsignedPositiveLongintExpression(value=str(value))  # type: ignore[arg-type]
    return True


def setAddressSpaceWidth(addressSpaceID: str, value: int | str) -> bool:
    """Set or create the ``width`` element.

    Section: F.7.12.14.

    Args:
        addressSpaceID: Address space handle.
        value: Integer or expression string.

    Returns:
        bool: ``True`` on success.

    Raises:
        TgiError: If handle invalid.
    """
    as_ = _resolve_address_space(addressSpaceID)
    if as_ is None:
        raise TgiError("Invalid addressSpace handle", TgiFaultCode.INVALID_ID)
    as_.width = UnsignedPositiveIntExpression(value=str(value))  # type: ignore[arg-type]
    return True


def setSegmentAddressOffset(segmentID: str, value: int | str) -> bool:
    """Set or create a segment's ``addressOffset``.

    Section: F.7.12.15.

    Args:
        segmentID: Segment handle.
        value: Integer or expression string.

    Returns:
        bool: ``True`` on success.

    Raises:
        TgiError: If handle invalid.
    """
    seg = _resolve_segment(segmentID)
    if seg is None:
        raise TgiError("Invalid segment handle", TgiFaultCode.INVALID_ID)
    seg.address_offset = UnsignedLongintExpression(value=str(value))  # type: ignore[arg-type]
    return True


def setSegmentRange(segmentID: str, value: int | str) -> bool:
    """Set or create a segment's ``range`` element.

    Section: F.7.12.16.

    Args:
        segmentID: Segment handle.
        value: Integer or expression string.

    Returns:
        bool: ``True`` on success.

    Raises:
        TgiError: If handle invalid.
    """
    seg = _resolve_segment(segmentID)
    if seg is None:
        raise TgiError("Invalid segment handle", TgiFaultCode.INVALID_ID)
    seg.range = UnsignedPositiveLongintExpression(value=str(value))  # type: ignore[arg-type]
    return True
