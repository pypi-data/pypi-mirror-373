"""Component category TGI functions (IEEE 1685-2022).

Implements BASE (F.7.29) and EXTENDED (F.7.30) Component functions. Only the
public TGI functions defined by those sections are exported (no convenience
helpers). All functions take opaque handles referencing *unconfigured*
``componentType`` object graphs (schema: ``ComponentType``) previously
registered via the core handle manager. Invalid handles raise
``TgiError`` with ``TgiFaultCode.INVALID_ID``. Mutating functions create the
minimal schema objects necessary to satisfy the call semantics; callers may
further refine created sub-elements through other category APIs.
"""
# ruff: noqa: I001  # Allow local inline import ordering within factory helpers

from collections.abc import Iterable
from typing import Any

from org.accellera.ipxact.v1685_2022 import ComponentType

from .core import TgiError, TgiFaultCode, get_handle, resolve_handle

__all__ = [
    # BASE (F.7.29)
    "getComponentAddressSpaceIDs",
    "getComponentBusInterfaceIDs",
    "getComponentChannelIDs",
    "getComponentChoiceIDs",
    "getComponentClearboxElementIDs",
    "getComponentComponentGeneratorIDs",
    "getComponentComponentInstantiationIDs",
    "getComponentCpuIDs",
    "getComponentDesignConfigurationInstantiationIDs",
    "getComponentDesignInstantiationIDs",
    "getComponentExternalTypeDefinitionsIDs",
    "getComponentFileSetIDs",
    "getComponentIndirectInterfaceIDs",
    "getComponentMemoryMapIDs",
    "getComponentModeIDs",
    "getComponentOtherClockDriverIDs",
    "getComponentPortIDs",
    "getComponentPowerDomainIDs",
    "getComponentResetTypeIDs",
    "getComponentSelectedViewIDs",
    # EXTENDED (F.7.30)
    "addComponentAddressSpace",
    "addComponentChannel",
    "addComponentChoice",
    "addComponentClearboxElement",
    "addComponentComponentGenerator",
    "addComponentComponentInstantiation",
    "addComponentCpu",
    "addComponentDesignConfigurationInstantiation",
    "addComponentDesignInstantiation",
    "addComponentFileSet",
    "addComponentIndirectInterface",
    "addComponentInitiatorBusInterface",
    "addComponentMemoryMap",
    "addComponentMirroredInitiatorBusInterface",
    "addComponentMirroredSystemBusInterface",
    "addComponentMirroredTargetBusInterface",
    "addComponentMode",
    "addComponentMonitorBusInterface",
    "addComponentOtherClockDriver",
    "addComponentResetType",
    "addComponentStructuredInterfacePort",
    "addComponentStructuredStructPort",
    "addComponentStructuredUnionPort",
    "addComponentSystemBusInterface",
    "addComponentTargetBusInterface",
    "addComponentTransactionalPort",
    "addComponentView",
    "addComponentWirePort",
    "removeComponentAddressSpace",
    "removeComponentBusInterface",
    "removeComponentChannel",
    "removeComponentChoice",
    "removeComponentClearboxElement",
    "removeComponentComponentGenerator",
    "removeComponentComponentInstantiation",
    "removeComponentCpu",
    "removeComponentDesignConfigurationInstantiation",
    "removeComponentDesignInstantiation",
    "removeComponentFileSet",
    "removeComponentIndirectInterface",
    "removeComponentMemoryMap",
    "removeComponentMode",
    "removeComponentOtherClockDriver",
    "removeComponentPort",
    "removeComponentResetType",
    "removeComponentView",
]

# ---------------------------------------------------------------------------
# Helpers (non-spec)
# ---------------------------------------------------------------------------

def _resolve_component(componentID: str) -> ComponentType:
    obj = resolve_handle(componentID)
    if not isinstance(obj, ComponentType):
        raise TgiError("Invalid component handle", TgiFaultCode.INVALID_ID)
    return obj


def _list(container: Any, attr: str) -> list[Any]:
    if container is None:
        return []
    value = getattr(container, attr, None)
    if value is None:
        return []
    if isinstance(value, list):  # already a list
        return value
    # Some inner container dataclasses expose e.g. file_set inside file_sets
    singular = attr.rstrip("s")
    inner = getattr(value, singular, None)
    if isinstance(inner, list):
        return inner
    try:  # pragma: no cover - defensive
        return list(value)
    except Exception:  # pragma: no cover
        return []


