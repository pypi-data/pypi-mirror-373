"""Abstractor category TGI functions (IEEE 1685-2022).

Implements BASE (F.7.4) and EXTENDED (F.7.5) Abstractor functions. Only 2022
standard APIs are exposed here. Functions raise :class:`TgiError` with
``TgiFaultCode.INVALID_ID`` for invalid handles and ``TgiFaultCode.INVALID_ARGUMENT``
for semantic violations as per the general TGI error model.
"""
# ruff: noqa: I001
from __future__ import annotations

from org.accellera.ipxact.v1685_2022 import (
    Abstractor,
    AbstractorGenerator,
    AbstractorGenerators,
    AbstractorPortType,
    Choices,
    FileSet,
    FileSets,
)
from org.accellera.ipxact.v1685_2022.abstractor_type import AbstractorType
from org.accellera.ipxact.v1685_2022.abstraction_types import AbstractionTypes
from org.accellera.ipxact.v1685_2022.configurable_library_ref_type import ConfigurableLibraryRefType
from org.accellera.ipxact.v1685_2022.library_ref_type import LibraryRefType

from .core import (
    TgiError,
    TgiFaultCode,
    get_handle,
    resolve_handle,
    register_parent,
    detach_child_by_handle,
)

__all__ = [
    # BASE (F.7.4)
    "getAbstractorAbstractorGeneratorIDs",
    "getAbstractorAbstractorInterfaceIDs",
    "getAbstractorAbstractorMode",
    "getAbstractorAbstractorModeID",
    "getAbstractorBusTypeRefByVLNV",
    "getAbstractorChoiceIDs",
    "getAbstractorComponentInstantiationIDs",
    "getAbstractorFileSetIDs",
    "getAbstractorInterfaceAbstractionTypeIDs",
    "getAbstractorPortIDs",
    "getAbstractorViewIDs",
    # EXTENDED (F.7.5)
    "addAbstractorAbstractorGenerator",
    "addAbstractorChoice",
    "addAbstractorComponentInstantiation",
    "addAbstractorFileSet",
    "addAbstractorInterfaceAbstractionType",
    "addAbstractorTransactionalPort",
    "addAbstractorWirePort",
    "addAbstractorStructuredInterfacePort",
    "addAbstractorStructuredStructPort",
    "addAbstractorStructuredUnionPort",
    "addAbstractorView",
    "removeAbstractorAbstractorGenerator",
    "removeAbstractorChoice",
    "removeAbstractorComponentInstantiation",
    "removeAbstractorFileSet",
    "removeAbstractorInterfaceAbstractionType",
    "removeAbstractorPort",
    "removeAbstractorView",
    "setAbstractorAbstractorMode",
    "setAbstractorBusType",
]


def _resolve(abstractorID: str) -> Abstractor | None:  # helper (non-spec)
    obj = resolve_handle(abstractorID)
    return obj if isinstance(obj, Abstractor) else None


def _resolve_port(portID: str) -> AbstractorPortType | None:  # helper
    obj = resolve_handle(portID)
    return obj if isinstance(obj, AbstractorPortType) else None


# ---------------------------------------------------------------------------
# BASE (F.7.4)
# ---------------------------------------------------------------------------

def getAbstractorAbstractorGeneratorIDs(abstractorID: str) -> list[str]:
    """Return handles of all ``abstractorGenerator`` children.

    Section: F.7.4.1.
    """
    a = _resolve(abstractorID)
    if a is None:
        raise TgiError("Invalid abstractor handle", TgiFaultCode.INVALID_ID)
    if a.abstractor_generators is None:
        return []
    return [get_handle(g) for g in getattr(a.abstractor_generators, "abstractor_generator", [])]


