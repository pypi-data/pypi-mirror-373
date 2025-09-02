"""Top element category TGI functions (IEEE 1685-2022).

Implements BASE (F.7.79) and EXTENDED (F.7.80) top element functions. The
"top element" represents the container / repository scope from which all
other IP-XACT elements (components, bus definitions, etc.) can be enumerated
or created. BASE traversal getters return empty lists or neutral values when
the provided handle is invalid (tolerant semantics). EXTENDED creation and
edit operations raise :class:`TgiError` with appropriate fault codes for
invalid IDs or arguments.

Because this implementation operates without a backing persistent database,
we treat a *top handle* as any object carrying collections named after the
relevant categories (e.g. ``abstraction_definitions``, ``components``). If
such collections are absent they are initialised on demand for creation
operations. Created objects are minimal, leveraging generated schema classes
when available or ``SimpleNamespace`` fallbacks otherwise.
"""
from collections.abc import Iterable
from types import SimpleNamespace
from typing import Any

from org.accellera.ipxact.v1685_2022 import (
    AbstractionDefinition,
    Abstractor,
    BusDefinition,
    Catalog,
    Component,
    Design,
    DesignConfiguration,
    GeneratorChain,
    TypeDefinitions,
)

from .core import (
    TgiError,
    TgiFaultCode,
    resolve_handle,
    get_handle,
    register_parent,
    registry,
)

__all__ = [
    # BASE (F.7.79)
    "getAbstractionDefIDs",
    "getAbstractorIDs",
    "getBusDefIDs",
    "getCatalogIDs",
    "getComponentIDs",
    "getDesignConfigurationIDs",
    "getDesignIDs",
    "getGeneratorChainIDs",
    "getID",
    "getTypeDefinitionsIDs",
    "getVLNV",
    "getXMLPath",
    # EXTENDED (F.7.80)
    "createAbstractionDef",
    "createAbstractor",
    "createBusDefinition",
    "createCatalog",
    "createComponent",
    "createDesign",
    "createDesignConfiguration",
    "createGeneratorChain",
    "createTypeDefinitions",
    "edit",
    "setXMLPath",
]


# ---------------------------------------------------------------------------
# Helpers (non-spec)
# ---------------------------------------------------------------------------

def _resolve_top(topID: str) -> Any | None:
    """Resolve a top element handle.

    Args:
        topID: Handle of the presumed top element.

    Returns:
        The underlying object or ``None`` if not found.
    """
    obj = resolve_handle(topID)
    return obj


def _collect_ids(container: Any | None, attr: str) -> list[str]:
    """Collect handles for elements of a named list attribute.

    Args:
        container: Parent object (may be ``None``).
        attr: Name of attribute expected to be a list (e.g. ``components``).

    Returns:
        List of child handles (empty if container/attribute absent).
    """
    if container is None or container is False:
        return []
    coll = getattr(container, attr, None)
    if coll is None:
        return []
    if isinstance(coll, list):
        return [get_handle(e) for e in coll]
    # Some generated group classes may wrap list under attribute
    if hasattr(coll, attr[:-1]):  # crude heuristic
        inner = getattr(coll, attr[:-1])
        if isinstance(inner, list):
            return [get_handle(e) for e in inner]
    # Fallback: treat as iterable
    if isinstance(coll, Iterable):
        return [get_handle(e) for e in coll]  # type: ignore[arg-type]
    return []


def _ensure_collection(top: Any, attr: str) -> list[Any]:
    """Return an existing list attribute or create an empty one.

    Args:
        top: Top element object.
        attr: Attribute name for the collection.

    Returns:
        The list instance stored on the object (created if missing).
    """
    existing = getattr(top, attr, None)
    if existing is None:
        new_list: list[Any] = []
        setattr(top, attr, new_list)
        return new_list
    return existing  # type: ignore[return-value]


def _new_or_ns(cls, **kwargs: Any) -> Any:
    """Instantiate *cls* with kwargs or fall back to ``SimpleNamespace``.

    Args:
        cls: Target class (schema generated when available).
        **kwargs: Initialization keyword arguments.

    Returns:
        Instance of ``cls`` or a ``SimpleNamespace`` with the same attributes.
    """
    try:  # pragma: no cover - happy path
        return cls(**kwargs)  # type: ignore[call-arg]
    except Exception:  # pragma: no cover - fallback
        return SimpleNamespace(**kwargs)


