"""Parameter category TGI functions (IEEE 1685-2022).

Implements BASE (F.7.65) and EXTENDED (F.7.66) functions for the ``parameter``
elements used widely across IP-XACT. Provides enumeration, choice & reference
helpers, value/expression accessors, and creation/removal/set operations.

Conventions:
* Getters return None/[] rather than raising for missing handles or fields.
* Set/remove operations raise ``TgiError`` with ``INVALID_ID`` for unknown
  handles, ``INVALID_ARGUMENT`` for illegal arguments.
* Expression handling mirrors simple value (model currently stores value only).
"""

from collections.abc import Iterable
from typing import Any

from org.accellera.ipxact.v1685_2022 import Parameter

from .core import (
    TgiError,
    TgiFaultCode,
    detach_child_by_handle,
    get_handle,
    register_parent,
    resolve_handle,
)

__all__ = [
    # BASE (F.7.65)
    "getModuleParameterDataTypeDefinitionRefByID",
    "getParameterChoiceRefByName",
    "getParameterIDFromReferenceID",
    "getParameterIDs",
    "getParameterNameFromReferenceID",
    "getParameterValue",
    "getParameterValueExpression",
    "getParameterValueID",
    # EXTENDED (F.7.66)
    "addParameter",
    "removeConfigGroupsAttribute",
    "removeParameter",
    "setParameterValue",
]


# ---------------------------------------------------------------------------
# Helpers (non-spec)
# ---------------------------------------------------------------------------

def _iter_parameters(container: Any) -> Iterable[Parameter]:
    if container is None:
        return []
    # Some containers embed under 'parameters'
    candidate = getattr(container, "parameters", None)
    if candidate is not None:
        container = candidate
    params = getattr(container, "parameter", None)
    if params is None:
        return []
    return [p for p in params if isinstance(p, Parameter)]


def _resolve_parameter(parameterID: str) -> Parameter | None:
    obj = resolve_handle(parameterID)
    return obj if isinstance(obj, Parameter) else None


def _find_parameter_by_name(container: Any, name: str) -> Parameter | None:
    for p in _iter_parameters(container):
        if getattr(p, "name", None) == name:
            return p
    return None


def _resolve_container(containerID: str) -> Any | None:
    return resolve_handle(containerID)


# ---------------------------------------------------------------------------
# BASE (F.7.65)
# ---------------------------------------------------------------------------

def getModuleParameterDataTypeDefinitionRefByID(parameterID: str) -> str | None:  # F.7.65.1
    """Return the data type definition reference ID (handle) if present.

    Section: F.7.65.1. Current model: return None (placeholder) pending full
    type definitions integration.
    """
    # Without schema binding for datatype definition, return None.
    return None


def getParameterChoiceRefByName(parameterContainerElementID: str, parameterName: str) -> str | None:  # F.7.65.2
    """Return handle of the ``choice`` referenced by parameter name.

    Section: F.7.65.2. Placeholder returns None until choices are attached to
    parameters in the model.
    """
    _ = (parameterContainerElementID, parameterName)
    return None


def getParameterIDFromReferenceID(
    parameterContainerElementID: str, referenceParameterID: str
) -> str | None:  # F.7.65.3
    """Map a reference parameter ID to the actual parameter ID (identity).

    Section: F.7.65.3. With no separate reference indirection layer yet,
    returns the input if it resolves to a Parameter.
    """
    obj = _resolve_parameter(referenceParameterID)
    return referenceParameterID if obj is not None else None


def getParameterIDs(parameterContainerElementID: str) -> list[str]:  # F.7.65.4
    """Return handles of all ``parameter`` elements under the container.

    Section: F.7.65.4.
    """
    container = _resolve_container(parameterContainerElementID)
    if container is None:
        return []
    return [get_handle(p) for p in _iter_parameters(container)]