def _ids(items: Iterable[Any]) -> list[str]:
    return [get_handle(i) for i in items]


def _append_list(container_obj: Any, list_attr: str, item: Any):
    lst = getattr(container_obj, list_attr)
    lst.append(item)  # type: ignore[attr-defined]


def _remove_from_list(container_obj: Any, list_attr: str, target: Any) -> bool:
    lst = list(getattr(container_obj, list_attr))  # type: ignore[attr-defined]
    kept = []
    removed = False
    for obj in lst:
        if obj is target and not removed:
            removed = True
            continue
        kept.append(obj)
    if removed:
        setattr(container_obj, list_attr, kept)  # type: ignore[arg-type]
    return removed


def _ensure_container(component: ComponentType, attr: str, cls: type, list_field: str):
    cur = getattr(component, attr)
    if cur is None:
        setattr(component, attr, cls(**{list_field: []}))  # type: ignore[arg-type]
    return getattr(component, attr)


def _ensure_model(component: ComponentType):  # create empty model scaffold if absent
    from org.accellera.ipxact.v1685_2022.model import Model

    if component.model is None:
        component.model = Model()  # type: ignore[arg-type]
    return component.model


# ---------------------------------------------------------------------------
# BASE (F.7.29)
# ---------------------------------------------------------------------------

def getComponentAddressSpaceIDs(componentID: str) -> list[str]:
    """Return handles of all ``addressSpace`` elements.

    Section: F.7.29.1.
    """
    comp = _resolve_component(componentID)
    return _ids(_list(comp.address_spaces, "address_space"))


def getComponentBusInterfaceIDs(componentID: str) -> list[str]:
    """Return handles of all ``busInterface`` elements.

    Section: F.7.29.2.
    """
    comp = _resolve_component(componentID)
    return _ids(_list(comp.bus_interfaces, "bus_interface"))


def getComponentChannelIDs(componentID: str) -> list[str]:
    """Return handles of all ``channel`` elements.

    Section: F.7.29.3.
    """
    comp = _resolve_component(componentID)
    return _ids(_list(comp.channels, "channel"))


def getComponentChoiceIDs(componentID: str) -> list[str]:
    """Return handles of all ``choice`` elements.

    Section: F.7.29.4.
    """
    comp = _resolve_component(componentID)
    return _ids(_list(comp.choices, "choice"))


def getComponentClearboxElementIDs(componentID: str) -> list[str]:
    """Return handles of ``clearboxElement`` children.

    Section: F.7.29.5.
    """
    comp = _resolve_component(componentID)
    return _ids(_list(comp.clearbox_elements, "clearbox_element"))


def getComponentComponentGeneratorIDs(componentID: str) -> list[str]:
    """Return handles of ``componentGenerator`` children.

    Section: F.7.29.6.
    """
    comp = _resolve_component(componentID)
    return _ids(_list(comp.component_generators, "component_generator"))


def getComponentComponentInstantiationIDs(componentID: str) -> list[str]:
    """Return handles of ``componentInstantiation`` elements in ``model``.

    Section: F.7.29.7.
    """
    comp = _resolve_component(componentID)
    model = comp.model
    if model is None or model.instantiations is None:
        return []
    return _ids(_list(model.instantiations, "component_instantiation"))


def getComponentCpuIDs(componentID: str) -> list[str]:
    """Return handles of ``cpu`` elements.

    Section: F.7.29.8.
    """
    comp = _resolve_component(componentID)
    return _ids(_list(comp.cpus, "cpu"))


def getComponentDesignConfigurationInstantiationIDs(componentID: str) -> list[str]:
    """Return handles of ``designConfigurationInstantiation`` elements.

    Section: F.7.29.9.
    """
    comp = _resolve_component(componentID)
    model = comp.model
    if model is None or model.instantiations is None:
        return []
    return _ids(_list(model.instantiations, "design_configuration_instantiation"))


