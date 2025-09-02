"""Core TGI in-memory infrastructure for IP-XACT 1685-2022.

Central utilities: handle allocation, handle resolution, VLNV registry, and
minimal fault/exception scaffolding.  This intentionally avoids dependencies
outside the standard library.
"""
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from threading import RLock
from typing import Any

__all__ = [
    "TgiFaultCode",
    "TgiError",
    "HandleManager",
    "get_handle",
    "resolve_handle",
    "register_parent",
    "get_parent_info",
    "detach_child_by_handle",
    "VLNV",
    "vlnv_to_tuple",
    "RegisteredElement",
    "VlnvRegistry",
    "registry",
]


class TgiFaultCode(str):
    """Subset of TGI fault codes (expand as coverage grows)."""

    INTERNAL_ERROR = "INTERNAL_ERROR"
    NOT_FOUND = "NOT_FOUND"
    INVALID_ID = "INVALID_ID"
    INVALID_ARGUMENT = "INVALID_ARGUMENT"
    ALREADY_EXISTS = "ALREADY_EXISTS"


class TgiError(RuntimeError):
    """Base exception with a TGI fault code."""

    def __init__(self, message: str, fault_code: str = TgiFaultCode.INTERNAL_ERROR) -> None:  # noqa: D401
        super().__init__(message)
        self.fault_code = fault_code


@dataclass(slots=True)
class _ParentInfo:
    parent_handle: str
    path: tuple[str, ...]
    container: str  # 'list' or 'single'


class HandleManager:
    """Allocate & resolve opaque handles for Python objects."""
    def __init__(self) -> None:
        """Initialize internal maps and locking primitives."""
        self._lock = RLock()
        self._next = 1
        self._handle_to_obj: dict[str, Any] = {}
        self._obj_to_handle: dict[int, str] = {}
        self._parent: dict[int, _ParentInfo] = {}

    def get(self, obj: Any) -> str:
        oid = id(obj)
        with self._lock:
            existing = self._obj_to_handle.get(oid)
            if existing:
                return existing
            handle = f"h{self._next:08x}"
            self._next += 1
            self._obj_to_handle[oid] = handle
            self._handle_to_obj[handle] = obj
            return handle

    def resolve(self, handle: str) -> Any | None:
        return self._handle_to_obj.get(handle)

    def forget(self, handle: str) -> bool:
        with self._lock:
            obj = self._handle_to_obj.pop(handle, None)
            if obj is None:
                return False
            self._obj_to_handle.pop(id(obj), None)
            self._parent.pop(id(obj), None)
            return True

    def register_parent(self, child: Any, parent: Any, path: tuple[str, ...], container: str) -> None:
        with self._lock:
            self._parent[id(child)] = _ParentInfo(
                parent_handle=self.get(parent),
                path=path,
                container=container,
            )

    def get_parent_info(self, child_handle: str) -> "_ParentInfo | None":
        obj = self._handle_to_obj.get(child_handle)
        return None if obj is None else self._parent.get(id(obj))

    def detach_child_by_handle(self, child_handle: str) -> bool:
        info = self.get_parent_info(child_handle)
        if info is None:
            return False
        parent_obj = self._handle_to_obj.get(info.parent_handle)
        if parent_obj is None:
            return False
        owner = parent_obj
        for attr in info.path[:-1]:
            owner = getattr(owner, attr, None)
            if owner is None:
                return False
        final_attr = info.path[-1] if info.path else None
        if info.container == "single":
            if final_attr and getattr(owner, final_attr, None) is self._handle_to_obj.get(child_handle):
                setattr(owner, final_attr, None)
                self.forget(child_handle)
                return True
            return False
        if info.container == "list":
            if not final_attr:
                return False
            lst = getattr(owner, final_attr, None)
            if not isinstance(lst, list):
                return False
            obj = self._handle_to_obj.get(child_handle)
            try:
                lst.remove(obj)
            except ValueError:
                return False
            self.forget(child_handle)
            return True
        return False


## _ParentInfo defined above HandleManager


_HANDLE_MANAGER = HandleManager()


def get_handle(obj: Any) -> str:
    """Return (and allocate if new) handle for ``obj``."""
    return _HANDLE_MANAGER.get(obj)


def resolve_handle(handle: str) -> Any | None:
    """Return underlying object or ``None`` if unknown."""
    return _HANDLE_MANAGER.resolve(handle)


def register_parent(child: Any, parent: Any, path: tuple[str, ...], container: str) -> None:
    """Public helper to register parent relationship (thin wrapper)."""
    _HANDLE_MANAGER.register_parent(child, parent, path, container)


