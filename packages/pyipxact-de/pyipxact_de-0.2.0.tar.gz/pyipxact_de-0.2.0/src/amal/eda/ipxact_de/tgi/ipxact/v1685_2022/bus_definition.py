"""Bus definition category TGI functions (IEEE 1685-2022).

Implements BASE (F.7.17) and EXTENDED (F.7.18) Bus Definition functions.

The schema class :class:`BusDefinition` models VLNV metadata, reference to an
optional base bus (``extends``), maximum initiator/target counts (unsigned
expressions), system group names, choices, parameters, assertions and optional
boolean capabilities (``directConnection``, ``broadcast``, ``isAddressable``).

BASE functions provide traversal and value retrieval. EXTENDED functions add,
remove and modify child elements and scalar/expression values. Where the spec
mentions removal of optional elements, corresponding ``remove*`` functions set
the underlying field to ``None`` and return ``True`` if a change occurred, else
``False``.

Assumptions:
* The full list of F.7.17/F.7.18 function names is inferred; if additional or
    differently named functions are required by the spec they can be added in a
    follow-up revision.
* Parameter / assertion category specific operations remain available via
    their dedicated category modules; minimal add/remove helpers are exposed
    here for completeness per F.7 classification symmetry.
"""
from collections.abc import Iterable
from typing import Any

from org.accellera.ipxact.v1685_2022 import BusDefinition
from org.accellera.ipxact.v1685_2022.assertion import Assertion  # type: ignore
from org.accellera.ipxact.v1685_2022.assertions import Assertions
from org.accellera.ipxact.v1685_2022.choices import Choices
from org.accellera.ipxact.v1685_2022.library_ref_type import LibraryRefType
from org.accellera.ipxact.v1685_2022.parameter import Parameter  # type: ignore
from org.accellera.ipxact.v1685_2022.parameters import Parameters
from org.accellera.ipxact.v1685_2022.unsigned_int_expression import UnsignedIntExpression

# ruff: noqa: I001 (import ordering harmonised with sibling modules)

from .core import (
        TgiError,
        TgiFaultCode,
        get_handle,
        resolve_handle,
        register_parent,
        detach_child_by_handle,
)