def getComponentDesignInstantiationIDs(componentID: str) -> list[str]:
    """Return handles of ``designInstantiation`` elements.

    Section: F.7.29.10.
    """
    comp = _resolve_component(componentID)
    model = comp.model
    if model is None or model.instantiations is None:
        return []
    return _ids(_list(model.instantiations, "design_instantiation"))


def getComponentExternalTypeDefinitionsIDs(componentID: str) -> list[str]:
    """Return handles of ``externalTypeDefinitions`` elements.

    Section: F.7.29.11.
    """
    comp = _resolve_component(componentID)
    td = comp.type_definitions
    if td is None:
        return []
    return _ids(_list(td, "external_type_definitions"))


def getComponentFileSetIDs(componentID: str) -> list[str]:
    """Return handles of ``fileSet`` elements.

    Section: F.7.29.12.
    """
    comp = _resolve_component(componentID)
    return _ids(_list(comp.file_sets, "file_set"))


def getComponentIndirectInterfaceIDs(componentID: str) -> list[str]:
    """Return handles of ``indirectInterface`` elements.

    Section: F.7.29.13.
    """
    comp = _resolve_component(componentID)
    return _ids(_list(comp.indirect_interfaces, "indirect_interface"))


def getComponentMemoryMapIDs(componentID: str) -> list[str]:
    """Return handles of ``memoryMap`` elements.

    Section: F.7.29.14.
    """
    comp = _resolve_component(componentID)
    return _ids(_list(comp.memory_maps, "memory_map"))


def getComponentModeIDs(componentID: str) -> list[str]:
    """Return handles of ``mode`` elements.

    Section: F.7.29.15.
    """
    comp = _resolve_component(componentID)
    return _ids(_list(comp.modes, "mode"))


def getComponentOtherClockDriverIDs(componentID: str) -> list[str]:
    """Return handles of ``otherClockDriver`` elements.

    Section: F.7.29.16.
    """
    comp = _resolve_component(componentID)
    return _ids(_list(comp.other_clock_drivers, "other_clock"))


def getComponentPortIDs(componentID: str) -> list[str]:
    """Return handles of model ``port`` elements (all styles).

    Section: F.7.29.17.
    """
    comp = _resolve_component(componentID)
    model = comp.model
    if model is None or model.ports is None:
        return []
    return _ids(_list(model.ports, "port"))


def getComponentPowerDomainIDs(componentID: str) -> list[str]:
    """Return handles of ``powerDomain`` elements.

    Section: F.7.29.18.
    """
    comp = _resolve_component(componentID)
    return _ids(_list(comp.power_domains, "power_domain"))


def getComponentResetTypeIDs(componentID: str) -> list[str]:
    """Return handles of ``resetType`` elements.

    Section: F.7.29.19.
    """
    comp = _resolve_component(componentID)
    return _ids(_list(comp.reset_types, "reset_type"))


def getComponentSelectedViewIDs(componentID: str) -> list[str]:
    """Return handles of ``selectedView`` elements.

    Section: F.7.29.20.
    """
    comp = _resolve_component(componentID)
    model = comp.model
    if model is None or model.views is None:
        return []
    return _ids(_list(model.views, "selected_view"))


# ---------------------------------------------------------------------------
# EXTENDED (F.7.30) – creation
# ---------------------------------------------------------------------------

def addComponentAddressSpace(componentID: str, name: str) -> str:
    """Add an ``addressSpace`` element.

    Section: F.7.30.1.
    """
    comp = _resolve_component(componentID)
    # Local simplified addressSpace helper generated under tgi tree (mirrors schema shape)
    from .address_space import AddressSpace  # type: ignore
    from org.accellera.ipxact.v1685_2022.address_spaces import AddressSpaces

    if comp.address_spaces is None:
        comp.address_spaces = AddressSpaces(address_space=[])  # type: ignore[arg-type]
    obj = AddressSpace(name=name)
    comp.address_spaces.address_space.append(obj)  # type: ignore[attr-defined]
    return get_handle(obj)