def get_parent_info(child_handle: str) -> _ParentInfo | None:  # pragma: no cover - thin wrapper
    return _HANDLE_MANAGER.get_parent_info(child_handle)


def detach_child_by_handle(child_handle: str) -> bool:  # pragma: no cover - thin wrapper
    return _HANDLE_MANAGER.detach_child_by_handle(child_handle)


VLNV = tuple[str, str, str, str]


def vlnv_to_tuple(vlnv_like: Sequence[str] | str) -> VLNV:
    """Normalize input to a 4-item VLNV tuple.

    Accepts either:
    - A sequence of four strings: (vendor, library, name, version)
    - A single string delimited by ';' or ':' (e.g. "vendor;library;name;version"
      or "vendor:library:name:version")

    Raises:
        TgiError: If the input cannot be parsed as exactly four parts.
    """
    # String form: try ';' first, then ':' as a fallback
    if isinstance(vlnv_like, str):
        s = vlnv_like.strip()
        parts = [p.strip() for p in s.split(";")]
        if len(parts) != 4:
            parts = [p.strip() for p in s.split(":")]
        if len(parts) != 4:
            raise TgiError(
                "VLNV must be vendor, library, name, version",
                TgiFaultCode.INVALID_ARGUMENT,
            )
        return tuple(parts)  # type: ignore[return-value]

    # Sequence form
    if len(vlnv_like) != 4:
        raise TgiError("VLNV must be vendor, library, name, version", TgiFaultCode.INVALID_ARGUMENT)
    return tuple(vlnv_like)  # type: ignore[return-value]


@dataclass(slots=True)
class RegisteredElement:
    """Metadata describing a registry entry."""

    vlnv: VLNV
    root: Any
    file_name: str | None = None


class VlnvRegistry:
    """In-memory VLNV <-> object registry."""

    def __init__(self) -> None:
        """Create empty registry structures."""
        self._lock = RLock()
        self._by_vlnv: dict[VLNV, RegisteredElement] = {}
        self._by_handle: dict[str, RegisteredElement] = {}

    def register(
        self,
        element: Any,
        vlnv_like: Sequence[str] | str,
        file_name: str | None = None,
        replace: bool = False,
    ) -> bool:
        """Register (or optionally replace) the VLNV mapping for an element.

        Args:
            element: Root model object.
            vlnv_like: VLNV as a sequence of (vendor, library, name, version)
                or a single string delimited by ';' or ':'.
            file_name: Optional file name the object originated from.
            replace: If True, replace existing entry silently.

        Returns:
            True on success.
        """
        vlnv = vlnv_to_tuple(vlnv_like)
        handle = get_handle(element)
        with self._lock:
            exists = vlnv in self._by_vlnv
            if exists and not replace:
                raise TgiError("VLNV already registered", TgiFaultCode.ALREADY_EXISTS)
            entry = RegisteredElement(vlnv=vlnv, root=element, file_name=file_name)
            self._by_vlnv[vlnv] = entry
            self._by_handle[handle] = entry
            return True

    def unregister(self, vlnv_like: Sequence[str] | str) -> bool:
        """Remove an existing VLNV mapping.

        Args:
            vlnv_like: (vendor, library, name, version)

        Returns:
            True if an entry was removed, else False.
        """
        vlnv = vlnv_to_tuple(vlnv_like)
        with self._lock:
            entry = self._by_vlnv.pop(vlnv, None)
            if entry is None:
                return False
            self._by_handle.pop(get_handle(entry.root), None)
            return True

    def get_id(self, vlnv_like: Sequence[str] | str) -> str | None:
        """Return handle for VLNV if registered else ``None``."""
        vlnv = vlnv_to_tuple(vlnv_like)
        entry = self._by_vlnv.get(vlnv)
        return get_handle(entry.root) if entry else None

    def get_vlnv(self, handle: str) -> VLNV | None:
        """Return VLNV tuple for a registered handle else ``None``."""
        entry = self._by_handle.get(handle)
        return entry.vlnv if entry else None

    def iter_by_predicate(self, predicate) -> Iterable[str]:  # predicate(root) -> bool
        """Yield handles whose root object satisfies ``predicate``.

        Args:
            predicate: Callable taking the root object and returning bool.

        Yields:
            Handles for each matching element.
        """
        with self._lock:
            for entry in self._by_vlnv.values():
                try:
                    if predicate(entry.root):
                        yield get_handle(entry.root)
                except Exception:  # pragma: no cover
                    continue


registry = VlnvRegistry()
