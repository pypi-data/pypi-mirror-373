"""Access handle category TGI functions.

Implements BASE (F.7.7) and EXTENDED (F.7.8) access handle functions covering
enumeration of accessHandle elements, indices, slices and viewRef children plus
add/remove/set operations. Access handles appear underneath several IP-XACT
objects (registers, fields, banks, etc.) inside an optional ``accessHandles``
container; this module centralizes traversal and mutation logic.
"""

from collections.abc import Iterable
from typing import Any

from org.accellera.ipxact.v1685_2022 import (
    PortAccessHandle,
    SimpleAccessHandle,
    SlicedAccessHandle,
)

from .core import (
    TgiError,
    TgiFaultCode,
    detach_child_by_handle,
    get_handle,
    register_parent,
    resolve_handle,
)

AccessHandleType = SimpleAccessHandle | SlicedAccessHandle | PortAccessHandle

__all__ = [
    # BASE (F.7.7)
    "getAccessHandleForce",
    "getAccessHandleIDs",
    "getAccessHandleIndicesIDs",
    "getAccessHandlePathSegmentIDs",
    "getAccessHandleSliceIDs",
    "getAccessHandleViewRefIDs",
    # EXTENDED (F.7.8)
    "addAccessHandle",
    "addAccessHandleIndex",
    "addAccessHandlePathSegment",
    "addAccessHandleSlice",
    "addAccessHandleViewRef",
    "removeAccessHandle",
    "removeAccessHandleIndex",
    "removeAccessHandlePathSegment",
    "removeAccessHandleSlice",
    "removeAccessHandleViewRef",
    "setAccessHandleForce",
]


# ---------------------------------------------------------------------------
# Helpers (non-spec)
# ---------------------------------------------------------------------------

def _resolve(accessHandleID: str) -> AccessHandleType | None:
    """Resolve a handle to an accessHandle element.

    Args:
        accessHandleID: Handle referencing a simple/sliced/port accessHandle.

    Returns:
        Resolved object or ``None`` if the handle does not reference one of
        the supported accessHandle types.
    """
    obj = resolve_handle(accessHandleID)
    if isinstance(obj, SimpleAccessHandle | SlicedAccessHandle | PortAccessHandle):
        return obj
    return None


def _ids_from(items: Iterable[Any]) -> list[str]:
    """Return handles for iterable items."""
    return [get_handle(i) for i in items]


def _ensure_port(accessHandleID: str) -> PortAccessHandle:
    """Return a PortAccessHandle or raise.

    Raises:
        TgiError: If the handle is invalid or not a portAccessHandle.
    """
    ah = _resolve(accessHandleID)
    if not isinstance(ah, PortAccessHandle):
        raise TgiError("Access handle is not portAccessHandle", TgiFaultCode.INVALID_ARGUMENT)
    return ah


def _ensure_sliced(accessHandleID: str) -> SlicedAccessHandle:
    """Return a SlicedAccessHandle or raise."""
    ah = _resolve(accessHandleID)
    if not isinstance(ah, SlicedAccessHandle):
        raise TgiError("Access handle is not slicedAccessHandle", TgiFaultCode.INVALID_ARGUMENT)
    return ah


def _ensure_simple(accessHandleID: str) -> SimpleAccessHandle:
    """Return a SimpleAccessHandle or raise."""
    ah = _resolve(accessHandleID)
    if not isinstance(ah, SimpleAccessHandle):
        raise TgiError("Access handle is not simpleAccessHandle", TgiFaultCode.INVALID_ARGUMENT)
    return ah