def getAbstractorAbstractorInterfaceIDs(abstractorID: str) -> list[str]:
    """Return handles of the exactly two abstractorInterface elements.

    Section: F.7.4.2.
    """
    a = _resolve(abstractorID)
    if a is None:
        raise TgiError("Invalid abstractor handle", TgiFaultCode.INVALID_ID)
    if a.abstractor_interfaces is None:
        return []
    return [get_handle(i) for i in getattr(a.abstractor_interfaces, "abstractor_interface", [])]


def getAbstractorAbstractorMode(abstractorID: str) -> tuple[str | None, str | None]:
    """Return (modeValue, group) for the abstractorMode element.

    Section: F.7.4.3. Returns (None, None) if not present.
    """
    a = _resolve(abstractorID)
    if a is None:
        raise TgiError("Invalid abstractor handle", TgiFaultCode.INVALID_ID)
    am = a.abstractor_mode
    if am is None:
        return (None, None)
    val = getattr(am, "value", None)
    mode_val = getattr(val, "value", None) if val is not None else None
    return (mode_val, getattr(am, "group", None))


def getAbstractorAbstractorModeID(abstractorID: str) -> str | None:
    """Return handle of the ``abstractorMode`` element.

    Section: F.7.4.4. Returns None if absent.
    """
    a = _resolve(abstractorID)
    if a is None:
        raise TgiError("Invalid abstractor handle", TgiFaultCode.INVALID_ID)
    am = a.abstractor_mode
    return None if am is None else get_handle(am)


def getAbstractorBusTypeRefByVLNV(abstractorID: str) -> tuple[str | None, str | None, str | None, str | None]:
    """Return busType VLNV reference.

    Section: F.7.4.5.
    """
    a = _resolve(abstractorID)
    if a is None:
        raise TgiError("Invalid abstractor handle", TgiFaultCode.INVALID_ID)
    bt = a.bus_type
    if bt is None:
        return (None, None, None, None)
    return (bt.vendor, bt.library, bt.name, bt.version)


def getAbstractorChoiceIDs(abstractorID: str) -> list[str]:
    """Return handles of ``choice`` children.

    Section: F.7.4.6.
    """
    a = _resolve(abstractorID)
    if a is None:
        raise TgiError("Invalid abstractor handle", TgiFaultCode.INVALID_ID)
    if a.choices is None:
        return []
    return [get_handle(c) for c in getattr(a.choices, "choice", [])]


def getAbstractorComponentInstantiationIDs(abstractorID: str) -> list[str]:
    """Return handles of componentInstantiation elements in model.instantiations.

    Section: F.7.4.7.
    """
    a = _resolve(abstractorID)
    if a is None:
        raise TgiError("Invalid abstractor handle", TgiFaultCode.INVALID_ID)
    model = a.model
    if model is None or model.instantiations is None:
        return []
    return [get_handle(ci) for ci in getattr(model.instantiations, "component_instantiation", [])]


def getAbstractorFileSetIDs(abstractorID: str) -> list[str]:
    """Return handles of fileSet children.

    Section: F.7.4.8.
    """
    a = _resolve(abstractorID)
    if a is None:
        raise TgiError("Invalid abstractor handle", TgiFaultCode.INVALID_ID)
    if a.file_sets is None:
        return []
    return [get_handle(fs) for fs in getattr(a.file_sets, "file_set", [])]


def getAbstractorInterfaceAbstractionTypeIDs(abstractorID: str) -> list[str]:
    """Return handles of abstractionType elements of both abstractorInterfaces.

    Section: F.7.4.9.
    """
    a = _resolve(abstractorID)
    if a is None:
        raise TgiError("Invalid abstractor handle", TgiFaultCode.INVALID_ID)
    if a.abstractor_interfaces is None:
        return []
    ids: list[str] = []
    for iface in getattr(a.abstractor_interfaces, "abstractor_interface", []):
        if iface.abstraction_types is None:
            continue
        for at in getattr(iface.abstraction_types, "abstraction_type", []):
            ids.append(get_handle(at))
    return ids