# ---------------------------------------------------------------------------
# BASE (F.7.79) traversal & meta
# ---------------------------------------------------------------------------

def getAbstractionDefIDs(topElementID: str) -> list[str]:  # F.7.79.1
    """Return handles of Abstraction Definitions under a top element.

    Tolerant BASE behavior: invalid ``topElementID`` returns ``[]``.
    """
    top = _resolve_top(topElementID)
    return _collect_ids(top, "abstraction_definitions")


def getAbstractorIDs(topElementID: str) -> list[str]:  # F.7.79.2
    """Return handles of Abstractors under a top element (BASE)."""
    top = _resolve_top(topElementID)
    return _collect_ids(top, "abstractors")


def getBusDefIDs(topElementID: str) -> list[str]:  # F.7.79.3
    """Return handles of Bus Definitions (BASE)."""
    top = _resolve_top(topElementID)
    return _collect_ids(top, "bus_definitions")


def _getCatalogIDs_spec(topElementID: str) -> list[str]:  # F.7.79.4
    """Return handles of Catalogs (BASE)."""
    top = _resolve_top(topElementID)
    return _collect_ids(top, "catalogs")


# Non-spec convenience alias required by existing tests exercising
# traversal over globally registered catalogs. Without argument it
# enumerates registered catalog roots (Administrative/Creation layer).
def _getCatalogIDs_noarg() -> list[str]:  # pragma: no cover - thin wrapper
    # Enumerate registered roots that are Catalog instances (or duck-type)
    def _is_catalog(obj: Any) -> bool:
        return obj.__class__.__name__ == "Catalog"

    return list(registry.iter_by_predicate(_is_catalog))


# Preserve backwards compatibility: if called without argument fall back
# to registry enumeration. This maintains spec signature while honoring
# test expectations during development phase.
def getCatalogIDs(*args, **kwargs):  # type: ignore[override]
    """Hybrid traversal.

    Dev-phase convenience: with no arguments enumerate globally
    registered root Catalog handles. With an argument delegate to the
    spec-conformant top-element scoped enumeration.
    """
    if not args and not kwargs:
        return _getCatalogIDs_noarg()
    return _getCatalogIDs_spec(*args, **kwargs)


def getComponentIDs(topElementID: str) -> list[str]:  # F.7.79.5
    """Return handles of Components (BASE)."""
    top = _resolve_top(topElementID)
    return _collect_ids(top, "components")


def getDesignConfigurationIDs(topElementID: str) -> list[str]:  # F.7.79.6
    """Return handles of Design Configurations (BASE)."""
    top = _resolve_top(topElementID)
    return _collect_ids(top, "design_configurations")


def getDesignIDs(topElementID: str) -> list[str]:  # F.7.79.7
    """Return handles of Designs (BASE)."""
    top = _resolve_top(topElementID)
    return _collect_ids(top, "designs")


def getGeneratorChainIDs(topElementID: str) -> list[str]:  # F.7.79.8
    """Return handles of Generator Chains (BASE)."""
    top = _resolve_top(topElementID)
    return _collect_ids(top, "generator_chains")


def getID(elementID):  # F.7.79.9
    """Return element handle (overloaded for VLNV sequences).

    Spec (Top element BASE) defines ``getID(elementID)`` returning the handle
    if valid else ``None``. The *Administrative* category defines
    ``getID(vlnvSequence)`` resolving a VLNV to a handle. To avoid one
    overshadowing the other in the aggregated namespace we implement a
    tolerant polymorphic version here: if *elementID* looks like a 4-length
    string sequence treat it as a VLNV, else treat it as an element handle.

    Args:
        elementID: Either a candidate handle string or a 4-sequence (vendor,
            library, name, version).

    Returns:
        Handle string or ``None`` if resolution fails.
    """
    # VLNV pattern
    if isinstance(elementID, list | tuple) and len(elementID) == 4 and all(
        isinstance(p, str) for p in elementID
    ):
        return registry.get_id(elementID)  # administrative semantics
    if not isinstance(elementID, str):  # not a handle
        return None
    obj = resolve_handle(elementID)
    return None if obj is None else get_handle(obj)


