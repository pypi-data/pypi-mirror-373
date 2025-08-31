"""CPU category TGI functions (IEEE 1685-2022).

Implements BASE (F.7.21) and EXTENDED (F.7.22) CPU functions.

The schema exposes CPUs via ``component.cpus.cpu[*]`` each with required
``name``, ``range``, ``width`` and ``memoryMapRef`` elements plus optional
``addressUnitBits`` (expression), ``regions`` list, executableImage list and
parameter list. Regions have required ``name``, ``addressOffset`` and ``range``.

BASE functions provide traversal of CPUs and their regions plus getters for
scalar/textual values and numeric/expression/ID triplets where the underlying
schema uses an expression type. EXTENDED functions support adding/removing CPUs
and regions, setting/clearing optional scalars and assigning expression values.

Assumptions:
* Function set aligns with patterns used in bus_definition, assertion, etc.
* Numeric getters attempt ``int()`` conversion; on failure they return ``None``.
* Removal of optional scalar/expression attributes returns True if a change
  occurred else False (idempotent semantics).
"""

# ruff: noqa: I001

from typing import Any

from org.accellera.ipxact.v1685_2022.address_unit_bits import AddressUnitBits
from org.accellera.ipxact.v1685_2022.component_type import ComponentType
from org.accellera.ipxact.v1685_2022.unsigned_longint_expression import UnsignedLongintExpression
from org.accellera.ipxact.v1685_2022.unsigned_positive_int_expression import UnsignedPositiveIntExpression
from org.accellera.ipxact.v1685_2022.unsigned_positive_longint_expression import UnsignedPositiveLongintExpression

from .core import (
    TgiError,
    TgiFaultCode,
    get_handle,
    resolve_handle,
    register_parent,
    detach_child_by_handle,
)