def getParameterNameFromReferenceID(
    parameterContainerElementID: str, referenceParameterID: str
) -> str | None:  # F.7.65.5
    """Return parameter name given a (possibly reference) parameter ID.

    Section: F.7.65.5.
    """
    _ = parameterContainerElementID  # container unused with identity mapping
    p = _resolve_parameter(referenceParameterID)
    return getattr(p, "name", None) if p is not None else None


def getParameterValue(parameterID: str) -> str | None:  # F.7.65.6
    """Return parameter value simple text.

    Section: F.7.65.6.
    """
    p = _resolve_parameter(parameterID)
    if p is None or p.value is None:
        return None
    return getattr(p.value, "value", None)


def getParameterValueExpression(parameterID: str) -> str | None:  # F.7.65.7
    """Return expression for parameter value (mirrors value currently).

    Section: F.7.65.7.
    """
    return getParameterValue(parameterID)


def getParameterValueID(parameterID: str) -> str | None:  # F.7.65.8
    """Return handle to the value element (parameter itself here).

    Section: F.7.65.8.
    """
    p = _resolve_parameter(parameterID)
    return parameterID if p is not None else None


# ---------------------------------------------------------------------------
# EXTENDED (F.7.66)
# ---------------------------------------------------------------------------

def addParameter(parameterContainerElementID: str, name: str, value: str | None = None) -> str:  # F.7.66.1
    """Create a new ``parameter`` and append to container.

    Section: F.7.66.1.
    Args:
        parameterContainerElementID: Handle of container with parameter list.
        name: Parameter name (must be unique within container).
        value: Optional initial value string.
    Raises:
        TgiError: On invalid container handle or duplicate name.
    """
    container = _resolve_container(parameterContainerElementID)
    if container is None:
        raise TgiError("Invalid parameter container handle", TgiFaultCode.INVALID_ID)
    if _find_parameter_by_name(container, name) is not None:
        raise TgiError("Parameter name already exists", TgiFaultCode.ALREADY_EXISTS)
    from org.accellera.ipxact.v1685_2022 import Value  # local import
    p = Parameter(name=name)
    if value is not None:
        p.value = Value(value=value)  # type: ignore[assignment]
    # attach
    params_holder = getattr(container, "parameters", None)
    holder = params_holder if params_holder is not None else container
    lst = getattr(holder, "parameter", None)
    if lst is None:
        holder.parameter = []  # type: ignore[attr-defined]
        lst = holder.parameter  # type: ignore[attr-defined]
    lst.append(p)
    register_parent(p, holder, ("parameter",), "list")
    return get_handle(p)


def removeConfigGroupsAttribute(parameterID: str) -> bool:  # F.7.66.2
    """Remove configGroups attribute from parameter (placeholder).

    Section: F.7.66.2. Current model: if attribute exists set to None.
    Returns True if removed, False if not present or parameter invalid.
    """
    p = _resolve_parameter(parameterID)
    if p is None:
        return False
    if getattr(p, "config_groups", None) is None and getattr(p, "configGroups", None) is None:
        return False
    if hasattr(p, "config_groups"):
        p.config_groups = None  # type: ignore[assignment]
    if hasattr(p, "configGroups"):
        p.configGroups = None  # type: ignore[assignment]
    return True


def removeParameter(parameterID: str) -> bool:  # F.7.66.3
    """Remove a parameter by handle.

    Section: F.7.66.3. Uses parent registry for structural detach.
    """
    return detach_child_by_handle(parameterID)


def setParameterValue(parameterID: str, newValue: str | None) -> bool:  # F.7.66.4
    """Set (or clear if None) parameter value.

    Section: F.7.66.4.
    """
    p = _resolve_parameter(parameterID)
    if p is None:
        raise TgiError("Invalid parameter handle", TgiFaultCode.INVALID_ID)
    if newValue is None:
        p.value = None  # type: ignore[assignment]
        return True
    from org.accellera.ipxact.v1685_2022 import Value
    if p.value is None:
        p.value = Value(value=newValue)  # type: ignore[assignment]
    else:
        p.value.value = newValue
    return True