def _ensure_access_handles_container(parentID: str):  # type: ignore[return-type]
    """Return/create an ``accessHandles`` container for a parent element.

    The parent element types that may own accessHandles share the attribute
    name ``access_handles`` (snake_case generated from schema). We lazily
    allocate the container list wrapper when first needed.
    """
    parent = resolve_handle(parentID)
    if parent is None:
        raise TgiError("Invalid parent handle", TgiFaultCode.INVALID_ID)
    # AccessHandles container classes differ by parent type; we attempt to
    # discover a nested "AccessHandles" dataclass via attribute.
    if getattr(parent, "access_handles", None) is None:
        # Try to locate nested AccessHandles type on the parent class.
        ah_cls = None
        for name in ["AccessHandles", "accessHandles", "access_handles"]:
            ah_cls = getattr(type(parent), name, None)
            if ah_cls is not None:
                break
        if ah_cls is None:
            raise TgiError("Parent does not support accessHandles", TgiFaultCode.INVALID_ARGUMENT)
        parent.access_handles = ah_cls(access_handle=[])  # type: ignore[attr-defined, arg-type]
    return parent.access_handles


def _append_and_register(container, element, list_attr: tuple[str, ...]):  # type: ignore[no-untyped-def]
    """Append element to container list attribute and register parent."""
    getattr(container, list_attr[-1]).append(element)
    register_parent(element, container, list_attr, "list")


# ---------------------------------------------------------------------------
# BASE (F.7.7)
# ---------------------------------------------------------------------------

def getAccessHandleForce(accessHandleID: str) -> bool | None:
    """Return the ``force`` attribute of a port/sliced handle.

    Section: F.7.7.1.

    Args:
        accessHandleID: Handle of a portAccessHandle or slicedAccessHandle.

    Returns:
        Boolean force value or ``None`` if the handle is simpleAccessHandle
        (which lacks the attribute) or the attribute is absent.
    """
    ah = _resolve(accessHandleID)
    if ah is None:
        raise TgiError("Invalid accessHandle handle", TgiFaultCode.INVALID_ID)
    if isinstance(ah, SimpleAccessHandle):
        return None
    return getattr(ah, "force", None)


def getAccessHandleIDs(parentID: str) -> list[str]:
    """Return handles of accessHandle children of a parent.

    Section: F.7.7.2.

    Args:
        parentID: Handle to an element that may own an ``accessHandles`` container.

    Returns:
        List of accessHandle handles (possibly empty).
    """
    parent = resolve_handle(parentID)
    if parent is None:
        raise TgiError("Invalid parent handle", TgiFaultCode.INVALID_ID)
    container = getattr(parent, "access_handles", None)
    if container is None:
        return []
    return [get_handle(a) for a in getattr(container, "access_handle", [])]


def getAccessHandleIndicesIDs(accessHandleID: str) -> list[str]:
    """Return index element handles of a portAccessHandle.

    Section: F.7.7.3.

    Args:
        accessHandleID: Handle referencing a portAccessHandle.

    Returns:
        List of index element handles (empty when none / wrong type).
    """
    ah = _resolve(accessHandleID)
    if not isinstance(ah, PortAccessHandle):
        return []
    if ah.indices is None:
        return []
    return [get_handle(i) for i in getattr(ah.indices, "index", [])]


def getAccessHandlePathSegmentIDs(accessHandleID: str) -> list[str]:
    """Return pathSegment handles of a simpleAccessHandle.

    Section: F.7.7.4.

    Args:
        accessHandleID: Handle referencing a simpleAccessHandle.

    Returns:
        List of pathSegment handles (empty when none / different type).
    """
    ah = _resolve(accessHandleID)
    if not isinstance(ah, SimpleAccessHandle):
        return []
    ps = ah.path_segments
    if ps is None:
        return []
    return [get_handle(psg) for psg in getattr(ps, "path_segment", [])]


def getAccessHandleSliceIDs(accessHandleID: str) -> list[str]:
    """Return slice handles of a portAccessHandle or slicedAccessHandle.

    Section: F.7.7.5.

    Args:
        accessHandleID: Handle referencing a slicedAccessHandle or portAccessHandle.

    Returns:
        List of slice handles (empty when none or unsupported type).
    """
    ah = _resolve(accessHandleID)
    if isinstance(ah, PortAccessHandle | SlicedAccessHandle):
        slices = getattr(ah, "slices", None)
        if slices is None:
            return []
        return [get_handle(s) for s in getattr(slices, "slice", [])]
    return []


