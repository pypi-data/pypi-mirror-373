"""Bus interface category TGI functions (IEEE 1685-2022).

Implements BASE (F.7.19) and EXTENDED (F.7.20) Bus Interface functions.

Bus interfaces expose VLNV references to busType and abstractionTypes, a
``connectionRequired`` attribute, optional textual metadata (name,
displayName, description) and port mapping sub-structures. The BASE API
covers enumeration of busInterface children, retrieval of VLNV tuples for
busType and associated abstractionType view references, and metadata getters.
The EXTENDED API supports adding/removing busInterface elements, adjusting
references and setting/clearing the connectionRequired flag.
"""

from typing import Any

from org.accellera.ipxact.v1685_2022 import BusInterfaces

from .core import (
    TgiError,
    TgiFaultCode,
    detach_child_by_handle,
    get_handle,
    register_parent,
    resolve_handle,
)  # noqa: WPS347

__all__ = [
    # BASE (F.7.19)
    "getComponentBusInterfaceIDs",
    "getBusInterfaceName",
    "getBusInterfaceDisplayName",
    "getBusInterfaceDescription",
    "getBusInterfaceBusTypeRefByVLNV",
    "getBusInterfaceAbstractionTypeBusTypeViewRefsByVLNV",
    "getBusInterfaceConnectionRequired",
    # EXTENDED (F.7.20)
    "addBusInterface",
    "removeBusInterface",
    "setBusInterfaceBusTypeRefByVLNV",
    "addBusInterfaceAbstractionTypeBusTypeViewRef",
    "setBusInterfaceConnectionRequired",
]


# ---------------------------------------------------------------------------
# Helpers (non-spec)
# ---------------------------------------------------------------------------

def _resolve_bus_interfaces(containerID: str) -> BusInterfaces:
    obj = resolve_handle(containerID)
    if not isinstance(obj, BusInterfaces):
        raise TgiError("Invalid busInterfaces handle", TgiFaultCode.INVALID_ID)
    return obj


def _name_group_value(obj: Any, attr: str) -> str | None:
    if obj is None:
        return None
    field = getattr(obj, attr, None)
    if field is None:
        return None
    return getattr(field, "value", field) if not isinstance(field, str) else field


# ---------------------------------------------------------------------------
# BASE (F.7.19)
# ---------------------------------------------------------------------------

def getComponentBusInterfaceIDs(busInterfacesID: str) -> list[str]:  # F.7.19.x
    """Return handles of all ``busInterface`` children.

    Args:
        busInterfacesID: Handle referencing a ``busInterfaces`` container.

    Returns:
        list[str]: Handles (possibly empty).
    """
    bis = _resolve_bus_interfaces(busInterfacesID)
    return [get_handle(bi) for bi in getattr(bis, "bus_interface", [])]


def getBusInterfaceName(busInterfaceID: str) -> str | None:  # F.7.19.x
    """Return the busInterface ``name`` attribute."""
    bi = resolve_handle(busInterfaceID)
    return getattr(bi, "name", None)


def getBusInterfaceDisplayName(busInterfaceID: str) -> str | None:  # F.7.19.x
    """Return ``displayName`` value."""
    return _name_group_value(resolve_handle(busInterfaceID), "display_name")


def getBusInterfaceDescription(busInterfaceID: str) -> str | None:  # F.7.19.x
    """Return ``description`` value."""
    return _name_group_value(resolve_handle(busInterfaceID), "description")


def getBusInterfaceBusTypeRefByVLNV(
    busInterfaceID: str,
) -> tuple[str | None, str | None, str | None, str | None]:  # F.7.19.x
    """Return the busType VLNV tuple ``(vendor, library, name, version)``.

    Returns a tuple of Nones if the reference is absent.
    """
    bi = resolve_handle(busInterfaceID)
    if bi is None:
        raise TgiError("Invalid bus interface handle", TgiFaultCode.INVALID_ID)
    bus_type = getattr(bi, "bus_type", None)
    if bus_type is None:
        return (None, None, None, None)
    return (
        getattr(bus_type, "vendor", None),
        getattr(bus_type, "library", None),
        getattr(bus_type, "name", None),
        getattr(bus_type, "version", None),
    )


def getBusInterfaceAbstractionTypeBusTypeViewRefsByVLNV(
    busInterfaceID: str,
) -> list[tuple[str | None, str | None, str | None, str | None]]:  # F.7.19.x
    """Return list of abstractionType view VLNV tuples.

    The 2022 schema models viewRef as name only; vendor/library/version will
    normally be ``None``.
    """
    bi = resolve_handle(busInterfaceID)
    if bi is None:
        raise TgiError("Invalid bus interface handle", TgiFaultCode.INVALID_ID)
    abstraction_types = getattr(bi, "abstraction_types", None)
    if abstraction_types is None:
        return []
    result: list[tuple[str | None, str | None, str | None, str | None]] = []
    ats = getattr(abstraction_types, "abstraction_type", [])
    for at in ats:
        vr_list = getattr(at, "view_ref", [])
        if not vr_list:
            result.append((None, None, None, None))
            continue
        # Use first view ref only (spec semantics treat each abstractionType separately)
        vr = vr_list[0]
        result.append((None, None, getattr(vr, "value", None), None))
    return result


