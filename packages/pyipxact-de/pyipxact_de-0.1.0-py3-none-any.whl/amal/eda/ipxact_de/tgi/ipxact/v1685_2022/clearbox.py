"""Clearbox category TGI functions (IEEE 1685-2022).

Implements BASE (F.7.27) and EXTENDED (F.7.28) Clearbox functions.

Provides traversal and manipulation utilities for clearbox elements, clearboxElementRef
and clearboxElementRefLocation structures. Functions raise :class:`TgiError` with
``TgiFaultCode.INVALID_ID`` when a supplied handle does not reference the expected
schema object.
"""

from org.accellera.ipxact.v1685_2022 import (
    ClearboxElementRefType,
    ClearboxElementType,
)

from .core import (
    TgiError,
    TgiFaultCode,
    detach_child_by_handle,
    get_handle,
    register_parent,
    resolve_handle,
)

__all__ = [
    # BASE (F.7.27)
    "getClearboxElementClearboxType",
    "getClearboxElementDriveable",
    "getClearboxElementRefByID",
    "getClearboxElementRefLocationIDs",
    # EXTENDED (F.7.28)
    "addClearboxElementRefLocation",
    "addLocationSlice",
    "removeClearboxElementDriveable",
    "removeClearboxElementRefLocation",
    "setClearboxElementClearboxType",
    "setClearboxElementDriveable",
]


# ---------------------------------------------------------------------------
# Helpers (non-spec)
# ---------------------------------------------------------------------------

def _resolve_clearbox_element(elementID: str) -> ClearboxElementType | None:
    obj = resolve_handle(elementID)
    return obj if isinstance(obj, ClearboxElementType) else None


def _resolve_clearbox_element_ref(refID: str) -> ClearboxElementRefType | None:
    obj = resolve_handle(refID)
    return obj if isinstance(obj, ClearboxElementRefType) else None


def _resolve_location(locationID: str):  # return location or None
    obj = resolve_handle(locationID)
    # Location is an inner class inside clearboxElementRefLocation? We treat generically.
    return obj


def _resolve_ref_location(refLocationID: str):  # generic resolution
    return resolve_handle(refLocationID)


# ---------------------------------------------------------------------------
# BASE (F.7.27)
# ---------------------------------------------------------------------------

def getClearboxElementClearboxType(clearboxElementID: str) -> str | None:
    """Return the ``clearboxType`` value for a clearboxElement.

    Section: F.7.27.1

    Args:
        clearboxElementID: Handle to a clearboxElement element.
    Returns:
        The clearboxType enumeration value as string, or None if not set.
    Raises:
        TgiError: If the handle is invalid.
    """
    el = _resolve_clearbox_element(clearboxElementID)
    if el is None:
        raise TgiError("Invalid clearboxElement handle", TgiFaultCode.INVALID_ID)
    cb = getattr(el, "clearbox_type", None)
    if cb is None:
        return None
    # SimpleClearboxType enum => return its value
    return getattr(cb, "value", cb)


def getClearboxElementDriveable(clearboxElementID: str) -> bool | None:
    """Return the ``driveable`` value for a clearboxElement.

    Section: F.7.27.2

    Args:
        clearboxElementID: Handle to a clearboxElement element.
    Returns:
        Boolean driveable value or None if not present.
    Raises:
        TgiError: If the handle is invalid.
    """
    el = _resolve_clearbox_element(clearboxElementID)
    if el is None:
        raise TgiError("Invalid clearboxElement handle", TgiFaultCode.INVALID_ID)
    return getattr(el, "driveable", None)


def getClearboxElementRefByID(clearboxElementRefID: str) -> str | None:
    """Return handle to the clearboxElement referenced by a clearboxElementRef.

    Section: F.7.27.3

    Args:
        clearboxElementRefID: Handle to a clearboxElementRef element.
    Returns:
        Handle to referenced clearboxElement or None if resolution fails.
    Raises:
        TgiError: If the ref handle is invalid.
    """
    ref = _resolve_clearbox_element_ref(clearboxElementRefID)
    if ref is None:
        raise TgiError("Invalid clearboxElementRef handle", TgiFaultCode.INVALID_ID)
    # Reference by name attribute; search siblings (?) – Without DE index we cannot resolve by name.
    # If the ref already holds a resolved object attribute (implementation dependent), return handle.
    target = getattr(ref, "_resolved_target", None)
    return None if target is None else get_handle(target)


def getClearboxElementRefLocationIDs(clearboxElementRefID: str) -> list[str]:
    """Return handles to all clearboxElementRefLocation elements.

    Section: F.7.27.4

    Args:
        clearboxElementRefID: Handle to a clearboxElementRef element.
    Returns:
        List of handles for each clearboxElementRefLocation.
    Raises:
        TgiError: If the ref handle is invalid.
    """
    ref = _resolve_clearbox_element_ref(clearboxElementRefID)
    if ref is None:
        raise TgiError("Invalid clearboxElementRef handle", TgiFaultCode.INVALID_ID)
    locs = getattr(ref, "clearbox_element_ref_locations", None)
    if locs is None:
        return []
    return [get_handle(loc) for loc in getattr(locs, "clearbox_element_ref_location", [])]