__all__: list[str] = [
    # BASE (F.7.21)
    "getComponentCpuIDs",
    "getCpuName",
    "getCpuDisplayName",
    "getCpuShortDescription",
    "getCpuDescription",
    "getCpuMemoryMapRef",
    "getCpuRange",
    "getCpuRangeExpression",
    "getCpuRangeID",
    "getCpuWidth",
    "getCpuWidthExpression",
    "getCpuWidthID",
    "getCpuAddressUnitBits",
    "getCpuAddressUnitBitsExpression",
    "getCpuAddressUnitBitsID",
    "getCpuRegionIDs",
    "getCpuRegionName",
    "getCpuRegionDisplayName",
    "getCpuRegionShortDescription",
    "getCpuRegionDescription",
    "getCpuRegionAddressOffset",
    "getCpuRegionAddressOffsetExpression",
    "getCpuRegionAddressOffsetID",
    "getCpuRegionRange",
    "getCpuRegionRangeExpression",
    "getCpuRegionRangeID",
    # EXTENDED (F.7.22)
    "addComponentCpu",
    "removeComponentCpu",
    "setCpuRange",
    "setCpuWidth",
    "setCpuAddressUnitBits",
    "setCpuMemoryMapRef",
    "removeCpuAddressUnitBits",
    "addCpuRegion",
    "removeCpuRegion",
    "setCpuRegionAddressOffset",
    "setCpuRegionRange",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _resolve_component(componentID: str) -> ComponentType:
    obj = resolve_handle(componentID)
    if not isinstance(obj, ComponentType):
        raise TgiError("Invalid component handle", TgiFaultCode.INVALID_ID)
    return obj


def _resolve_cpu(cpuID: str) -> ComponentType.Cpus.Cpu:
    obj = resolve_handle(cpuID)
    if not isinstance(obj, ComponentType.Cpus.Cpu):  # type: ignore[arg-type]
        raise TgiError("Invalid cpu handle", TgiFaultCode.INVALID_ID)
    return obj


def _resolve_region(regionID: str) -> ComponentType.Cpus.Cpu.Regions.Region:
    obj = resolve_handle(regionID)
    if not isinstance(obj, ComponentType.Cpus.Cpu.Regions.Region):  # type: ignore[arg-type]
        raise TgiError("Invalid cpu region handle", TgiFaultCode.INVALID_ID)
    return obj


def _text(obj: Any, attr: str) -> str | None:
    val = getattr(obj, attr, None)
    if val is None:
        return None
    return getattr(val, "value", val)


def _int_expr(expr: Any) -> int | None:
    if expr is None:
        return None
    try:
        return int(getattr(expr, "value", ""))
    except Exception:  # pragma: no cover
        return None


# ---------------------------------------------------------------------------
# BASE (F.7.21)
# ---------------------------------------------------------------------------

def getComponentCpuIDs(componentID: str) -> list[str]:
    """Return handles of ``cpu`` elements of a component.

    Args:
        componentID: Component handle.

    Returns:
        list[str]: Handles list (empty if none).
    """
    comp = _resolve_component(componentID)
    if comp.cpus is None:
        return []
    return [get_handle(c) for c in getattr(comp.cpus, "cpu", [])]


def getCpuName(cpuID: str) -> str | None:
    return _text(_resolve_cpu(cpuID), "name")


def getCpuDisplayName(cpuID: str) -> str | None:
    return _text(_resolve_cpu(cpuID), "display_name")


def getCpuShortDescription(cpuID: str) -> str | None:
    return _text(_resolve_cpu(cpuID), "short_description")


def getCpuDescription(cpuID: str) -> str | None:
    return _text(_resolve_cpu(cpuID), "description")


def getCpuMemoryMapRef(cpuID: str) -> str | None:
    return getattr(_resolve_cpu(cpuID), "memory_map_ref", None)


def getCpuRange(cpuID: str) -> int | None:
    return _int_expr(getattr(_resolve_cpu(cpuID), "range", None))


def getCpuRangeExpression(cpuID: str) -> str | None:
    return _text(_resolve_cpu(cpuID), "range")


def getCpuRangeID(cpuID: str) -> str | None:
    expr = getattr(_resolve_cpu(cpuID), "range", None)
    return get_handle(expr) if expr is not None else None


def getCpuWidth(cpuID: str) -> int | None:
    return _int_expr(getattr(_resolve_cpu(cpuID), "width", None))


def getCpuWidthExpression(cpuID: str) -> str | None:
    return _text(_resolve_cpu(cpuID), "width")


def getCpuWidthID(cpuID: str) -> str | None:
    expr = getattr(_resolve_cpu(cpuID), "width", None)
    return get_handle(expr) if expr is not None else None


def getCpuAddressUnitBits(cpuID: str) -> int | None:
    return _int_expr(getattr(_resolve_cpu(cpuID), "address_unit_bits", None))


def getCpuAddressUnitBitsExpression(cpuID: str) -> str | None:
    return _text(_resolve_cpu(cpuID), "address_unit_bits")


def getCpuAddressUnitBitsID(cpuID: str) -> str | None:
    expr = getattr(_resolve_cpu(cpuID), "address_unit_bits", None)
    return get_handle(expr) if expr is not None else None


def getCpuRegionIDs(cpuID: str) -> list[str]:
    cpu = _resolve_cpu(cpuID)
    regions = getattr(cpu, "regions", None)
    if regions is None:
        return []
    return [get_handle(r) for r in getattr(regions, "region", [])]


def getCpuRegionName(regionID: str) -> str | None:
    return _text(_resolve_region(regionID), "name")


def getCpuRegionDisplayName(regionID: str) -> str | None:
    return _text(_resolve_region(regionID), "display_name")


def getCpuRegionShortDescription(regionID: str) -> str | None:
    return _text(_resolve_region(regionID), "short_description")


def getCpuRegionDescription(regionID: str) -> str | None:
    return _text(_resolve_region(regionID), "description")


def getCpuRegionAddressOffset(regionID: str) -> int | None:
    return _int_expr(getattr(_resolve_region(regionID), "address_offset", None))


def getCpuRegionAddressOffsetExpression(regionID: str) -> str | None:
    return _text(_resolve_region(regionID), "address_offset")


def getCpuRegionAddressOffsetID(regionID: str) -> str | None:
    expr = getattr(_resolve_region(regionID), "address_offset", None)
    return get_handle(expr) if expr is not None else None


def getCpuRegionRange(regionID: str) -> int | None:
    return _int_expr(getattr(_resolve_region(regionID), "range", None))


def getCpuRegionRangeExpression(regionID: str) -> str | None:
    return _text(_resolve_region(regionID), "range")


def getCpuRegionRangeID(regionID: str) -> str | None:
    expr = getattr(_resolve_region(regionID), "range", None)
    return get_handle(expr) if expr is not None else None


# ---------------------------------------------------------------------------
# EXTENDED (F.7.22)
# ---------------------------------------------------------------------------

def addComponentCpu(
    componentID: str,
    name: str,
    memoryMapRef: str,
    rangeValue: int | str,
    widthValue: int | str,
) -> str:
    """Add a ``cpu`` to a component.

    Args:
        componentID: Component handle.
        name: CPU name.
        memoryMapRef: Referenced memory map name.
        rangeValue: Integer or expression for ``range``.
        widthValue: Integer or expression for ``width``.
    """
    comp = _resolve_component(componentID)
    if comp.cpus is None:
        comp.cpus = ComponentType.Cpus()  # type: ignore[arg-type]
    cpu = ComponentType.Cpus.Cpu(name=name, memory_map_ref=memoryMapRef)  # type: ignore[call-arg]
    # expressions
    cpu.range = UnsignedPositiveLongintExpression(value=str(rangeValue))  # type: ignore[arg-type]
    cpu.width = UnsignedPositiveIntExpression(value=str(widthValue))  # type: ignore[arg-type]
    comp.cpus.cpu.append(cpu)  # type: ignore[attr-defined]
    register_parent(cpu, comp, ("cpus",), "list")
    return get_handle(cpu)


def removeComponentCpu(cpuID: str) -> bool:
    """Remove a ``cpu`` element.

    Returns True if removed.
    """
    return detach_child_by_handle(cpuID)


def setCpuRange(cpuID: str, value: int | str | None) -> bool:
    """Set or clear the ``range`` expression of a CPU."""
    cpu = _resolve_cpu(cpuID)
    if value is None:
        changed = cpu.range is not None
        cpu.range = None  # type: ignore[assignment]
        return changed
    cpu.range = UnsignedPositiveLongintExpression(value=str(value))  # type: ignore[arg-type]
    return True


def setCpuWidth(cpuID: str, value: int | str | None) -> bool:
    """Set or clear the ``width`` expression of a CPU."""
    cpu = _resolve_cpu(cpuID)
    if value is None:
        changed = cpu.width is not None
        cpu.width = None  # type: ignore[assignment]
        return changed
    cpu.width = UnsignedPositiveIntExpression(value=str(value))  # type: ignore[arg-type]
    return True


def setCpuAddressUnitBits(cpuID: str, value: int | str | None) -> bool:
    """Set or clear ``addressUnitBits``.

    Value is stored as an ``AddressUnitBits`` expression. Clearing occurs when
    value is None.
    """
    cpu = _resolve_cpu(cpuID)
    if value is None:
        changed = cpu.address_unit_bits is not None
        cpu.address_unit_bits = None  # type: ignore[assignment]
        return changed
    cpu.address_unit_bits = AddressUnitBits(value=str(value))  # type: ignore[arg-type]
    return True


def setCpuMemoryMapRef(cpuID: str, memoryMapRef: str | None) -> bool:
    """Set or clear the ``memoryMapRef`` value."""
    cpu = _resolve_cpu(cpuID)
    if memoryMapRef is None:
        changed = cpu.memory_map_ref is not None
        cpu.memory_map_ref = None  # type: ignore[assignment]
        return changed
    cpu.memory_map_ref = memoryMapRef  # type: ignore[assignment]
    return True


def removeCpuAddressUnitBits(cpuID: str) -> bool:
    """Remove ``addressUnitBits`` (alias for set with None)."""
    return setCpuAddressUnitBits(cpuID, None)


def addCpuRegion(
    cpuID: str,
    name: str,
    addressOffset: int | str,
    rangeValue: int | str,
) -> str:
    """Append a ``region`` to a CPU.

    Args:
        cpuID: CPU handle.
        name: Region name.
        addressOffset: Numeric/expression for addressOffset.
        rangeValue: Numeric/expression for range.
    """
    cpu = _resolve_cpu(cpuID)
    if cpu.regions is None:
        cpu.regions = ComponentType.Cpus.Cpu.Regions()  # type: ignore[arg-type]
    r = ComponentType.Cpus.Cpu.Regions.Region(name=name)  # type: ignore[call-arg]
    r.address_offset = UnsignedLongintExpression(value=str(addressOffset))  # type: ignore[attr-defined]
    r.range = UnsignedPositiveLongintExpression(value=str(rangeValue))  # type: ignore[attr-defined]
    cpu.regions.region.append(r)  # type: ignore[attr-defined]
    register_parent(r, cpu, ("regions",), "list")
    return get_handle(r)


def removeCpuRegion(regionID: str) -> bool:
    """Remove a CPU region by handle."""
    return detach_child_by_handle(regionID)


def setCpuRegionAddressOffset(regionID: str, value: int | str | None) -> bool:
    """Set or clear a region ``addressOffset`` expression."""
    r = _resolve_region(regionID)
    if value is None:
        changed = r.address_offset is not None
        r.address_offset = None  # type: ignore[assignment]
        return changed
    r.address_offset = UnsignedLongintExpression(value=str(value))  # type: ignore[arg-type]
    return True


def setCpuRegionRange(regionID: str, value: int | str | None) -> bool:
    """Set or clear a region ``range`` expression."""
    r = _resolve_region(regionID)
    if value is None:
        changed = r.range is not None
        r.range = None  # type: ignore[assignment]
        return changed
    r.range = UnsignedPositiveLongintExpression(value=str(value))  # type: ignore[arg-type]
    return True