def addComponentChannel(componentID: str, name: str) -> str:
    """Add a ``channel`` element.

    Section: F.7.30.2.
    """
    comp = _resolve_component(componentID)
    from org.accellera.ipxact.v1685_2022.channels import Channels
    # Single channel element type lives inside channels container as 'channel'
    from org.accellera.ipxact.v1685_2022.channels import Channel  # type: ignore

    if comp.channels is None:
        comp.channels = Channels(channel=[])  # type: ignore[arg-type]
    ch = Channel(name=name)
    comp.channels.channel.append(ch)  # type: ignore[attr-defined]
    return get_handle(ch)


def addComponentChoice(componentID: str, name: str) -> str:
    """Add a ``choice`` element (no enumerations yet).

    Section: F.7.30.3.
    """
    comp = _resolve_component(componentID)
    from org.accellera.ipxact.v1685_2022.choices import Choices

    if comp.choices is None:
        comp.choices = Choices(choice=[])  # type: ignore[arg-type]
    # Embedded dataclass generated within container
    choice_cls = Choices.Choice  # type: ignore[attr-defined]
    obj = choice_cls(name=name)  # type: ignore[call-arg]
    comp.choices.choice.append(obj)  # type: ignore[attr-defined]
    return get_handle(obj)


def addComponentClearboxElement(componentID: str, name: str | None = None) -> str:
    """Add a ``clearboxElement``.

    Section: F.7.30.4. Name is optional (schema may not define one).
    """
    comp = _resolve_component(componentID)
    if comp.clearbox_elements is None:
        from org.accellera.ipxact.v1685_2022.component_type import ComponentType as _CT

        comp.clearbox_elements = _CT.ClearboxElements(clearbox_element=[])  # type: ignore[arg-type]
    from org.accellera.ipxact.v1685_2022.clearbox_element_type import ClearboxElementType

    el = ClearboxElementType()
    if name is not None:
        el.name = name  # type: ignore[attr-defined]
    comp.clearbox_elements.clearbox_element.append(el)  # type: ignore[attr-defined]
    return get_handle(el)


def addComponentComponentGenerator(componentID: str, name: str) -> str:
    """Add a ``componentGenerator`` element.

    Section: F.7.30.5.
    """
    comp = _resolve_component(componentID)
    from org.accellera.ipxact.v1685_2022.component_generators import ComponentGenerators
    from org.accellera.ipxact.v1685_2022.generator import Generator

    if comp.component_generators is None:
        comp.component_generators = ComponentGenerators(component_generator=[])  # type: ignore[arg-type]
    gen = Generator(name=name)
    comp.component_generators.component_generator.append(gen)  # type: ignore[attr-defined]
    return get_handle(gen)


def addComponentComponentInstantiation(componentID: str, name: str) -> str:
    """Add a ``componentInstantiation`` (model.instantiations).

    Section: F.7.30.6.
    """
    comp = _resolve_component(componentID)
    model = _ensure_model(comp)
    from org.accellera.ipxact.v1685_2022.model import Instantiations  # type: ignore
    from org.accellera.ipxact.v1685_2022.component_instantiation_type import ComponentInstantiationType

    if model.instantiations is None:
        model.instantiations = Instantiations(
            component_instantiation=[],
            design_instantiation=[],
            design_configuration_instantiation=[],
        )  # type: ignore[arg-type]
    ci = ComponentInstantiationType(name=name)
    model.instantiations.component_instantiation.append(ci)  # type: ignore[attr-defined]
    return get_handle(ci)


def addComponentCpu(componentID: str, name: str) -> str:
    """Add a ``cpu`` element.

    Section: F.7.30.7.
    """
    comp = _resolve_component(componentID)
    from org.accellera.ipxact.v1685_2022.component_type import ComponentType as CT

    if comp.cpus is None:
        comp.cpus = CT.Cpus(cpu=[])  # type: ignore[arg-type]
    cpu_cls = CT.Cpus.Cpu
    cpu = cpu_cls(name=name)  # type: ignore[call-arg]
    comp.cpus.cpu.append(cpu)  # type: ignore[attr-defined]
    return get_handle(cpu)


