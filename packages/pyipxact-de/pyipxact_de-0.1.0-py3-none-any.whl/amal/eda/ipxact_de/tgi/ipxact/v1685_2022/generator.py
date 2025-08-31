"""Generator category TGI functions (IEEE 1685-2022).

Implements exactly the BASE (F.7.49) and EXTENDED (F.7.50) Generator
functions. These operate on generator objects (``Generator``) and the
instance generators (``AbstractorGenerator`` and ``ComponentGenerator``)
which extend ``InstanceGeneratorType``.

Error semantics follow the common TGI model:
* INVALID_ID for unknown / wrong-type handles
* INVALID_ARGUMENT for semantic misuse (e.g. applying a group add to a
  non-instance generator, enum literal mismatch, etc.).
"""
# ruff: noqa: I001
from org.accellera.ipxact.v1685_2022 import (
    Generator,
    AbstractorGenerator,
    ComponentGenerator,
)
from org.accellera.ipxact.v1685_2022.instance_generator_type import InstanceGeneratorType
from org.accellera.ipxact.v1685_2022.instance_generator_type_scope import InstanceGeneratorTypeScope
from org.accellera.ipxact.v1685_2022.generator_type import GeneratorType

from .core import (
    TgiError,
    TgiFaultCode,
    get_handle,
    resolve_handle,
    register_parent,
    detach_child_by_handle,
)

__all__ = [
    # BASE (F.7.49)
    "getAbstractorGeneratorGroup",
    "getAbstractorGeneratorGroupIDs",
    "getComponentGeneratorGroupIDs",
    "getGeneratorApiService",
    "getGeneratorApiTypeID",
    "getGeneratorExecutable",
    "getGeneratorGeneratorExe",
    "getGeneratorGroups",
    "getGeneratorPhase",
    "getGeneratorPhaseExpression",
    "getGeneratorPhaseID",
    "getGeneratorScope",
    "getGeneratorTransportMethodsID",
    "getTransportMethodsTransportMethodID",
    # EXTENDED (F.7.50)
    "addAbstractorGeneratorGroup",
    "addComponentGeneratorGroup",
    "removeAbstractorGeneratorGroup",
    "removeComponentGeneratorGroup",
    "removeGeneratorApiService",
    "removeGeneratorApiType",
    "removeGeneratorPhase",
    "removeGeneratorTransportMethods",
    "removeTransportMethodsTransportMethod",
    "setGeneratorApiService",
    "setGeneratorApiType",
    "setGeneratorGeneratorExe",
    "setGeneratorPhase",
    "setGeneratorScope",
    "setGeneratorTransportMethods",
    "setTransportMethodsTransportMethod",
]


# ---------------------------------------------------------------------------
# Helpers (non-spec)
# ---------------------------------------------------------------------------

def _resolve_generator(handle: str) -> Generator | None:
    obj = resolve_handle(handle)
    return obj if isinstance(obj, Generator) else None


def _resolve_instance_generator(handle: str) -> InstanceGeneratorType | None:
    obj = resolve_handle(handle)
    return obj if isinstance(obj, AbstractorGenerator | ComponentGenerator) else None


def _resolve_transport_methods(handle: str) -> GeneratorType.TransportMethods | None:
    obj = resolve_handle(handle)
    return obj if isinstance(obj, GeneratorType.TransportMethods) else None


# ---------------------------------------------------------------------------
# BASE (F.7.49)
# ---------------------------------------------------------------------------

def getAbstractorGeneratorGroup(abstractorGeneratorID: str) -> str | None:
    """Return the first group value of an ``AbstractorGenerator``.

    Section: F.7.49.1. If no group elements exist, returns None.
    """
    ig = _resolve_instance_generator(abstractorGeneratorID)
    if ig is None or not isinstance(resolve_handle(abstractorGeneratorID), AbstractorGenerator):
        raise TgiError("Invalid abstractorGenerator handle", TgiFaultCode.INVALID_ID)
    groups = getattr(ig, "group", [])
    for g in groups:
        return getattr(g, "value", None)
    return None


def getAbstractorGeneratorGroupIDs(abstractorGeneratorID: str) -> list[str]:
    """Return handles of all group elements of an ``AbstractorGenerator``.

    Section: F.7.49.2.
    """
    ig = _resolve_instance_generator(abstractorGeneratorID)
    if ig is None or not isinstance(resolve_handle(abstractorGeneratorID), AbstractorGenerator):
        raise TgiError("Invalid abstractorGenerator handle", TgiFaultCode.INVALID_ID)
    return [get_handle(g) for g in getattr(ig, "group", [])]