# ---------------------------------------------------------------------------
# EXTENDED (F.7.28)
# ---------------------------------------------------------------------------

def addClearboxElementRefLocation(clearboxElementRefID: str, value: str) -> str:
    """Add a ``clearboxElementRefLocation`` to a clearboxElementRef.

    Section: F.7.28.1

    Args:
        clearboxElementRefID: Handle to a clearboxElementRef element.
        value: Path segment value.
    Returns:
        Handle of the newly added clearboxElementRefLocation.
    Raises:
        TgiError: If the ref handle is invalid.
    """
    ref = _resolve_clearbox_element_ref(clearboxElementRefID)
    if ref is None:
        raise TgiError("Invalid clearboxElementRef handle", TgiFaultCode.INVALID_ID)
    if getattr(ref, "clearbox_element_ref_locations", None) is None:
        # Create container instance (schema inner class may exist; fallback simple object)
        class _Locs:  # lightweight container
            clearbox_element_ref_location = []  # type: ignore[var-annotated]
        ref.clearbox_element_ref_locations = _Locs()  # type: ignore[attr-defined]
    # Location object creation (schema-specific). We synthesize a generic object with 'value'.
    class _Location:  # minimal stand-in if real class not present
        __slots__ = ("value", "slices")
        def __init__(self, value: str):
            self.value = value
            self.slices = []
    loc = _Location(value)
    ref.clearbox_element_ref_locations.clearbox_element_ref_location.append(loc)  # type: ignore[attr-defined]
    register_parent(loc, ref, ("clearbox_element_ref_locations",), "list")
    return get_handle(loc)


def addLocationSlice(locationID: str, value: str) -> str:
    """Add a slice to a Location element.

    Section: F.7.28.2

    Args:
        locationID: Handle to a location element.
        value: Slice value (path segment).
    Returns:
        Handle to the new slice element.
    Raises:
        TgiError: If the location handle is invalid.
    """
    loc = _resolve_location(locationID)
    if loc is None:
        raise TgiError("Invalid location handle", TgiFaultCode.INVALID_ID)
    if not hasattr(loc, "slices"):
        loc.slices = []  # type: ignore[attr-defined]
    class _Slice:
        __slots__ = ("value",)
        def __init__(self, value: str):
            self.value = value
    sl = _Slice(value)
    loc.slices.append(sl)  # type: ignore[attr-defined]
    register_parent(sl, loc, ("slices",), "list")
    return get_handle(sl)


def removeClearboxElementDriveable(clearboxElementID: str) -> bool:
    """Remove the ``driveable`` element from a clearboxElement.

    Section: F.7.28.3

    Args:
        clearboxElementID: Handle to a clearboxElement element.
    Returns:
        True if removed, False if not present or invalid.
    """
    el = _resolve_clearbox_element(clearboxElementID)
    if el is None:
        return False
    if hasattr(el, "driveable") and el.driveable is not None:  # type: ignore[attr-defined]
        try:
            delattr(el, "driveable")
        except Exception:  # pragma: no cover - defensive
            return False
        return True
    return False


def removeClearboxElementRefLocation(clearboxElementRefLocationID: str) -> bool:
    """Remove a clearboxElementRefLocation element.

    Section: F.7.28.4

    Args:
        clearboxElementRefLocationID: Handle to a clearboxElementRefLocation element.
    Returns:
        True if removed, False otherwise.
    """
    return detach_child_by_handle(clearboxElementRefLocationID)


def setClearboxElementClearboxType(clearboxID: str, clearboxType: str) -> bool:
    """Set the clearbox type of a clearbox element.

    Section: F.7.28.5

    Args:
        clearboxID: Handle to a clearboxElement element.
        clearboxType: New clearbox type string.
    Returns:
        True if set, False if not found.
    Raises:
        TgiError: If the handle is invalid.
    """
    el = _resolve_clearbox_element(clearboxID)
    if el is None:
        raise TgiError("Invalid clearboxElement handle", TgiFaultCode.INVALID_ID)
    # Underlying attribute is clearbox_type (enum). We assign raw string; actual enum mapping left to DE.
    el.clearbox_type = clearboxType  # type: ignore[attr-defined]
    return True


def setClearboxElementDriveable(clearboxElementID: str, value: bool) -> bool:
    """Set the driveable value for a clearboxElement.

    Section: F.7.28.6

    Args:
        clearboxElementID: Handle to a clearboxElement element.
        value: Boolean driveable state.
    Returns:
        True if set, False if not found.
    Raises:
        TgiError: If the handle is invalid.
    """
    el = _resolve_clearbox_element(clearboxElementID)
    if el is None:
        raise TgiError("Invalid clearboxElement handle", TgiFaultCode.INVALID_ID)
    el.driveable = value  # type: ignore[attr-defined]
    return True