def getTypeDefinitionsIDs(topElementID: str) -> list[str]:  # F.7.79.10
    """Return handles of Type Definitions (BASE)."""
    top = _resolve_top(topElementID)
    return _collect_ids(top, "type_definitions")


def getVLNV(elementID: str):  # F.7.79.11
    """Return VLNV quadruple of an element (BASE).

    If the *handle* refers to a root registered in the global registry we
    delegate to that (ensuring unregistered elements return ``None`` after
    removal). Otherwise we fall back to extracting vendor/library/name/
    version attributes directly and returning a 4-tuple with ``None`` in
    missing positions. Invalid handles return ``(None, None, None, None)``.
    """
    # First attempt registry resolution (administrative semantics)
    reg_vlnv = None
    if isinstance(elementID, str):  # guard for malformed input
        reg_vlnv = registry.get_vlnv(elementID)
    if reg_vlnv is not None:
        return reg_vlnv
    # If the caller passed a handle string that is *not* currently registered
    # administrative semantics expect None (see tests expecting None after
    # unregister). We therefore return None instead of synthesizing from
    # attributes. To access raw attributes callers can still inspect the
    # underlying object via resolve_handle.
    if isinstance(elementID, str):
        return None
    obj = resolve_handle(elementID)
    if obj is None:
        return (None, None, None, None)
    return (
        getattr(obj, "vendor", None),
        getattr(obj, "library", None),
        getattr(obj, "name", None),
        getattr(obj, "version", None),
    )


def getXMLPath(elementID: str) -> str | None:  # F.7.79.12
    """Return XML path for an element or synthesize one from VLNV.

    Synthesis produces ``/vendor:library:name:version`` skipping missing parts.
    Invalid handle returns ``None``.
    """
    obj = resolve_handle(elementID)
    if obj is None:
        return None
    path = getattr(obj, "xml_path", None)
    if path is None:
        vendor, library, name, version = (
            getattr(obj, "vendor", None),
            getattr(obj, "library", None),
            getattr(obj, "name", None),
            getattr(obj, "version", None),
        )
        if name is not None:
            return "/" + ":".join([p for p in (vendor, library, name, version) if p])
    return path


# ---------------------------------------------------------------------------
# EXTENDED (F.7.80) creation & edit
# ---------------------------------------------------------------------------

def createAbstractionDef(topElementID: str, name: str) -> str:  # F.7.80.1
    """Create an Abstraction Definition (EXTENDED).

    Raises:
        TgiError: If the top element handle is invalid.
    """
    top = _resolve_top(topElementID)
    if top is None:
        raise TgiError("Invalid top element handle", TgiFaultCode.INVALID_ID)
    coll = _ensure_collection(top, "abstraction_definitions")
    obj = _new_or_ns(AbstractionDefinition, name=name)
    coll.append(obj)
    register_parent(obj, top, ("abstraction_definitions",), "list")
    return get_handle(obj)


def createAbstractor(topElementID: str, name: str) -> str:  # F.7.80.2
    """Create an Abstractor (EXTENDED)."""
    top = _resolve_top(topElementID)
    if top is None:
        raise TgiError("Invalid top element handle", TgiFaultCode.INVALID_ID)
    coll = _ensure_collection(top, "abstractors")
    obj = _new_or_ns(Abstractor, name=name)
    coll.append(obj)
    register_parent(obj, top, ("abstractors",), "list")
    return get_handle(obj)


def createBusDefinition(topElementID: str, name: str) -> str:  # F.7.80.3
    """Create a Bus Definition (EXTENDED)."""
    top = _resolve_top(topElementID)
    if top is None:
        raise TgiError("Invalid top element handle", TgiFaultCode.INVALID_ID)
    coll = _ensure_collection(top, "bus_definitions")
    obj = _new_or_ns(BusDefinition, name=name)
    coll.append(obj)
    register_parent(obj, top, ("bus_definitions",), "list")
    return get_handle(obj)