def getComponentGeneratorGroupIDs(componentGeneratorID: str) -> list[str]:
    """Return handles of group elements of a ``ComponentGenerator``.

    Section: F.7.49.3.
    """
    ig = _resolve_instance_generator(componentGeneratorID)
    if ig is None or not isinstance(resolve_handle(componentGeneratorID), ComponentGenerator):
        raise TgiError("Invalid componentGenerator handle", TgiFaultCode.INVALID_ID)
    return [get_handle(g) for g in getattr(ig, "group", [])]


def getGeneratorApiService(generatorID: str) -> str | None:
    """Return API service (SOAP/REST).

    Section: F.7.49.4.
    """
    g = _resolve_generator(generatorID)
    if g is None:
        raise TgiError("Invalid generator handle", TgiFaultCode.INVALID_ID)
    svc = g.api_service
    return None if svc is None else getattr(svc, "value", None)


def getGeneratorApiTypeID(generatorID: str) -> str | None:
    """Return handle of the ``apiType`` element (not its value).

    Section: F.7.49.5.
    """
    g = _resolve_generator(generatorID)
    if g is None:
        raise TgiError("Invalid generator handle", TgiFaultCode.INVALID_ID)
    api = g.api_type
    return None if api is None else get_handle(api)


def getGeneratorExecutable(generatorID: str) -> str | None:
    """Return the path string of ``generatorExe``.

    Section: F.7.49.6.
    """
    g = _resolve_generator(generatorID)
    if g is None:
        raise TgiError("Invalid generator handle", TgiFaultCode.INVALID_ID)
    exe = g.generator_exe
    return None if exe is None else getattr(exe, "value", None)


def getGeneratorGeneratorExe(generatorID: str) -> str | None:
    """Return the ID (handle) of the ``generatorExe`` element.

    Section: F.7.49.7. Returns None if absent.
    """
    g = _resolve_generator(generatorID)
    if g is None:
        raise TgiError("Invalid generator handle", TgiFaultCode.INVALID_ID)
    exe = g.generator_exe
    return None if exe is None else get_handle(exe)


def getGeneratorGroups(generatorID: str) -> list[str]:
    """Return list of group values (works for instance generators only).

    Section: F.7.49.8. Non-instance generators return empty list.
    """
    ig = _resolve_instance_generator(generatorID)
    if ig is None:
        # Plain generator: no groups
        return []
    return [str(getattr(g, "value", "")) for g in getattr(ig, "group", []) if getattr(g, "value", None) is not None]


def getGeneratorPhase(generatorID: str) -> str | None:
    """Return numeric/string phase value or None.

    Section: F.7.49.9.
    """
    g = _resolve_generator(generatorID)
    if g is None:
        raise TgiError("Invalid generator handle", TgiFaultCode.INVALID_ID)
    ph = g.phase
    return None if ph is None else getattr(ph, "value", None)


def getGeneratorPhaseExpression(generatorID: str) -> str | None:
    """Return expression string of phase (same as value for this schema).

    Section: F.7.49.10.
    """
    return getGeneratorPhase(generatorID)


def getGeneratorPhaseID(generatorID: str) -> str | None:
    """Return handle of ``phase`` element.

    Section: F.7.49.11.
    """
    g = _resolve_generator(generatorID)
    if g is None:
        raise TgiError("Invalid generator handle", TgiFaultCode.INVALID_ID)
    ph = g.phase
    return None if ph is None else get_handle(ph)


def getGeneratorScope(generatorID: str) -> str | None:
    """Return scope attribute (INSTANCE or DESIGN) for instance generators.

    Section: F.7.49.12. Returns None for plain Generator objects.
    """
    ig = _resolve_instance_generator(generatorID)
    if ig is None:
        return None
    scope = getattr(ig, "scope", None)
    if scope is None:
        return None
    # InstanceGeneratorTypeScope is an Enum
    try:
        return scope.value  # type: ignore[return-value]
    except AttributeError:  # pragma: no cover - defensive
        return str(scope)


def getGeneratorTransportMethodsID(generatorID: str) -> str | None:
    """Return handle of ``transportMethods`` element.

    Section: F.7.49.13.
    """
    g = _resolve_generator(generatorID)
    if g is None:
        raise TgiError("Invalid generator handle", TgiFaultCode.INVALID_ID)
    tm = g.transport_methods
    return None if tm is None else get_handle(tm)