def addComponentDesignConfigurationInstantiation(componentID: str, name: str) -> str:
    """Add a ``designConfigurationInstantiation``.

    Section: F.7.30.8.
    """
    comp = _resolve_component(componentID)
    model = _ensure_model(comp)
    from org.accellera.ipxact.v1685_2022.model import Instantiations  # type: ignore
    from .design_configuration_instantiation import DesignConfigurationInstantiation  # type: ignore

    if model.instantiations is None:
        model.instantiations = Instantiations(
            component_instantiation=[],
            design_instantiation=[],
            design_configuration_instantiation=[],
        )  # type: ignore[arg-type]
    dci = DesignConfigurationInstantiation(name=name)
    model.instantiations.design_configuration_instantiation.append(dci)  # type: ignore[attr-defined]
    return get_handle(dci)


def addComponentDesignInstantiation(componentID: str, name: str) -> str:
    """Add a ``designInstantiation``.

    Section: F.7.30.9.
    """
    comp = _resolve_component(componentID)
    model = _ensure_model(comp)
    from org.accellera.ipxact.v1685_2022.model import Instantiations  # type: ignore
    from .design_instantiation import DesignInstantiation  # type: ignore

    if model.instantiations is None:
        model.instantiations = Instantiations(
            component_instantiation=[],
            design_instantiation=[],
            design_configuration_instantiation=[],
        )  # type: ignore[arg-type]
    di = DesignInstantiation(name=name)
    model.instantiations.design_instantiation.append(di)  # type: ignore[attr-defined]
    return get_handle(di)


def addComponentFileSet(componentID: str, name: str) -> str:
    """Add a ``fileSet`` element.

    Section: F.7.30.10.
    """
    comp = _resolve_component(componentID)
    from org.accellera.ipxact.v1685_2022.file_sets import FileSets
    from org.accellera.ipxact.v1685_2022.file_set import FileSet

    if comp.file_sets is None:
        comp.file_sets = FileSets(file_set=[])  # type: ignore[arg-type]
    fs = FileSet(name=name)
    comp.file_sets.file_set.append(fs)  # type: ignore[attr-defined]
    return get_handle(fs)


def addComponentIndirectInterface(componentID: str, name: str) -> str:
    """Add an ``indirectInterface`` element.

    Section: F.7.30.11.
    """
    comp = _resolve_component(componentID)
    from org.accellera.ipxact.v1685_2022.indirect_interfaces import IndirectInterfaces
    from org.accellera.ipxact.v1685_2022.indirect_interface import IndirectInterface

    if comp.indirect_interfaces is None:
        comp.indirect_interfaces = IndirectInterfaces(indirect_interface=[])  # type: ignore[arg-type]
    ii = IndirectInterface(name=name)
    comp.indirect_interfaces.indirect_interface.append(ii)  # type: ignore[attr-defined]
    return get_handle(ii)


def _add_bus_interface(component: ComponentType, name: str, kind: str) -> str:
    from org.accellera.ipxact.v1685_2022.bus_interfaces import BusInterfaces
    from org.accellera.ipxact.v1685_2022.bus_interface_type import BusInterfaceType

    if component.bus_interfaces is None:
        component.bus_interfaces = BusInterfaces(bus_interface=[])  # type: ignore[arg-type]
    bi = BusInterfaceType(name=name)
    # Mark role using a vendor extension attribute if no direct field; keep lightweight.
    bi._tgi_role = kind  # type: ignore[attr-defined]
    component.bus_interfaces.bus_interface.append(bi)  # type: ignore[attr-defined]
    return get_handle(bi)


def addComponentInitiatorBusInterface(componentID: str, name: str) -> str:
    """Add an initiator ``busInterface``.

    Section: F.7.30.12.
    """
    return _add_bus_interface(_resolve_component(componentID), name, "initiator")


def addComponentMemoryMap(componentID: str, name: str) -> str:
    """Add a ``memoryMap`` element.

    Section: F.7.30.13.
    """
    comp = _resolve_component(componentID)
    from org.accellera.ipxact.v1685_2022.memory_maps import MemoryMaps
    from .memory_map import MemoryMap  # type: ignore

    if comp.memory_maps is None:
        comp.memory_maps = MemoryMaps(memory_map=[])  # type: ignore[arg-type]
    mm = MemoryMap(name=name)
    comp.memory_maps.memory_map.append(mm)  # type: ignore[attr-defined]
    return get_handle(mm)


def addComponentMirroredInitiatorBusInterface(componentID: str, name: str) -> str:
    """Add a mirrored initiator ``busInterface``.

    Section: F.7.30.14.
    """
    return _add_bus_interface(_resolve_component(componentID), name, "mirroredInitiator")