def getAbstractorPortIDs(abstractorID: str) -> list[str]:
    """Return handles of all abstractor model ports.

    Section: F.7.4.10.
    """
    a = _resolve(abstractorID)
    if a is None:
        raise TgiError("Invalid abstractor handle", TgiFaultCode.INVALID_ID)
    model = a.model
    if model is None or model.ports is None:
        return []
    return [get_handle(p) for p in getattr(model.ports, "port", [])]


def getAbstractorViewIDs(abstractorID: str) -> list[str]:
    """Return handles of view elements in model.views.

    Section: F.7.4.11.
    """
    a = _resolve(abstractorID)
    if a is None:
        raise TgiError("Invalid abstractor handle", TgiFaultCode.INVALID_ID)
    model = a.model
    if model is None or model.views is None:
        return []
    return [get_handle(v) for v in getattr(model.views, "view", [])]


# ---------------------------------------------------------------------------
# EXTENDED (F.7.5) – creation, removal, set operations
# ---------------------------------------------------------------------------

def addAbstractorAbstractorGenerator(abstractorID: str, name: str, generatorExecutable: str) -> str:
    """Create and append an ``abstractorGenerator``.

    Section: F.7.5.1.
    """
    a = _resolve(abstractorID)
    if a is None:
        raise TgiError("Invalid abstractor handle", TgiFaultCode.INVALID_ID)
    if a.abstractor_generators is None:
        a.abstractor_generators = AbstractorGenerators()
    gen = AbstractorGenerator()
    gen.name = name
    gen.generator_executable = generatorExecutable  # type: ignore[attr-defined]
    a.abstractor_generators.abstractor_generator.append(gen)  # type: ignore[attr-defined]
    register_parent(gen, a, ("abstractor_generators",), "list")
    return get_handle(gen)


def addAbstractorChoice(abstractorID: str, name: str) -> str:
    """Add a ``choice`` element with the given name (no enumerations yet).

    Section: F.7.5.2.
    """
    a = _resolve(abstractorID)
    if a is None:
        raise TgiError("Invalid abstractor handle", TgiFaultCode.INVALID_ID)
    if a.choices is None:
        a.choices = Choices()
    ch = Choices.Choice(name=name)
    a.choices.choice.append(ch)  # type: ignore[attr-defined]
    register_parent(ch, a, ("choices",), "list")
    return get_handle(ch)


def addAbstractorComponentInstantiation(abstractorID: str, name: str) -> str:
    """Add a ``componentInstantiation`` under model.instantiations.

    Section: F.7.5.3.
    """
    from org.accellera.ipxact.v1685_2022.component_instantiation_type import (
        ComponentInstantiationType,
    )
    a = _resolve(abstractorID)
    if a is None:
        raise TgiError("Invalid abstractor handle", TgiFaultCode.INVALID_ID)
    if a.model is None:
        from org.accellera.ipxact.v1685_2022.abstractor_model_type import AbstractorModelType
        a.model = AbstractorModelType()
    if a.model.instantiations is None:
        from org.accellera.ipxact.v1685_2022.abstractor_model_type import AbstractorModelType
        a.model.instantiations = AbstractorModelType.Instantiations()
    ci = ComponentInstantiationType(name=name)
    a.model.instantiations.component_instantiation.append(ci)  # type: ignore[attr-defined]
    register_parent(ci, a, ("model", "instantiations"), "list")
    return get_handle(ci)


def addAbstractorFileSet(abstractorID: str, name: str) -> str:
    """Add a new ``fileSet`` under the abstractor.

    Section: F.7.5.4.
    """
    a = _resolve(abstractorID)
    if a is None:
        raise TgiError("Invalid abstractor handle", TgiFaultCode.INVALID_ID)
    if a.file_sets is None:
        a.file_sets = FileSets()
    fs = FileSet(name=name)
    a.file_sets.file_set.append(fs)  # type: ignore[attr-defined]
    register_parent(fs, a, ("file_sets",), "list")
    return get_handle(fs)


