"""Module parameter category TGI functions (IEEE 1685-2022).

Implements BASE (F.7.61) and EXTENDED (F.7.62) functions for accessing and
modifying ``moduleParameter`` elements under a ``componentInstantiation`` or
any container exposing a ``module_parameter`` list. This mirrors the style and
error semantics of other category modules (e.g. abstraction_definition).

Rules applied:
* Get functions never raise for missing elements; they return ``None`` or an
  empty list.
* Traversal enumerations return handles (opaque IDs) for contained module
  parameters.
* Extended add/remove/set operations raise ``TgiError`` with
  ``TgiFaultCode.INVALID_ID`` for unknown handles and ``TgiFaultCode.INVALID_ARGUMENT``
  for invalid arguments; otherwise return ``True``/new handle.
* Expressions are not distinguished from values in the current simplified in-
  memory model, so the expression getter mirrors value retrieval.
"""

# ruff: noqa: I001
from collections.abc import Iterable
from typing import Any

from org.accellera.ipxact.v1685_2022 import (
    ComponentInstantiationType,
    ModuleParameterType,
)

from .core import (
    TgiError,
    TgiFaultCode,
    get_handle,
    resolve_handle,
    register_parent,
    detach_child_by_handle,
)

__all__ = [
    # BASE (F.7.61)
    "getModuleParameterIDs",
    "getModuleParameterValue",
    "getModuleParameterValueExpression",
    # EXTENDED (F.7.62)
    "addModuleParameter",
    "removeModuleParameter",
    "setModuleParameterValue",
]


# ---------------------------------------------------------------------------
# Helpers (non-spec)
# ---------------------------------------------------------------------------

def _iter_module_parameters(owner: Any) -> Iterable[ModuleParameterType]:
    """Yield ``ModuleParameterType`` children for a container.

    Accepts a ``ComponentInstantiationType`` or an object with a
    ``module_parameter`` list.
    """
    if owner is None:
        return []
    if isinstance(owner, ComponentInstantiationType):
        owner = owner.module_parameters  # type: ignore[assignment]
    if owner is None:
        return []
    params = getattr(owner, "module_parameter", None)
    if params is None:
        return []
    return [p for p in params if isinstance(p, ModuleParameterType)]


def _resolve_param(paramID: str) -> ModuleParameterType | None:
    obj = resolve_handle(paramID)
    return obj if isinstance(obj, ModuleParameterType) else None


def _resolve_container(containerID: str) -> Any | None:
    return resolve_handle(containerID)


# ---------------------------------------------------------------------------
# BASE (F.7.61)
# ---------------------------------------------------------------------------

def getModuleParameterIDs(moduleParameterContainerElementID: str) -> list[str]:  # F.7.61.1
    """Return handles of all ``moduleParameter`` elements in the container.

    Section: F.7.61.1.
    """
    obj = _resolve_container(moduleParameterContainerElementID)
    if obj is None:
        return []
    return [get_handle(p) for p in _iter_module_parameters(obj)]


def getModuleParameterValue(moduleParameterID: str) -> str | None:  # F.7.61.2
    """Return the parameter value simple string (None if absent).

    Section: F.7.61.2.
    """
    p = _resolve_param(moduleParameterID)
    if p is None or p.value is None:
        return None
    return getattr(p.value, "value", None)


def getModuleParameterValueExpression(moduleParameterID: str) -> str | None:  # F.7.61.3
    """Return the value expression (mirrors value in this model).

    Section: F.7.61.3.
    """
    return getModuleParameterValue(moduleParameterID)


# ---------------------------------------------------------------------------
# EXTENDED (F.7.62)
# ---------------------------------------------------------------------------

def addModuleParameter(moduleParameterContainerElementID: str, name: str, value: str | None = None) -> str:  # F.7.62.1
    """Add a new ``moduleParameter`` below the container, returning its handle.

    Section: F.7.62.1.
    Args:
        moduleParameterContainerElementID: Handle to container (componentInstantiation
            or object with ``module_parameter`` list attribute).
        name: Parameter name.
        value: Optional initial value string.
    """
    container = _resolve_container(moduleParameterContainerElementID)
    if container is None:
        raise TgiError("Invalid module parameter container handle", TgiFaultCode.INVALID_ID)
    from org.accellera.ipxact.v1685_2022 import Value  # local import to avoid cycles
    mp = ModuleParameterType(name=name)
    if value is not None:
        mp.value = Value(value=value)  # type: ignore[assignment]
    # Determine list owner
    if isinstance(container, ComponentInstantiationType):
        if container.module_parameters is None:
            # Create a lightweight holder with a module_parameter list
            class _ModuleParameters:  # local anonymous structure
                def __init__(self) -> None:
                    self.module_parameter: list[ModuleParameterType] = []

            container.module_parameters = _ModuleParameters()  # type: ignore[assignment]
        owner = container.module_parameters
    else:
        owner = container
    lst = getattr(owner, "module_parameter", None)
    if lst is None:
        # create list attribute if missing (development convenience)
        owner.module_parameter = []  # type: ignore[attr-defined]
        lst = owner.module_parameter  # type: ignore[attr-defined]
    if isinstance(lst, list):
        lst.append(mp)
    register_parent(mp, owner, ("module_parameter",), "list")
    return get_handle(mp)


def removeModuleParameter(moduleParameterID: str) -> bool:  # F.7.62.2
    """Remove a ``moduleParameter`` by handle.

    Section: F.7.62.2.
    """
    # Attempt structured detach first
    return detach_child_by_handle(moduleParameterID)


def setModuleParameterValue(moduleParameterID: str, newValue: str) -> bool:  # F.7.62.3
    """Set parameter value, creating value element if needed.

    Section: F.7.62.3.
    """
    p = _resolve_param(moduleParameterID)
    if p is None:
        raise TgiError("Invalid moduleParameter handle", TgiFaultCode.INVALID_ID)
    if newValue is None:
        raise TgiError("newValue cannot be None", TgiFaultCode.INVALID_ARGUMENT)
    from org.accellera.ipxact.v1685_2022 import Value  # local import
    if p.value is None:
        p.value = Value(value=newValue)  # type: ignore[assignment]
    else:
        p.value.value = newValue
    return True