def addComponentMirroredSystemBusInterface(componentID: str, name: str) -> str:
    """Add a mirrored system ``busInterface``.

    Section: F.7.30.15.
    """
    return _add_bus_interface(_resolve_component(componentID), name, "mirroredSystem")


def addComponentMirroredTargetBusInterface(componentID: str, name: str) -> str:
    """Add a mirrored target ``busInterface``.

    Section: F.7.30.16.
    """
    return _add_bus_interface(_resolve_component(componentID), name, "mirroredTarget")


def addComponentMode(componentID: str, name: str) -> str:
    """Add a ``mode`` element.

    Section: F.7.30.17.
    """
    comp = _resolve_component(componentID)
    from org.accellera.ipxact.v1685_2022.component_type import ComponentType as CT

    if comp.modes is None:
        comp.modes = CT.Modes(mode=[])  # type: ignore[arg-type]
    mode_cls = CT.Modes.Mode
    md = mode_cls(name=name)  # type: ignore[call-arg]
    comp.modes.mode.append(md)  # type: ignore[attr-defined]
    return get_handle(md)


def addComponentMonitorBusInterface(componentID: str, name: str) -> str:
    """Add a monitor ``busInterface``.

    Section: F.7.30.18.
    """
    return _add_bus_interface(_resolve_component(componentID), name, "monitor")


def addComponentOtherClockDriver(componentID: str, name: str) -> str:
    """Add an ``otherClockDriver`` element.

    Section: F.7.30.19.
    """
    comp = _resolve_component(componentID)
    from org.accellera.ipxact.v1685_2022.other_clocks import OtherClocks
    from org.accellera.ipxact.v1685_2022.other_clock_driver import (
        OtherClockDriver as OtherClock,
    )

    if comp.other_clock_drivers is None:
        comp.other_clock_drivers = OtherClocks(other_clock=[])  # type: ignore[arg-type]
    # Schema uses attribute clock_name instead of name
    oc = OtherClock(clock_name=name)
    comp.other_clock_drivers.other_clock.append(oc)  # type: ignore[attr-defined]
    return get_handle(oc)


def addComponentResetType(componentID: str, name: str) -> str:
    """Add a ``resetType`` element.

    Section: F.7.30.20.
    """
    comp = _resolve_component(componentID)
    from org.accellera.ipxact.v1685_2022.component_type import ComponentType as CT

    if comp.reset_types is None:
        comp.reset_types = CT.ResetTypes(reset_type=[])  # type: ignore[arg-type]
    rt = CT.ResetTypes.ResetType(name=name)  # type: ignore[call-arg]
    comp.reset_types.reset_type.append(rt)  # type: ignore[attr-defined]
    return get_handle(rt)


def _add_structured_port(
    component: ComponentType,
    name: str,
    kind: str,
    subPortName: str | None = None,
    typeName: str | None = None,
    direction: str | None = None,
) -> str:
    model = _ensure_model(component)
    from org.accellera.ipxact.v1685_2022.port_type import PortType
    from org.accellera.ipxact.v1685_2022.model import Ports  # type: ignore

    if model.ports is None:
        model.ports = Ports(port=[])  # type: ignore[arg-type]
    pt = PortType(name=name)
    pt._tgi_portKind = kind  # type: ignore[attr-defined]
    if subPortName is not None:
        pt._tgi_subPort = subPortName  # type: ignore[attr-defined]
    if typeName is not None:
        pt._tgi_typeDef = typeName  # type: ignore[attr-defined]
    if direction is not None:
        pt._tgi_direction = direction  # type: ignore[attr-defined]
    model.ports.port.append(pt)  # type: ignore[attr-defined]
    return get_handle(pt)


def addComponentStructuredInterfacePort(
    componentID: str,
    name: str,
    subPortName: str,
    structPortTypeDefTypeName: str,
) -> str:
    """Add a structured interface port.

    Section: F.7.30.21.
    """
    return _add_structured_port(
        _resolve_component(componentID),
        name,
        "structuredInterface",
        subPortName,
        structPortTypeDefTypeName,
    )