def addAbstractorInterfaceAbstractionType(
    abstractorID: str,
    interfaceIndex: int,
    abstractionRefVLNV: tuple[str, str, str, str],
) -> str:
    """Add an ``abstractionType`` to one of the two abstractorInterfaces.

    Section: F.7.5.5.
    Args:
        interfaceIndex: 0 or 1 selecting which of the two interfaces.
        abstractionRefVLNV: (vendor, library, name, version) of abstractionDef.
    """
    if interfaceIndex not in (0, 1):
        raise TgiError("interfaceIndex must be 0 or 1", TgiFaultCode.INVALID_ARGUMENT)
    a = _resolve(abstractorID)
    if a is None:
        raise TgiError("Invalid abstractor handle", TgiFaultCode.INVALID_ID)
    if a.abstractor_interfaces is None:
        raise TgiError("Abstractor missing interfaces", TgiFaultCode.INVALID_ARGUMENT)
    interfaces = list(getattr(a.abstractor_interfaces, "abstractor_interface", []))
    if len(interfaces) <= interfaceIndex:
        raise TgiError("Interface index out of range", TgiFaultCode.INVALID_ARGUMENT)
    iface = interfaces[interfaceIndex]
    if iface.abstraction_types is None:
        iface.abstraction_types = AbstractionTypes()
    at = AbstractionTypes.AbstractionType(
        abstraction_ref=ConfigurableLibraryRefType(
            vendor=abstractionRefVLNV[0],
            library=abstractionRefVLNV[1],
            name=abstractionRefVLNV[2],
            version=abstractionRefVLNV[3],
        )
    )
    iface.abstraction_types.abstraction_type.append(at)  # type: ignore[attr-defined]
    register_parent(at, iface, ("abstraction_types",), "list")
    return get_handle(at)


def addAbstractorTransactionalPort(abstractorID: str, name: str, initiative: str | None = None) -> str:
    """Add a transactional model port.

    Section: F.7.5.6.
    """
    from org.accellera.ipxact.v1685_2022.abstractor_port_transactional_type import (
        AbstractorPortTransactionalType,
    )
    a = _resolve(abstractorID)
    if a is None:
        raise TgiError("Invalid abstractor handle", TgiFaultCode.INVALID_ID)
    if a.model is None:
        from org.accellera.ipxact.v1685_2022.abstractor_model_type import AbstractorModelType
        a.model = AbstractorModelType()
    if a.model.ports is None:
        from org.accellera.ipxact.v1685_2022.abstractor_model_type import AbstractorModelType
        a.model.ports = AbstractorModelType.Ports()
    p = AbstractorPortType(name=name)
    p.transactional = AbstractorPortTransactionalType()
    if initiative:
        p.transactional.initiative = initiative  # type: ignore[attr-defined]
    a.model.ports.port.append(p)  # type: ignore[attr-defined]
    register_parent(p, a, ("model", "ports"), "list")
    return get_handle(p)


def addAbstractorWirePort(abstractorID: str, name: str, direction: str | None = None) -> str:
    """Add a wire model port.

    Section: F.7.5.7.
    """
    from org.accellera.ipxact.v1685_2022.abstractor_port_wire_type import (
        AbstractorPortWireType,
    )
    a = _resolve(abstractorID)
    if a is None:
        raise TgiError("Invalid abstractor handle", TgiFaultCode.INVALID_ID)
    if a.model is None:
        from org.accellera.ipxact.v1685_2022.abstractor_model_type import AbstractorModelType
        a.model = AbstractorModelType()
    if a.model.ports is None:
        from org.accellera.ipxact.v1685_2022.abstractor_model_type import AbstractorModelType
        a.model.ports = AbstractorModelType.Ports()
    p = AbstractorPortType(name=name)
    p.wire = AbstractorPortWireType()
    if direction:
        p.wire.direction = direction  # type: ignore[attr-defined]
    a.model.ports.port.append(p)  # type: ignore[attr-defined]
    register_parent(p, a, ("model", "ports"), "list")
    return get_handle(p)