def getTransportMethodsTransportMethodID(transportMethodsID: str) -> str | None:
    """Return handle of the ``transportMethod`` child.

    Section: F.7.49.14.
    """
    tm = _resolve_transport_methods(transportMethodsID)
    if tm is None:
        raise TgiError("Invalid transportMethods handle", TgiFaultCode.INVALID_ID)
    method = tm.transport_method
    return None if method is None else get_handle(method)


# ---------------------------------------------------------------------------
# EXTENDED (F.7.50)
# ---------------------------------------------------------------------------

def addAbstractorGeneratorGroup(abstractorGeneratorID: str, groupName: str) -> str:
    """Append a group element to an ``AbstractorGenerator``.

    Section: F.7.50.1.
    """
    ig = _resolve_instance_generator(abstractorGeneratorID)
    if ig is None or not isinstance(resolve_handle(abstractorGeneratorID), AbstractorGenerator):
        raise TgiError("Invalid abstractorGenerator handle", TgiFaultCode.INVALID_ID)
    grp = InstanceGeneratorType.Group(value=groupName)
    ig.group.append(grp)  # type: ignore[attr-defined]
    register_parent(grp, ig, ("group",), "list")
    return get_handle(grp)


def addComponentGeneratorGroup(componentGeneratorID: str, groupName: str) -> str:
    """Append a group element to a ``ComponentGenerator``.

    Section: F.7.50.2.
    """
    ig = _resolve_instance_generator(componentGeneratorID)
    if ig is None or not isinstance(resolve_handle(componentGeneratorID), ComponentGenerator):
        raise TgiError("Invalid componentGenerator handle", TgiFaultCode.INVALID_ID)
    grp = InstanceGeneratorType.Group(value=groupName)
    ig.group.append(grp)  # type: ignore[attr-defined]
    register_parent(grp, ig, ("group",), "list")
    return get_handle(grp)


def removeAbstractorGeneratorGroup(groupID: str) -> bool:
    """Remove a group element from an ``AbstractorGenerator``.

    Section: F.7.50.3.
    """
    return detach_child_by_handle(groupID)


def removeComponentGeneratorGroup(groupID: str) -> bool:
    """Remove a group element from a ``ComponentGenerator``.

    Section: F.7.50.4.
    """
    return detach_child_by_handle(groupID)


def removeGeneratorApiService(generatorID: str) -> bool:
    """Remove the ``apiService`` element.

    Section: F.7.50.5.
    """
    g = _resolve_generator(generatorID)
    if g is None:
        raise TgiError("Invalid generator handle", TgiFaultCode.INVALID_ID)
    g.api_service = None  # type: ignore[assignment]
    return True


def removeGeneratorApiType(generatorID: str) -> bool:
    """Remove the ``apiType`` element.

    Section: F.7.50.6.
    """
    g = _resolve_generator(generatorID)
    if g is None:
        raise TgiError("Invalid generator handle", TgiFaultCode.INVALID_ID)
    g.api_type = None  # type: ignore[assignment]
    return True


def removeGeneratorPhase(generatorID: str) -> bool:
    """Remove the ``phase`` element.

    Section: F.7.50.7.
    """
    g = _resolve_generator(generatorID)
    if g is None:
        raise TgiError("Invalid generator handle", TgiFaultCode.INVALID_ID)
    g.phase = None  # type: ignore[assignment]
    return True


def removeGeneratorTransportMethods(generatorID: str) -> bool:
    """Remove the ``transportMethods`` container.

    Section: F.7.50.8.
    """
    g = _resolve_generator(generatorID)
    if g is None:
        raise TgiError("Invalid generator handle", TgiFaultCode.INVALID_ID)
    g.transport_methods = None  # type: ignore[assignment]
    return True


def removeTransportMethodsTransportMethod(transportMethodsID: str) -> bool:
    """Remove the ``transportMethod`` child from a container.

    Section: F.7.50.9. Container itself remains.
    """
    tm = _resolve_transport_methods(transportMethodsID)
    if tm is None:
        raise TgiError("Invalid transportMethods handle", TgiFaultCode.INVALID_ID)
    tm.transport_method = None  # type: ignore[assignment]
    return True