def getAccessHandleViewRefIDs(accessHandleID: str) -> list[str]:
    """Return viewRef handles for any accessHandle variant.

    Section: F.7.7.6.

    Args:
        accessHandleID: Handle referencing a simple/sliced/port accessHandle.

    Returns:
        List of viewRef handles (empty if none / invalid type).
    """
    ah = _resolve(accessHandleID)
    if ah is None:
        raise TgiError("Invalid accessHandle handle", TgiFaultCode.INVALID_ID)
    return [get_handle(vr) for vr in getattr(ah, "view_ref", [])]


# ---------------------------------------------------------------------------
# EXTENDED (F.7.8)
# ---------------------------------------------------------------------------

def addAccessHandle(parentID: str, type: str) -> str:  # pragma: no cover - scaffold
    """Add an accessHandle of the requested type.

    Section: F.7.8.1.

    Supported ``type`` strings: ``simple``, ``sliced``, ``port``.

    Args:
        parentID: Handle of element that can own ``accessHandles``.
        type: Variant to create.

    Returns:
        Handle of the created accessHandle.
    """
    container = _ensure_access_handles_container(parentID)
    kind = type.lower()
    if kind not in {"simple", "sliced", "port"}:
        raise TgiError("Unsupported accessHandle type", TgiFaultCode.INVALID_ARGUMENT)
    if kind == "simple":
        ah = SimpleAccessHandle(path_segments=None)  # type: ignore[arg-type]
    elif kind == "sliced":
        from org.accellera.ipxact.v1685_2022.slices_type import SlicesType

        ah = SlicedAccessHandle(slices=SlicesType(slice=[]))  # type: ignore[arg-type]
    else:  # port
        from org.accellera.ipxact.v1685_2022.port_slices_type import PortSlicesType

        ah = PortAccessHandle(slices=PortSlicesType(slice=[]))  # type: ignore[arg-type]
    _append_and_register(container, ah, ("access_handle",))
    return get_handle(ah)


def addAccessHandleIndex(accessHandleID: str, value: str) -> str:  # pragma: no cover - scaffold
    """Add an ``index`` element to a portAccessHandle.

    Section: F.7.8.2.
    """
    ah = _ensure_port(accessHandleID)
    from org.accellera.ipxact.v1685_2022.port_access_handle import PortAccessHandle as PAH

    if ah.indices is None:
        ah.indices = PAH.Indices(index=[])  # type: ignore[arg-type]
    idx = PAH.Indices.Index(value=value)  # type: ignore[arg-type]
    ah.indices.index.append(idx)  # type: ignore[attr-defined]
    register_parent(idx, ah.indices, ("index",), "list")
    return get_handle(idx)


def addAccessHandlePathSegment(accessHandleID: str, value: str) -> str:  # pragma: no cover - scaffold
    """Add a pathSegment to a simpleAccessHandle.

    Section: F.7.8.3.
    """
    ah = _ensure_simple(accessHandleID)
    from org.accellera.ipxact.v1685_2022.path_segment_type import PathSegmentType
    from org.accellera.ipxact.v1685_2022.simple_access_handle import (
        SimpleAccessHandle as SAH,
    )

    if ah.path_segments is None:
        ah.path_segments = SAH.PathSegments(path_segment=[])  # type: ignore[arg-type]
    seg = PathSegmentType(value=value)  # type: ignore[arg-type]
    ah.path_segments.path_segment.append(seg)  # type: ignore[attr-defined]
    register_parent(seg, ah.path_segments, ("path_segment",), "list")
    return get_handle(seg)