def addAbstractorStructuredInterfacePort(
    abstractorID: str,
    name: str,
    subPortName: str,
    structPortTypeDefTypeName: str,
) -> str:
    """Add a structured interface port (adds a subPort reference).

    Section: F.7.5.8.
    """
    from org.accellera.ipxact.v1685_2022.abstractor_sub_port_type import (
        AbstractorPortStructuredType,
        AbstractorSubPortType,
    )
    a = _resolve(abstractorID)
    if a is None:
        raise TgiError("Invalid abstractor handle", TgiFaultCode.INVALID_ID)
    if a.model is None:
        from org.accellera.ipxact.v1685_2022.abstractor_model_type import AbstractorModelType
        a.model = AbstractorModelType()
    if a.model.ports is None:
        from org.accellera.ipxact.v1685_2022.abstractor_model_type import AbstractorModelType
        a.model.ports = AbstractorModelType.Ports()
    p = AbstractorPortType(name=name)
    p.structured = AbstractorPortStructuredType()
    sp = AbstractorSubPortType(name=subPortName)
    p.structured.interface_port.append(sp)  # type: ignore[attr-defined]
    a.model.ports.port.append(p)  # type: ignore[attr-defined]
    register_parent(p, a, ("model", "ports"), "list")
    return get_handle(p)


def addAbstractorStructuredStructPort(
    abstractorID: str,
    name: str,
    subPortName: str,
    structPortTypeDefTypeName: str,
    direction: str | None = None,
) -> str:
    """Add a structured structPort with direction.

    Section: F.7.5.9.
    """
    from org.accellera.ipxact.v1685_2022.abstractor_sub_port_type import (
        AbstractorPortStructuredType,
        AbstractorSubPortType,
    )
    a = _resolve(abstractorID)
    if a is None:
        raise TgiError("Invalid abstractor handle", TgiFaultCode.INVALID_ID)
    if a.model is None:
        from org.accellera.ipxact.v1685_2022.abstractor_model_type import AbstractorModelType
        a.model = AbstractorModelType()
    if a.model.ports is None:
        from org.accellera.ipxact.v1685_2022.abstractor_model_type import AbstractorModelType
        a.model.ports = AbstractorModelType.Ports()
    p = AbstractorPortType(name=name)
    p.structured = AbstractorPortStructuredType()
    sp = AbstractorSubPortType(name=subPortName)
    if direction:
        sp.direction = direction  # type: ignore[attr-defined]
    p.structured.struct_port.append(sp)  # type: ignore[attr-defined]
    a.model.ports.port.append(p)  # type: ignore[attr-defined]
    register_parent(p, a, ("model", "ports"), "list")
    return get_handle(p)


def addAbstractorStructuredUnionPort(
    abstractorID: str,
    name: str,
    structPortTypeDefTypeName: str,
    subPortName: str,
    direction: str | None = None,
) -> str:
    """Add a structured unionPort with direction.

    Section: F.7.5.10.
    """
    from org.accellera.ipxact.v1685_2022.abstractor_sub_port_type import (
        AbstractorPortStructuredType,
        AbstractorSubPortType,
    )
    a = _resolve(abstractorID)
    if a is None:
        raise TgiError("Invalid abstractor handle", TgiFaultCode.INVALID_ID)
    if a.model is None:
        from org.accellera.ipxact.v1685_2022.abstractor_model_type import AbstractorModelType
        a.model = AbstractorModelType()
    if a.model.ports is None:
        from org.accellera.ipxact.v1685_2022.abstractor_model_type import AbstractorModelType
        a.model.ports = AbstractorModelType.Ports()
    p = AbstractorPortType(name=name)
    p.structured = AbstractorPortStructuredType()
    sp = AbstractorSubPortType(name=subPortName)
    if direction:
        sp.direction = direction  # type: ignore[attr-defined]
    p.structured.union_port.append(sp)  # type: ignore[attr-defined]
    a.model.ports.port.append(p)  # type: ignore[attr-defined]
    register_parent(p, a, ("model", "ports"), "list")
    return get_handle(p)