def addComponentStructuredStructPort(
    componentID: str,
    name: str,
    subPortName: str,
    structPortTypeDefTypeName: str,
) -> str:
    """Add a structured struct port.

    Section: F.7.30.22.
    """
    return _add_structured_port(
        _resolve_component(componentID),
        name,
        "structuredStruct",
        subPortName,
        structPortTypeDefTypeName,
    )


def addComponentStructuredUnionPort(
    componentID: str,
    name: str,
    structPortTypeDefTypeName: str,
    subPortName: str,
) -> str:
    """Add a structured union port.

    Section: F.7.30.23.
    """
    return _add_structured_port(
        _resolve_component(componentID),
        name,
        "structuredUnion",
        subPortName,
        structPortTypeDefTypeName,
    )


def addComponentSystemBusInterface(componentID: str, name: str) -> str:
    """Add a system ``busInterface``.

    Section: F.7.30.24.
    """
    return _add_bus_interface(_resolve_component(componentID), name, "system")


def addComponentTargetBusInterface(componentID: str, name: str) -> str:
    """Add a target ``busInterface``.

    Section: F.7.30.25.
    """
    return _add_bus_interface(_resolve_component(componentID), name, "target")


def addComponentTransactionalPort(componentID: str, name: str) -> str:
    """Add a transactional port.

    Section: F.7.30.26.
    """
    return _add_structured_port(_resolve_component(componentID), name, "transactional")


def addComponentView(componentID: str, name: str) -> str:
    """Add a ``view`` element.

    Section: F.7.30.27.
    """
    comp = _resolve_component(componentID)
    model = _ensure_model(comp)
    from .view import View  # type: ignore
    from org.accellera.ipxact.v1685_2022.model import Views  # type: ignore

    if model.views is None:
        model.views = Views(view=[], selected_view=[])  # type: ignore[arg-type]
    vw = View(name=name)
    model.views.view.append(vw)  # type: ignore[attr-defined]
    return get_handle(vw)


def addComponentWirePort(componentID: str, name: str, direction: str | None = None) -> str:
    """Add a wire port.

    Section: F.7.30.28.
    """
    return _add_structured_port(_resolve_component(componentID), name, "wire", direction=direction)


# ---------------------------------------------------------------------------
# EXTENDED removal (F.7.30.xx)
# ---------------------------------------------------------------------------

def _remove(container, list_attr: str, handle: str) -> bool:
    from .core import resolve_handle as _res

    target = _res(handle)
    if target is None:
        return False
    return _remove_from_list(container, list_attr, target)


def removeComponentAddressSpace(componentID: str, addressSpaceID: str) -> bool:
    """Remove an ``addressSpace``.

    Section: F.7.30.29.
    """
    comp = _resolve_component(componentID)
    if comp.address_spaces is None:
        return False
    return _remove(comp.address_spaces, "address_space", addressSpaceID)


def removeComponentBusInterface(componentID: str, busInterfaceID: str) -> bool:
    """Remove a ``busInterface`` (any role).

    Section: F.7.30.30.
    """
    comp = _resolve_component(componentID)
    if comp.bus_interfaces is None:
        return False
    return _remove(comp.bus_interfaces, "bus_interface", busInterfaceID)


def removeComponentChannel(componentID: str, channelID: str) -> bool:
    """Remove a ``channel``.

    Section: F.7.30.31.
    """
    comp = _resolve_component(componentID)
    if comp.channels is None:
        return False
    return _remove(comp.channels, "channel", channelID)


def removeComponentChoice(componentID: str, choiceID: str) -> bool:
    """Remove a ``choice``.

    Section: F.7.30.32.
    """
    comp = _resolve_component(componentID)
    if comp.choices is None:
        return False
    return _remove(comp.choices, "choice", choiceID)


def removeComponentClearboxElement(componentID: str, clearboxElementID: str) -> bool:
    """Remove a ``clearboxElement``.

    Section: F.7.30.33.
    """
    comp = _resolve_component(componentID)
    if comp.clearbox_elements is None:
        return False
    return _remove(comp.clearbox_elements, "clearbox_element", clearboxElementID)