def getBusInterfaceConnectionRequired(busInterfaceID: str) -> bool | None:  # F.7.19.x
    """Return ``connectionRequired`` attribute value (or None)."""
    bi = resolve_handle(busInterfaceID)
    if bi is None:
        raise TgiError("Invalid bus interface handle", TgiFaultCode.INVALID_ID)
    return getattr(bi, "connection_required", None)


# ---------------------------------------------------------------------------
# EXTENDED (F.7.20)
# ---------------------------------------------------------------------------

def addBusInterface(componentID: str, name: str, busTypeVLNV: tuple[str, str, str, str]) -> str:  # F.7.20.x
    """Create and append a new ``busInterface`` under a component.

    Args:
        componentID: Parent component handle.
        name: Interface name.
        busTypeVLNV: (vendor, library, name, version) tuple for busType ref.
    """
    comp = resolve_handle(componentID)
    from org.accellera.ipxact.v1685_2022.component_type import ComponentType
    if not isinstance(comp, ComponentType):
        raise TgiError("Invalid component handle", TgiFaultCode.INVALID_ID)
    from org.accellera.ipxact.v1685_2022.bus_interface import BusInterface
    from org.accellera.ipxact.v1685_2022.bus_interfaces import BusInterfaces
    from org.accellera.ipxact.v1685_2022.configurable_library_ref_type import ConfigurableLibraryRefType

    (v, lib, n, ver) = busTypeVLNV
    if comp.bus_interfaces is None:
        comp.bus_interfaces = BusInterfaces(bus_interface=[])  # type: ignore[arg-type]
    bi = BusInterface(name=name)
    bi.bus_type = ConfigurableLibraryRefType(vendor=v, library=lib, name=n, version=ver)  # type: ignore[arg-type]
    comp.bus_interfaces.bus_interface.append(bi)  # type: ignore[attr-defined]
    register_parent(bi, comp, ("bus_interfaces",), "list")
    return get_handle(bi)


def removeBusInterface(busInterfaceID: str) -> bool:  # F.7.20.x
    """Remove a ``busInterface`` by handle.

    Returns True if removed, False otherwise.
    """
    return detach_child_by_handle(busInterfaceID)


def setBusInterfaceBusTypeRefByVLNV(
    busInterfaceID: str,
    busTypeVLNV: tuple[str, str, str, str] | None,
) -> bool:  # F.7.20.x
    """Set or clear the busType reference of a busInterface."""
    bi = resolve_handle(busInterfaceID)
    from org.accellera.ipxact.v1685_2022.bus_interface import BusInterface
    if not isinstance(bi, BusInterface):
        raise TgiError("Invalid bus interface handle", TgiFaultCode.INVALID_ID)
    if busTypeVLNV is None:
        bi.bus_type = None  # type: ignore[assignment]
        return True
    (v, lib, n, ver) = busTypeVLNV
    from org.accellera.ipxact.v1685_2022.configurable_library_ref_type import ConfigurableLibraryRefType

    bi.bus_type = ConfigurableLibraryRefType(vendor=v, library=lib, name=n, version=ver)  # type: ignore[arg-type]
    return True


def addBusInterfaceAbstractionTypeBusTypeViewRef(
    busInterfaceID: str,
    viewVLNV: tuple[str, str, str, str],
) -> bool:  # F.7.20.x
    """Append an abstractionType element referencing a view (name only stored)."""
    bi = resolve_handle(busInterfaceID)
    from org.accellera.ipxact.v1685_2022.bus_interface import BusInterface
    if not isinstance(bi, BusInterface):
        raise TgiError("Invalid bus interface handle", TgiFaultCode.INVALID_ID)
    from org.accellera.ipxact.v1685_2022.abstraction_types import AbstractionTypes
    from org.accellera.ipxact.v1685_2022.view_ref import ViewRef

    if bi.abstraction_types is None:
        bi.abstraction_types = AbstractionTypes(abstraction_type=[])  # type: ignore[arg-type]
    (_, _, name, _) = viewVLNV
    at = AbstractionTypes.AbstractionType()
    at.view_ref.append(ViewRef(value=name))  # type: ignore[attr-defined]
    bi.abstraction_types.abstraction_type.append(at)  # type: ignore[attr-defined]
    return True


def setBusInterfaceConnectionRequired(busInterfaceID: str, required: bool | None) -> bool:  # F.7.20.x
    """Set or clear the ``connectionRequired`` flag."""
    bi = resolve_handle(busInterfaceID)
    from org.accellera.ipxact.v1685_2022.bus_interface import BusInterface
    if not isinstance(bi, BusInterface):
        raise TgiError("Invalid bus interface handle", TgiFaultCode.INVALID_ID)
    bi.connection_required = required  # type: ignore[assignment]
    return True