def addAbstractorView(abstractorID: str, name: str) -> str:
    """Add a view element under model.views.

    Section: F.7.5.11.
    """
    from org.accellera.ipxact.v1685_2022.abstractor_model_type import AbstractorModelType
    a = _resolve(abstractorID)
    if a is None:
        raise TgiError("Invalid abstractor handle", TgiFaultCode.INVALID_ID)
    if a.model is None:
        a.model = AbstractorModelType()
    if a.model.views is None:
        a.model.views = AbstractorModelType.Views()
    v = AbstractorModelType.Views.View(name=name)
    a.model.views.view.append(v)  # type: ignore[attr-defined]
    register_parent(v, a, ("model", "views"), "list")
    return get_handle(v)


def removeAbstractorAbstractorGenerator(abstractorGeneratorID: str) -> bool:
    """Remove an abstractorGenerator.

    Section: F.7.5.12.
    """
    return detach_child_by_handle(abstractorGeneratorID)


def removeAbstractorChoice(choiceID: str) -> bool:
    """Remove a choice element.

    Section: F.7.5.13.
    """
    return detach_child_by_handle(choiceID)


def removeAbstractorComponentInstantiation(componentInstantiationID: str) -> bool:
    """Remove a componentInstantiation.

    Section: F.7.5.14.
    """
    return detach_child_by_handle(componentInstantiationID)


def removeAbstractorFileSet(fileSetID: str) -> bool:
    """Remove a fileSet element.

    Section: F.7.5.15.
    """
    return detach_child_by_handle(fileSetID)


def removeAbstractorInterfaceAbstractionType(abstractionTypeID: str) -> bool:
    """Remove an abstractionType from an abstractorInterface.

    Section: F.7.5.16.
    """
    return detach_child_by_handle(abstractionTypeID)


def removeAbstractorPort(portID: str) -> bool:
    """Remove a model port (any style).

    Section: F.7.5.17.
    """
    return detach_child_by_handle(portID)


def removeAbstractorView(viewID: str) -> bool:
    """Remove a model view.

    Section: F.7.5.18.
    """
    return detach_child_by_handle(viewID)


def setAbstractorAbstractorMode(abstractorID: str, modeValue: str, group: str | None = None) -> bool:
    """Set/replace the abstractorMode element.

    Section: F.7.5.19.
    """
    from org.accellera.ipxact.v1685_2022.abstractor_mode_type import AbstractorModeType
    a = _resolve(abstractorID)
    if a is None:
        raise TgiError("Invalid abstractor handle", TgiFaultCode.INVALID_ID)
    a.abstractor_mode = AbstractorType.AbstractorMode(
        value=AbstractorModeType(modeValue),
        group=group,
    )
    return True


def setAbstractorBusType(abstractorID: str, vlnv: tuple[str, str, str, str]) -> bool:
    """Set/replace the busType reference.

    Section: F.7.5.20.
    """
    a = _resolve(abstractorID)
    if a is None:
        raise TgiError("Invalid abstractor handle", TgiFaultCode.INVALID_ID)
    a.bus_type = LibraryRefType(
        vendor=vlnv[0],
        library=vlnv[1],
        name=vlnv[2],
        version=vlnv[3],
    )
    return True


# Sections F.7.5.21 & F.7.5.22 (if present in spec for additional setters/removers)
# are not defined here because they either map to vendor extensions or are
# outside current schema scope. They can be added once underlying schema objects
# are introduced.