def removeComponentComponentGenerator(componentID: str, componentGeneratorID: str) -> bool:
    """Remove a ``componentGenerator``.

    Section: F.7.30.34.
    """
    comp = _resolve_component(componentID)
    if comp.component_generators is None:
        return False
    return _remove(comp.component_generators, "component_generator", componentGeneratorID)


def removeComponentComponentInstantiation(componentID: str, componentInstantiationID: str) -> bool:
    """Remove a ``componentInstantiation``.

    Section: F.7.30.35.
    """
    comp = _resolve_component(componentID)
    model = comp.model
    if model is None or model.instantiations is None:
        return False
    return _remove(model.instantiations, "component_instantiation", componentInstantiationID)


def removeComponentCpu(componentID: str, cpuID: str) -> bool:
    """Remove a ``cpu`` element.

    Section: F.7.30.36.
    """
    comp = _resolve_component(componentID)
    if comp.cpus is None:
        return False
    return _remove(comp.cpus, "cpu", cpuID)


def removeComponentDesignConfigurationInstantiation(componentID: str, designConfigurationInstantiationID: str) -> bool:
    """Remove a ``designConfigurationInstantiation``.

    Section: F.7.30.37.
    """
    comp = _resolve_component(componentID)
    model = comp.model
    if model is None or model.instantiations is None:
        return False
    return _remove(model.instantiations, "design_configuration_instantiation", designConfigurationInstantiationID)


def removeComponentDesignInstantiation(componentID: str, designInstantiationID: str) -> bool:
    """Remove a ``designInstantiation``.

    Section: F.7.30.38.
    """
    comp = _resolve_component(componentID)
    model = comp.model
    if model is None or model.instantiations is None:
        return False
    return _remove(model.instantiations, "design_instantiation", designInstantiationID)


def removeComponentFileSet(componentID: str, fileSetID: str) -> bool:
    """Remove a ``fileSet``.

    Section: F.7.30.39.
    """
    comp = _resolve_component(componentID)
    if comp.file_sets is None:
        return False
    return _remove(comp.file_sets, "file_set", fileSetID)


def removeComponentIndirectInterface(componentID: str, indirectInterfaceID: str) -> bool:
    """Remove an ``indirectInterface``.

    Section: F.7.30.40.
    """
    comp = _resolve_component(componentID)
    if comp.indirect_interfaces is None:
        return False
    return _remove(comp.indirect_interfaces, "indirect_interface", indirectInterfaceID)


def removeComponentMemoryMap(componentID: str, memoryMapID: str) -> bool:
    """Remove a ``memoryMap``.

    Section: F.7.30.41.
    """
    comp = _resolve_component(componentID)
    if comp.memory_maps is None:
        return False
    return _remove(comp.memory_maps, "memory_map", memoryMapID)


def removeComponentMode(componentID: str, modeID: str) -> bool:
    """Remove a ``mode``.

    Section: F.7.30.42.
    """
    comp = _resolve_component(componentID)
    if comp.modes is None:
        return False
    return _remove(comp.modes, "mode", modeID)


def removeComponentOtherClockDriver(componentID: str, otherClockDriverID: str) -> bool:
    """Remove an ``otherClockDriver``.

    Section: F.7.30.43.
    """
    comp = _resolve_component(componentID)
    if comp.other_clock_drivers is None:
        return False
    return _remove(comp.other_clock_drivers, "other_clock", otherClockDriverID)


def removeComponentPort(componentID: str, portID: str) -> bool:
    """Remove a ``port`` (any style) from model.ports.

    Section: F.7.30.44.
    """
    comp = _resolve_component(componentID)
    model = comp.model
    if model is None or model.ports is None:
        return False
    return _remove(model.ports, "port", portID)


def removeComponentResetType(componentID: str, resetTypeID: str) -> bool:
    """Remove a ``resetType`` element.

    Section: F.7.30.45.
    """
    comp = _resolve_component(componentID)
    if comp.reset_types is None:
        return False
    return _remove(comp.reset_types, "reset_type", resetTypeID)


def removeComponentView(componentID: str, viewID: str) -> bool:
    """Remove a ``view`` element.

    Section: F.7.30.46.
    """
    comp = _resolve_component(componentID)
    model = comp.model
    if model is None or model.views is None:
        return False
    return _remove(model.views, "view", viewID)