def createCatalog(topElementID: str, name: str) -> str:  # F.7.80.4
    """Create a Catalog under a top element (EXTENDED).

    Spec F.7.80.4: Adds a new ``catalog`` child to the given top element and
    returns its handle. Only the top-element scoped creation is supported
    here (root VLNV catalog creation is handled by the Creation category).

    Args:
        topElementID: Handle of the top element.
        name: Catalog name.

    Returns:
        Handle of the newly created Catalog.

    Raises:
        TgiError: If the top element handle is invalid.
    """
    top = _resolve_top(topElementID)
    if top is None:
        raise TgiError("Invalid top element handle", TgiFaultCode.INVALID_ID)
    coll = _ensure_collection(top, "catalogs")
    obj = _new_or_ns(Catalog, name=name)
    coll.append(obj)
    register_parent(obj, top, ("catalogs",), "list")
    return get_handle(obj)


def createComponent(topElementID: str, name: str) -> str:  # F.7.80.5
    """Create a Component (EXTENDED)."""
    top = _resolve_top(topElementID)
    if top is None:
        raise TgiError("Invalid top element handle", TgiFaultCode.INVALID_ID)
    coll = _ensure_collection(top, "components")
    obj = _new_or_ns(Component, name=name)
    coll.append(obj)
    register_parent(obj, top, ("components",), "list")
    return get_handle(obj)


def createDesign(topElementID: str, name: str) -> str:  # F.7.80.6
    """Create a Design (EXTENDED)."""
    top = _resolve_top(topElementID)
    if top is None:
        raise TgiError("Invalid top element handle", TgiFaultCode.INVALID_ID)
    coll = _ensure_collection(top, "designs")
    obj = _new_or_ns(Design, name=name)
    coll.append(obj)
    register_parent(obj, top, ("designs",), "list")
    return get_handle(obj)


def createDesignConfiguration(topElementID: str, name: str) -> str:  # F.7.80.7
    """Create a Design Configuration (EXTENDED)."""
    top = _resolve_top(topElementID)
    if top is None:
        raise TgiError("Invalid top element handle", TgiFaultCode.INVALID_ID)
    coll = _ensure_collection(top, "design_configurations")
    obj = _new_or_ns(DesignConfiguration, name=name)
    coll.append(obj)
    register_parent(obj, top, ("design_configurations",), "list")
    return get_handle(obj)


def createGeneratorChain(topElementID: str, name: str) -> str:  # F.7.80.8
    """Create a Generator Chain (EXTENDED)."""
    top = _resolve_top(topElementID)
    if top is None:
        raise TgiError("Invalid top element handle", TgiFaultCode.INVALID_ID)
    coll = _ensure_collection(top, "generator_chains")
    obj = _new_or_ns(GeneratorChain, name=name)
    coll.append(obj)
    register_parent(obj, top, ("generator_chains",), "list")
    return get_handle(obj)


def createTypeDefinitions(topElementID: str, name: str) -> str:  # F.7.80.9
    """Create a TypeDefinitions element (EXTENDED)."""
    top = _resolve_top(topElementID)
    if top is None:
        raise TgiError("Invalid top element handle", TgiFaultCode.INVALID_ID)
    coll = _ensure_collection(top, "type_definitions")
    obj = _new_or_ns(TypeDefinitions, name=name)
    coll.append(obj)
    register_parent(obj, top, ("type_definitions",), "list")
    return get_handle(obj)


def edit(elementID: str, attribute: str, value: Any) -> bool:  # F.7.80.10
    """Set an arbitrary attribute on a model element (EXTENDED).

    Raises:
        TgiError: If the element handle is invalid or the update fails.
    """
    obj = resolve_handle(elementID)
    if obj is None:
        raise TgiError("Invalid element handle", TgiFaultCode.INVALID_ID)
    try:
        setattr(obj, attribute, value)
    except Exception as exc:  # pragma: no cover
        raise TgiError(
            f"Failed to edit attribute {attribute}: {exc}", TgiFaultCode.INVALID_ARGUMENT
        ) from exc
    return True


def setXMLPath(elementID: str, path: str) -> bool:  # F.7.80.11
    """Associate an XML path with an element (EXTENDED)."""
    obj = resolve_handle(elementID)
    if obj is None:
        raise TgiError("Invalid element handle", TgiFaultCode.INVALID_ID)
    obj.xml_path = path  # type: ignore[attr-defined]
    return True