def setGeneratorApiService(generatorID: str, apiService: str | None) -> bool:
    """Set or clear the ``apiService`` element.

    Section: F.7.50.10.
    """
    g = _resolve_generator(generatorID)
    if g is None:
        raise TgiError("Invalid generator handle", TgiFaultCode.INVALID_ID)
    if apiService is None:
        g.api_service = None  # type: ignore[assignment]
        return True
    from org.accellera.ipxact.v1685_2022.generator_type_api_service import GeneratorTypeApiService
    try:
        enum_val = GeneratorTypeApiService(apiService)
    except ValueError as exc:
        raise TgiError("Unknown apiService value", TgiFaultCode.INVALID_ARGUMENT) from exc
    g.api_service = enum_val  # type: ignore[assignment]
    return True


def setGeneratorApiType(generatorID: str, apiType: str | None) -> bool:
    """Set or clear the ``apiType`` element.

    Section: F.7.50.11.
    """
    g = _resolve_generator(generatorID)
    if g is None:
        raise TgiError("Invalid generator handle", TgiFaultCode.INVALID_ID)
    if apiType is None:
        g.api_type = None  # type: ignore[assignment]
        return True
    from org.accellera.ipxact.v1685_2022.api_type import ApiType
    try:
        enum_val = ApiType(apiType)
    except ValueError as exc:
        raise TgiError("Unknown apiType value", TgiFaultCode.INVALID_ARGUMENT) from exc
    g.api_type = GeneratorType.ApiType(value=enum_val)  # type: ignore[arg-type]
    return True


def setGeneratorGeneratorExe(generatorID: str, path: str) -> bool:
    """Set the path of ``generatorExe`` (creates element if absent).

    Section: F.7.50.12.
    """
    from org.accellera.ipxact.v1685_2022.ipxact_uri import IpxactUri
    g = _resolve_generator(generatorID)
    if g is None:
        raise TgiError("Invalid generator handle", TgiFaultCode.INVALID_ID)
    if g.generator_exe is None:
        g.generator_exe = IpxactUri(value=path)  # type: ignore[arg-type]
    else:
        if hasattr(g.generator_exe, "value"):
            g.generator_exe.value = path  # type: ignore[attr-defined]
        else:  # pragma: no cover
            g.generator_exe = IpxactUri(value=path)  # type: ignore[arg-type]
    return True


def setGeneratorPhase(generatorID: str, phaseValue: str) -> bool:
    """Set (or create) the ``phase`` element value.

    Section: F.7.50.13. The value is stored as the expression string.
    """
    from org.accellera.ipxact.v1685_2022.phase import Phase
    g = _resolve_generator(generatorID)
    if g is None:
        raise TgiError("Invalid generator handle", TgiFaultCode.INVALID_ID)
    g.phase = Phase(value=phaseValue)  # type: ignore[arg-type]
    return True


def setGeneratorScope(generatorID: str, scope: str) -> bool:
    """Set scope attribute of an instance generator (INSTANCE/DESIGN).

    Section: F.7.50.14.
    """
    ig = _resolve_instance_generator(generatorID)
    if ig is None:
        raise TgiError("Handle is not an instance generator", TgiFaultCode.INVALID_ID)
    try:
        ig.scope = InstanceGeneratorTypeScope(scope)  # type: ignore[assignment]
    except ValueError as exc:
        raise TgiError("Unknown scope value", TgiFaultCode.INVALID_ARGUMENT) from exc
    return True


def setGeneratorTransportMethods(generatorID: str) -> str | None:
    """Ensure a ``transportMethods`` container exists; return its handle.

    Section: F.7.50.15. Does not create a transportMethod child.
    """
    g = _resolve_generator(generatorID)
    if g is None:
        raise TgiError("Invalid generator handle", TgiFaultCode.INVALID_ID)
    if g.transport_methods is None:
        g.transport_methods = GeneratorType.TransportMethods()  # type: ignore[arg-type]
    return get_handle(g.transport_methods)


def setTransportMethodsTransportMethod(transportMethodsID: str, method: str | None) -> bool:
    """Set/clear the ``transportMethod`` child (currently only 'file').

    Section: F.7.50.16.
    """
    tm = _resolve_transport_methods(transportMethodsID)
    if tm is None:
        raise TgiError("Invalid transportMethods handle", TgiFaultCode.INVALID_ID)
    if method is None:
        tm.transport_method = None  # type: ignore[assignment]
        return True
    from org.accellera.ipxact.v1685_2022.transport_method_type import TransportMethodType
    try:
        enum_val = TransportMethodType(method)
    except ValueError as exc:
        raise TgiError("Unknown transportMethod value", TgiFaultCode.INVALID_ARGUMENT) from exc
    tm.transport_method = GeneratorType.TransportMethods.TransportMethod(value=enum_val)  # type: ignore[arg-type]
    return True