def addAccessHandleSlice(accessHandleID: str, value: str) -> str:  # pragma: no cover - scaffold
    """Add a slice element to a port or sliced accessHandle.

    Section: F.7.8.4.
    """
    ah = _resolve(accessHandleID)
    if isinstance(ah, PortAccessHandle):
        from org.accellera.ipxact.v1685_2022.port_slice_type import PortSliceType
        from org.accellera.ipxact.v1685_2022.port_slices_type import PortSlicesType

        if ah.slices is None:
            ah.slices = PortSlicesType(slice=[])  # type: ignore[arg-type]
        sl = PortSliceType(value=value)  # type: ignore[arg-type]
        ah.slices.slice.append(sl)  # type: ignore[attr-defined]
        register_parent(sl, ah.slices, ("slice",), "list")
        return get_handle(sl)
    if isinstance(ah, SlicedAccessHandle):
        from org.accellera.ipxact.v1685_2022.slice_type import SliceType
        from org.accellera.ipxact.v1685_2022.slices_type import SlicesType

        if ah.slices is None:
            ah.slices = SlicesType(slice=[])  # type: ignore[arg-type]
        sl = SliceType(value=value)  # type: ignore[arg-type]
        ah.slices.slice.append(sl)  # type: ignore[attr-defined]
        register_parent(sl, ah.slices, ("slice",), "list")
        return get_handle(sl)
    raise TgiError("Access handle does not support slices", TgiFaultCode.INVALID_ARGUMENT)


def addAccessHandleViewRef(accessHandleID: str, viewName: str) -> str:  # pragma: no cover - scaffold
    """Add a viewRef child to any accessHandle variant.

    Section: F.7.8.5.
    """
    ah = _resolve(accessHandleID)
    if ah is None:
        raise TgiError("Invalid accessHandle handle", TgiFaultCode.INVALID_ID)
    # Each variant defines an inner ViewRef dataclass named ViewRef.
    view_ref_cls = type(ah).ViewRef  # type: ignore[attr-defined]
    vr = view_ref_cls(value=viewName)  # type: ignore[arg-type]
    ah.view_ref.append(vr)  # type: ignore[attr-defined]
    register_parent(vr, ah, ("view_ref",), "list")
    return get_handle(vr)


def removeAccessHandle(accessHandleID: str) -> bool:  # pragma: no cover - scaffold
    """Remove an accessHandle element.

    Section: F.7.8.6.
    """
    if _resolve(accessHandleID) is None:
        return False
    return detach_child_by_handle(accessHandleID)


def removeAccessHandleIndex(indexID: str) -> bool:  # pragma: no cover - scaffold
    """Remove an index element.

    Section: F.7.8.7.
    """
    obj = resolve_handle(indexID)
    if obj is None:
        return False
    return detach_child_by_handle(indexID)


def removeAccessHandlePathSegment(pathSegmentID: str) -> bool:  # pragma: no cover - scaffold
    """Remove a pathSegment element.

    Section: F.7.8.8.
    """
    obj = resolve_handle(pathSegmentID)
    if obj is None:
        return False
    return detach_child_by_handle(pathSegmentID)


def removeAccessHandleSlice(sliceID: str) -> bool:  # pragma: no cover - scaffold
    """Remove a slice element (port/sliced variants).

    Section: F.7.8.9.
    """
    obj = resolve_handle(sliceID)
    if obj is None:
        return False
    return detach_child_by_handle(sliceID)


def removeAccessHandleViewRef(viewRefID: str) -> bool:  # pragma: no cover - scaffold
    """Remove a viewRef element.

    Section: F.7.8.10.
    """
    obj = resolve_handle(viewRefID)
    if obj is None:
        return False
    return detach_child_by_handle(viewRefID)


def setAccessHandleForce(accessHandleID: str, value: bool | None) -> bool:  # pragma: no cover - scaffold
    """Set or clear the force attribute of a sliced/port accessHandle.

    Section: F.7.8.11.

    Args:
        accessHandleID: Handle referencing a slicedAccessHandle or portAccessHandle.
        value: Boolean to set or ``None`` to clear (restore default semantics).

    Returns:
        True on success, False if not applicable.
    """
    ah = _resolve(accessHandleID)
    if isinstance(ah, PortAccessHandle | SlicedAccessHandle):
        if value is None:
            # Represent clearing by setting default True attr (attribute is not
            # optional in generated dataclasses, so emulate absence by default).
            ah.force = True  # type: ignore[attr-defined]
        else:
            ah.force = bool(value)  # type: ignore[attr-defined]
        return True
    return False