__all__: list[str] = [
        # BASE (F.7.17)
        "getBusDefinitionSystemGroupNameIDs",
        "getBusDefinitionChoiceIDs",
        "getBusDefinitionParameterIDs",
        "getBusDefinitionAssertionIDs",
        "getBusDefinitionVendor",
        "getBusDefinitionLibrary",
        "getBusDefinitionName",
        "getBusDefinitionVersion",
        "getBusDefinitionDisplayName",
        "getBusDefinitionShortDescription",
        "getBusDefinitionDescription",
        "getBusDefinitionDirectConnection",
        "getBusDefinitionBroadcast",
        "getBusDefinitionIsAddressable",
        "getBusDefinitionExtendsVendor",
        "getBusDefinitionExtendsLibrary",
        "getBusDefinitionExtendsName",
        "getBusDefinitionExtendsVersion",
        "getBusDefinitionExtendsVLNV",
        "getBusDefinitionMaxInitiators",
        "getBusDefinitionMaxInitiatorsExpression",
        "getBusDefinitionMaxInitiatorsID",
        "getBusDefinitionMaxTargets",
        "getBusDefinitionMaxTargetsExpression",
        "getBusDefinitionMaxTargetsID",
        "getBusDefinitionSystemGroupNameValue",
        # EXTENDED (F.7.18)
        "addBusDefinitionSystemGroupName",
        "addBusDefinitionChoice",
        "addBusDefinitionParameterInteger",
        "addBusDefinitionAssertion",
        "removeBusDefinitionSystemGroupName",
        "removeBusDefinitionChoice",
        "removeBusDefinitionParameter",
        "removeBusDefinitionAssertion",
        "setBusDefinitionDisplayName",
        "setBusDefinitionShortDescription",
        "setBusDefinitionDescription",
        "setBusDefinitionExtends",
        "removeBusDefinitionExtends",
        "setBusDefinitionDirectConnection",
        "removeBusDefinitionDirectConnection",
        "setBusDefinitionBroadcast",
        "removeBusDefinitionBroadcast",
        "setBusDefinitionIsAddressable",
        "removeBusDefinitionIsAddressable",
        "setBusDefinitionMaxInitiators",
        "removeBusDefinitionMaxInitiators",
        "setBusDefinitionMaxTargets",
        "removeBusDefinitionMaxTargets",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _resolve(busDefinitionID: str) -> BusDefinition:
    """Resolve and type-check a bus definition handle.

    Args:
        busDefinitionID: Handle referencing a busDefinition element.

    Returns:
        BusDefinition: Resolved schema object.

    Raises:
        TgiError: If the handle is invalid or not a BusDefinition.
    """
    obj = resolve_handle(busDefinitionID)
    if not isinstance(obj, BusDefinition):  # type: ignore[arg-type]
        raise TgiError("Invalid busDefinition handle", TgiFaultCode.INVALID_ID)
    return obj


def _ids(items: Iterable[Any]) -> list[str]:
    return [get_handle(i) for i in items]


def _scalar(obj: Any, attr: str) -> str | None:
    val = getattr(obj, attr, None)
    if val is None:
        return None
    return getattr(val, "value", val)


# ---------------------------------------------------------------------------
# Traversal
# ---------------------------------------------------------------------------

def getBusDefinitionSystemGroupNameIDs(busDefinitionID: str) -> list[str]:  # F.7.17.x
    """Return handles of ``systemGroupName`` elements.

    Args:
        busDefinitionID: Bus definition handle.

    Returns:
        list[str]: Handles (possibly empty) of system group names.
    """
    bd = _resolve(busDefinitionID)
    sgs = getattr(bd, "system_group_names", None)
    if sgs is None:
        return []
    return _ids(getattr(sgs, "system_group_name", []))


def getBusDefinitionChoiceIDs(busDefinitionID: str) -> list[str]:  # F.7.17.x
    """Return handles of ``choice`` children (if any)."""
    bd = _resolve(busDefinitionID)
    chs = getattr(bd, "choices", None)
    if chs is None:
        return []
    return [get_handle(c) for c in getattr(chs, "choice", [])]


def getBusDefinitionParameterIDs(busDefinitionID: str) -> list[str]:  # F.7.17.x
    """Return handles of ``parameter`` children (if any)."""
    bd = _resolve(busDefinitionID)
    ps = getattr(bd, "parameters", None)
    if ps is None:
        return []
    return [get_handle(p) for p in getattr(ps, "parameter", [])]


def getBusDefinitionAssertionIDs(busDefinitionID: str) -> list[str]:  # F.7.17.x
    """Return handles of ``assertion`` children (if any)."""
    bd = _resolve(busDefinitionID)
    ats = getattr(bd, "assertions", None)
    if ats is None:
        return []
    return [get_handle(a) for a in getattr(ats, "assertion", [])]


# ---------------------------------------------------------------------------
# Getters
# ---------------------------------------------------------------------------

def getBusDefinitionVendor(busDefinitionID: str) -> str | None:  # F.7.17.x
    """Return ``vendor`` value."""
    return _scalar(_resolve(busDefinitionID), "vendor")


def getBusDefinitionLibrary(busDefinitionID: str) -> str | None:  # F.7.17.x
    """Return ``library`` value."""
    return _scalar(_resolve(busDefinitionID), "library")


def getBusDefinitionName(busDefinitionID: str) -> str | None:  # F.7.17.x
    """Return ``name`` value."""
    return _scalar(_resolve(busDefinitionID), "name")


def getBusDefinitionVersion(busDefinitionID: str) -> str | None:  # F.7.17.x
    """Return ``version`` value."""
    return _scalar(_resolve(busDefinitionID), "version")


def getBusDefinitionDisplayName(busDefinitionID: str) -> str | None:  # F.7.17.x
    """Return ``displayName`` value."""
    return _scalar(_resolve(busDefinitionID), "display_name")


def getBusDefinitionShortDescription(busDefinitionID: str) -> str | None:  # F.7.17.x
    """Return ``shortDescription`` value."""
    return _scalar(_resolve(busDefinitionID), "short_description")


def getBusDefinitionDescription(busDefinitionID: str) -> str | None:  # F.7.17.x
    """Return ``description`` value."""
    return _scalar(_resolve(busDefinitionID), "description")


def getBusDefinitionDirectConnection(busDefinitionID: str) -> bool | None:  # F.7.17.x
    """Return boolean ``directConnection`` flag."""
    bd = _resolve(busDefinitionID)
    return getattr(bd, "direct_connection", None)


def getBusDefinitionBroadcast(busDefinitionID: str) -> bool | None:  # F.7.17.x
    """Return boolean ``broadcast`` flag."""
    bd = _resolve(busDefinitionID)
    return getattr(bd, "broadcast", None)


def getBusDefinitionIsAddressable(busDefinitionID: str) -> bool | None:  # F.7.17.x
    """Return boolean ``isAddressable`` flag."""
    bd = _resolve(busDefinitionID)
    return getattr(bd, "is_addressable", None)


def getBusDefinitionExtendsVendor(busDefinitionID: str) -> str | None:  # F.7.17.x
    ext = getattr(_resolve(busDefinitionID), "extends", None)
    return getattr(ext, "vendor", None) if ext is not None else None


def getBusDefinitionExtendsLibrary(busDefinitionID: str) -> str | None:  # F.7.17.x
    ext = getattr(_resolve(busDefinitionID), "extends", None)
    return getattr(ext, "library", None) if ext is not None else None


def getBusDefinitionExtendsName(busDefinitionID: str) -> str | None:  # F.7.17.x
    ext = getattr(_resolve(busDefinitionID), "extends", None)
    return getattr(ext, "name", None) if ext is not None else None


def getBusDefinitionExtendsVersion(busDefinitionID: str) -> str | None:  # F.7.17.x
    ext = getattr(_resolve(busDefinitionID), "extends", None)
    return getattr(ext, "version", None) if ext is not None else None


def getBusDefinitionExtendsVLNV(busDefinitionID: str) -> str | None:  # F.7.17.x
    """Return concatenated VLNV string for ``extends`` (vendor:library:name:version)."""
    bd = _resolve(busDefinitionID)
    ext = getattr(bd, "extends", None)
    if ext is None:
        return None
    parts_raw = [getattr(ext, a, None) for a in ("vendor", "library", "name", "version")]
    if any(p is None for p in parts_raw):
        return None
    return ":".join(str(p) for p in parts_raw)


def getBusDefinitionMaxInitiators(busDefinitionID: str) -> int | None:  # F.7.17.x
    """Return integer value of ``maxInitiators`` if convertible."""
    expr = getattr(_resolve(busDefinitionID), "max_initiators", None)
    if expr is None:
        return None
    try:
        return int(getattr(expr, "value", ""))  # type: ignore[arg-type]
    except Exception:  # pragma: no cover
        return None


def getBusDefinitionMaxInitiatorsExpression(busDefinitionID: str) -> str | None:  # F.7.17.x
    """Return expression string for ``maxInitiators``."""
    return _scalar(_resolve(busDefinitionID), "max_initiators")


def getBusDefinitionMaxInitiatorsID(busDefinitionID: str) -> str | None:  # F.7.17.x
    expr = getattr(_resolve(busDefinitionID), "max_initiators", None)
    return get_handle(expr) if expr is not None else None


def getBusDefinitionMaxTargets(busDefinitionID: str) -> int | None:  # F.7.17.x
    """Return integer value of ``maxTargets`` if convertible."""
    expr = getattr(_resolve(busDefinitionID), "max_targets", None)
    if expr is None:
        return None
    try:
        return int(getattr(expr, "value", ""))  # type: ignore[arg-type]
    except Exception:  # pragma: no cover
        return None


def getBusDefinitionMaxTargetsExpression(busDefinitionID: str) -> str | None:  # F.7.17.x
    """Return expression string for ``maxTargets``."""
    return _scalar(_resolve(busDefinitionID), "max_targets")


def getBusDefinitionMaxTargetsID(busDefinitionID: str) -> str | None:  # F.7.17.x
    expr = getattr(_resolve(busDefinitionID), "max_targets", None)
    return get_handle(expr) if expr is not None else None


def getBusDefinitionSystemGroupNameValue(systemGroupNameID: str) -> str | None:  # F.7.17.x
    """Return the ``value`` of a ``systemGroupName`` element.

    Args:
        systemGroupNameID: Handle of a systemGroupName element.

    Returns:
        str | None: String value.

    Raises:
        TgiError: If the handle is invalid.
    """
    sgn = resolve_handle(systemGroupNameID)
    if sgn is None or not hasattr(sgn, "value"):
        raise TgiError("Invalid systemGroupName handle", TgiFaultCode.INVALID_ID)
    return getattr(sgn, "value", None)


# ---------------------------------------------------------------------------
# EXTENDED (F.7.18)
# ---------------------------------------------------------------------------

def addBusDefinitionSystemGroupName(busDefinitionID: str, name: str) -> str:  # F.7.18.x
    """Append a new ``systemGroupName`` element.

    Args:
        busDefinitionID: Bus definition handle.
        name: Group name string.

    Returns:
        str: Handle of created element.
    """
    bd = _resolve(busDefinitionID)
    if bd.system_group_names is None:
        bd.system_group_names = BusDefinition.SystemGroupNames()  # type: ignore[attr-defined]
    sgn = BusDefinition.SystemGroupNames.SystemGroupName(value=name)
    bd.system_group_names.system_group_name.append(sgn)  # type: ignore[attr-defined]
    register_parent(sgn, bd, ("system_group_names",), "list")
    return get_handle(sgn)


def addBusDefinitionChoice(busDefinitionID: str, name: str) -> str:  # F.7.18.x
    """Append a ``choice`` element with given name."""
    bd = _resolve(busDefinitionID)
    if bd.choices is None:
        bd.choices = Choices()  # type: ignore[attr-defined]
    ch = Choices.Choice(name=name)  # type: ignore[attr-defined]
    bd.choices.choice.append(ch)  # type: ignore[attr-defined]
    register_parent(ch, bd, ("choices",), "list")
    return get_handle(ch)


def addBusDefinitionParameterInteger(busDefinitionID: str, name: str, value: int) -> str:  # F.7.18.x
    """Add a simple integer ``parameter`` (name/value only).

    Args:
        busDefinitionID: Bus definition handle.
        name: Parameter name.
        value: Integer value (stored as string expression).
    """
    bd = _resolve(busDefinitionID)
    if bd.parameters is None:
        bd.parameters = Parameters()  # type: ignore[attr-defined]
    param = Parameter(name=name, value=str(value))  # type: ignore[call-arg]
    bd.parameters.parameter.append(param)  # type: ignore[attr-defined]
    register_parent(param, bd, ("parameters",), "list")
    return get_handle(param)


def addBusDefinitionAssertion(busDefinitionID: str, name: str, expression: str) -> str:  # F.7.18.x
    """Add an ``assertion`` element (name + expression)."""
    from org.accellera.ipxact.v1685_2022.unsigned_bit_expression import UnsignedBitExpression

    bd = _resolve(busDefinitionID)
    if bd.assertions is None:
        bd.assertions = Assertions()  # type: ignore[attr-defined]
    a = Assertion(name=name)  # type: ignore[call-arg]
    a.assert_value = UnsignedBitExpression(value=expression)  # type: ignore[attr-defined]
    bd.assertions.assertion.append(a)  # type: ignore[attr-defined]
    register_parent(a, bd, ("assertions",), "list")
    return get_handle(a)


def removeBusDefinitionSystemGroupName(systemGroupNameID: str) -> bool:  # F.7.18.x
    """Remove a systemGroupName element by handle."""
    return detach_child_by_handle(systemGroupNameID)


def removeBusDefinitionChoice(choiceID: str) -> bool:  # F.7.18.x
    """Remove a ``choice`` element by handle."""
    return detach_child_by_handle(choiceID)


def removeBusDefinitionParameter(parameterID: str) -> bool:  # F.7.18.x
    """Remove a ``parameter`` element by handle."""
    return detach_child_by_handle(parameterID)


def removeBusDefinitionAssertion(assertionID: str) -> bool:  # F.7.18.x
    """Remove an ``assertion`` element by handle."""
    return detach_child_by_handle(assertionID)


def setBusDefinitionDisplayName(busDefinitionID: str, value: str) -> bool:  # F.7.18.x
    """Set or create the ``displayName`` element."""
    bd = _resolve(busDefinitionID)
    bd.display_name = value  # type: ignore[attr-defined]
    return True


def setBusDefinitionShortDescription(busDefinitionID: str, value: str) -> bool:  # F.7.18.x
    """Set or create the ``shortDescription`` element."""
    from org.accellera.ipxact.v1685_2022.short_description import ShortDescription

    bd = _resolve(busDefinitionID)
    bd.short_description = ShortDescription(value=value)  # type: ignore[attr-defined]
    return True


def setBusDefinitionDescription(busDefinitionID: str, value: str) -> bool:  # F.7.18.x
    """Set or create the ``description`` element."""
    from org.accellera.ipxact.v1685_2022.description import Description

    bd = _resolve(busDefinitionID)
    bd.description = Description(value=value)  # type: ignore[attr-defined]
    return True


def setBusDefinitionExtends(
    busDefinitionID: str,
    vendor: str,
    library: str,
    name: str,
    version: str,
) -> bool:  # F.7.18.x
    """Set or create the ``extends`` reference (VLNV)."""
    bd = _resolve(busDefinitionID)
    bd.extends = LibraryRefType(vendor=vendor, library=library, name=name, version=version)  # type: ignore[attr-defined]
    return True


def removeBusDefinitionExtends(busDefinitionID: str) -> bool:  # F.7.18.x
    """Remove ``extends`` reference if present."""
    bd = _resolve(busDefinitionID)
    if bd.extends is not None:
        bd.extends = None  # type: ignore[attr-defined]
        return True
    return False


def setBusDefinitionDirectConnection(busDefinitionID: str, flag: bool) -> bool:  # F.7.18.x
    """Set ``directConnection`` boolean."""
    bd = _resolve(busDefinitionID)
    bd.direct_connection = flag  # type: ignore[attr-defined]
    return True


def removeBusDefinitionDirectConnection(busDefinitionID: str) -> bool:  # F.7.18.x
    """Remove (clear) ``directConnection`` if set."""
    bd = _resolve(busDefinitionID)
    if bd.direct_connection is not None:
        bd.direct_connection = None  # type: ignore[attr-defined]
        return True
    return False


def setBusDefinitionBroadcast(busDefinitionID: str, flag: bool) -> bool:  # F.7.18.x
    """Set ``broadcast`` flag."""
    bd = _resolve(busDefinitionID)
    bd.broadcast = flag  # type: ignore[attr-defined]
    return True


def removeBusDefinitionBroadcast(busDefinitionID: str) -> bool:  # F.7.18.x
    """Remove ``broadcast`` flag if present."""
    bd = _resolve(busDefinitionID)
    if bd.broadcast is not None:
        bd.broadcast = None  # type: ignore[attr-defined]
        return True
    return False


def setBusDefinitionIsAddressable(busDefinitionID: str, flag: bool) -> bool:  # F.7.18.x
    """Set ``isAddressable`` flag."""
    bd = _resolve(busDefinitionID)
    bd.is_addressable = flag  # type: ignore[attr-defined]
    return True


def removeBusDefinitionIsAddressable(busDefinitionID: str) -> bool:  # F.7.18.x
    """Remove ``isAddressable`` flag if present."""
    bd = _resolve(busDefinitionID)
    if bd.is_addressable is not None:
        bd.is_addressable = None  # type: ignore[attr-defined]
        return True
    return False


def setBusDefinitionMaxInitiators(busDefinitionID: str, value: int | str) -> bool:  # F.7.18.x
    """Set (or create) ``maxInitiators`` expression."""
    bd = _resolve(busDefinitionID)
    bd.max_initiators = UnsignedIntExpression(value=str(value))  # type: ignore[attr-defined]
    return True


def removeBusDefinitionMaxInitiators(busDefinitionID: str) -> bool:  # F.7.18.x
    """Remove ``maxInitiators`` element."""
    bd = _resolve(busDefinitionID)
    if bd.max_initiators is not None:
        bd.max_initiators = None  # type: ignore[attr-defined]
        return True
    return False


def setBusDefinitionMaxTargets(busDefinitionID: str, value: int | str) -> bool:  # F.7.18.x
    """Set (or create) ``maxTargets`` expression."""
    bd = _resolve(busDefinitionID)
    bd.max_targets = UnsignedIntExpression(value=str(value))  # type: ignore[attr-defined]
    return True


def removeBusDefinitionMaxTargets(busDefinitionID: str) -> bool:  # F.7.18.x
    """Remove ``maxTargets`` element."""
    bd = _resolve(busDefinitionID)
    if bd.max_targets is not None:
        bd.max_targets = None  # type: ignore[attr-defined]
        return True
    return False

