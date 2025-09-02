"""Configurable element category TGI functions (IEEE 1685-2022).

Implements BASE (F.7.31) and EXTENDED (F.7.32) configurable element
functions. A *configurable element* in the 2022 schema is represented by
``configurableElementValue`` entries contained inside an optional
``configurableElementValues`` element under various parent objects (e.g.
component, designConfiguration viewConfiguration, generator instances,
abstractor instances, etc.). A *configured element* (in the wording of the
standard) owns a collection of ``configurableElementValue`` children each of
which carries a required ``referenceId`` attribute referencing the ID of a
configurable (unconfigured) element plus an expression value (the textual
content inherited from ``complexBaseExpression``).

The mapping between *unconfigured* and *configured* IDs in this initial
implementation is *identity*: the same object can act as both handle kinds
because the project has not yet introduced distinct configured wrapper
objects. Consequently ``getUnconfiguredID`` currently returns the provided
handle (identity mapping). This can be revised transparently later without
changing the public API.

Only the public TGI functions explicitly listed in sections F.7.31 and F.7.32
are exported—no convenience helpers. Invalid handles raise ``TgiError`` with
``TgiFaultCode.INVALID_ID``. Semantic issues (e.g. attempting to mutate a
non-owning parent) raise ``TgiError`` with ``TgiFaultCode.INVALID_ARGUMENT``.
"""

from collections.abc import Iterable
from typing import Any

from org.accellera.ipxact.v1685_2022.configurable_element_value import ConfigurableElementValue
from org.accellera.ipxact.v1685_2022.configurable_element_values import ConfigurableElementValues

from .core import TgiError, TgiFaultCode, detach_child_by_handle, get_handle, register_parent, resolve_handle

__all__ = [
    # BASE (F.7.31)
    "getConfigurableElementIDs",
    "getConfigurableElementValue",
    "getConfigurableElementValueExpression",
    "getConfigurableElementValueIDs",
    "getConfigurableElementValueReferenceID",
    "getConfigurableElementValueValueExpression",
    "getUnconfiguredID",
    # EXTENDED (F.7.32)
    "addConfigurableElementValue",
    "addViewConfigurationConfigurableElementValue",
    "removeConfigurableElementValue",
    "setConfigurableElementValue",
    "setConfigurableElementValueReferenceID",
    "setConfigurableElementValueValue",
]

# ---------------------------------------------------------------------------
# Helpers (non-spec)
# ---------------------------------------------------------------------------

def _iter_configurable_element_values(owner: Any) -> list[ConfigurableElementValue]:
    """Return list of ``ConfigurableElementValue`` children of *owner*.

    Helper (non-spec). Accepts either a direct ``ConfigurableElementValues``
    container or any object possessing a ``configurable_element_values``
    attribute (or legacy camelCase variant) referencing the container.
    Returns an empty list when absent.
    """
    container: ConfigurableElementValues | None = None
    if isinstance(owner, ConfigurableElementValues):  # direct container
        container = owner
    else:
        container = getattr(owner, "configurable_element_values", None)
        if container is None:
            container = getattr(owner, "configurableElementValues", None)  # pragma: no cover (defensive)
    if container is None:
        return []
    try:
        items: Iterable[ConfigurableElementValue] = container.configurable_element_value  # type: ignore[attr-defined]
    except AttributeError:  # pragma: no cover
        items = getattr(container, "configurableElementValue", [])
    return [i for i in items if isinstance(i, ConfigurableElementValue)]


def _resolve_configurable_element_value(handle: str) -> ConfigurableElementValue | None:
    obj = resolve_handle(handle)
    return obj if isinstance(obj, ConfigurableElementValue) else None


def _ensure_values_container(owner: Any) -> ConfigurableElementValues:
    """Ensure the parent *owner* has a ``ConfigurableElementValues`` container.

    The container is (lazily) installed into the attribute name used by the
    schema: ``configurable_element_values``. If a camelCase name is present it
    is reused (supporting older interim code paths).
    """
    container = getattr(owner, "configurable_element_values", None)
    if container is None:
        container = getattr(owner, "configurableElementValues", None)
    if container is None:
        container = ConfigurableElementValues(configurable_element_value=[])  # type: ignore[arg-type]
        try:
            owner.configurable_element_values = container  # type: ignore[attr-defined]
        except Exception as exc:  # pragma: no cover - defensive
            raise TgiError(
                f"Owner does not support configurableElementValues: {type(owner).__name__}",
                TgiFaultCode.INVALID_ARGUMENT,
            ) from exc
    return container


# ---------------------------------------------------------------------------
# BASE (F.7.31)
# ---------------------------------------------------------------------------

def getConfigurableElementIDs(unconfiguredElementID: str) -> list[str]:
    """Return handles of all *configurable elements* for an unconfigured element.

    Section: F.7.31.1.

    The standard conceptual model distinguishes between an *unconfigured* element
    (definition) and *configurable elements* (parameters) that can be bound with
    values when configuring instances. In this implementation configurable
    elements correspond directly to ``configurableElementValue`` children;
    thus this function returns their handles (identity mapping for now).

    Args:
        unconfiguredElementID: Handle referencing an unconfigured element.

    Returns:
        list[str]: Handles of all associated configurable elements.

    Raises:
        TgiError: If the handle is invalid.
    """
    owner = resolve_handle(unconfiguredElementID)
    if owner is None:
        raise TgiError("Invalid unconfigured element handle", TgiFaultCode.INVALID_ID)
    return [get_handle(v) for v in _iter_configurable_element_values(owner)]


def getConfigurableElementValue(configurableElementID: str) -> str | None:
    """Return the default value of a configurable element.

    Section: F.7.31.2.

    Args:
        configurableElementID: Handle of the configurable element (value).

    Returns:
        str | None: Expression/value text or ``None`` if absent.

    Raises:
        TgiError: If the handle is invalid.
    """
    cev = _resolve_configurable_element_value(configurableElementID)
    if cev is None:
        raise TgiError("Invalid configurableElement handle", TgiFaultCode.INVALID_ID)
    return getattr(cev, "value", None)


def getConfigurableElementValueExpression(configurableElementID: str) -> str | None:
    """Return the default expression of a configurable element.

    Section: F.7.31.3.

    Equivalent to :func:`getConfigurableElementValue` for the current schema
    where the stored textual value doubles as the expression.
    """
    return getConfigurableElementValue(configurableElementID)


def getConfigurableElementValueIDs(configuredElementID: str) -> list[str]:
    """Return handles of all ``configurableElementValue`` children of a configured element.

    Section: F.7.31.4.

    Args:
        configuredElementID: Handle referencing a configured element.

    Returns:
        list[str]: Child handles (empty list if none).

    Raises:
        TgiError: If the handle is invalid.
    """
    owner = resolve_handle(configuredElementID)
    if owner is None:
        raise TgiError("Invalid configured element handle", TgiFaultCode.INVALID_ID)
    return [get_handle(v) for v in _iter_configurable_element_values(owner)]


def getConfigurableElementValueReferenceID(configurableElementValueID: str) -> str | None:
    """Return the ``referenceId`` attribute of a configurable element value.

    Section: F.7.31.5.

    Args:
        configurableElementValueID: Handle of the child value.

    Returns:
        str | None: Reference ID string or ``None`` if unset.

    Raises:
        TgiError: If the handle is invalid.
    """
    cev = _resolve_configurable_element_value(configurableElementValueID)
    if cev is None:
        raise TgiError("Invalid configurableElementValue handle", TgiFaultCode.INVALID_ID)
    return cev.reference_id


def getConfigurableElementValueValueExpression(configurableElementValueID: str) -> str | None:
    """Return the expression text stored in a configurable element value.

    Section: F.7.31.6.

    Args:
        configurableElementValueID: Handle of the value element.

    Returns:
        str | None: Expression string or ``None``.

    Raises:
        TgiError: If the handle is invalid.
    """
    cev = _resolve_configurable_element_value(configurableElementValueID)
    if cev is None:
        raise TgiError("Invalid configurableElementValue handle", TgiFaultCode.INVALID_ID)
    return getattr(cev, "value", None)


def getUnconfiguredID(configuredElementID: str) -> str | None:
    """Return the unconfigured element ID for the given configured element.

    Section: F.7.31.7.

    Identity mapping placeholder (see module docstring). Always returns the
    provided ID after validating it resolves.
    """
    obj = resolve_handle(configuredElementID)
    if obj is None:
        raise TgiError("Invalid configured element handle", TgiFaultCode.INVALID_ID)
    return configuredElementID


# ---------------------------------------------------------------------------
# EXTENDED (F.7.32)
# ---------------------------------------------------------------------------

def addConfigurableElementValue(configuredElementID: str, referenceID: str, expression: str) -> str:
    """Add a configurable element value under a configured element.

    Section: F.7.32.1.

    Args:
        configuredElementID: Parent handle.
        referenceID: Referenced configurable element ID.
        expression: Expression / value text.

    Returns:
        str: Handle of the newly created ``configurableElementValue``.

    Raises:
        TgiError: If the parent handle is invalid.
    """
    owner = resolve_handle(configuredElementID)
    if owner is None:
        raise TgiError("Invalid configured element handle", TgiFaultCode.INVALID_ID)
    container = _ensure_values_container(owner)
    cev = ConfigurableElementValue(reference_id=referenceID)
    cev.value = expression  # underlying base expression value
    container.configurable_element_value.append(cev)  # type: ignore[attr-defined]
    register_parent(cev, container, ("configurable_element_value",), "list")
    return get_handle(cev)


def addViewConfigurationConfigurableElementValue(viewConfigurationID: str, referenceID: str, expression: str) -> str:
    """Add a configurable element value to a ``designConfiguration.viewConfiguration.view``.

    Section: F.7.32.2.

    The *viewConfigurationID* is expected to reference a ``DesignConfiguration.ViewConfiguration``
    whose ``view`` child contains (or will contain) a ``configurableElementValues`` container.
    Only minimal structure is created; the ``view`` element itself must already exist.
    """
    vc = resolve_handle(viewConfigurationID)
    if vc is None:
        raise TgiError("Invalid viewConfiguration handle", TgiFaultCode.INVALID_ID)
    view = getattr(vc, "view", None)
    if view is None:
        raise TgiError("viewConfiguration has no 'view' element", TgiFaultCode.INVALID_ARGUMENT)
    container = _ensure_values_container(view)
    cev = ConfigurableElementValue(reference_id=referenceID)
    cev.value = expression
    container.configurable_element_value.append(cev)  # type: ignore[attr-defined]
    register_parent(cev, container, ("configurable_element_value",), "list")
    return get_handle(cev)


def removeConfigurableElementValue(configurableElementValueID: str) -> bool:
    """Remove the referenced configurable element value.

    Section: F.7.32.3.

    Args:
        configurableElementValueID: Handle of the value to remove.

    Returns:
        bool: True if removed, False if not found / wrong type.
    """
    cev = _resolve_configurable_element_value(configurableElementValueID)
    if cev is None:
        return False
    return detach_child_by_handle(configurableElementValueID)


def setConfigurableElementValue(configurableElementID: str, expression: str) -> bool:
    """Set the *default* value/expression of a configurable element.

    Section: F.7.32.4.

    Args:
        configurableElementID: Handle of the value element.
        expression: New expression text.

    Returns:
        bool: True if updated, False if not.
    """
    cev = _resolve_configurable_element_value(configurableElementID)
    if cev is None:
        return False
    cev.value = expression
    return True


def setConfigurableElementValueReferenceID(configurableElementValueID: str, referenceID: str) -> bool:
    """Set the ``referenceId`` attribute of a configurable element value.

    Section: F.7.32.5.

    Args:
        configurableElementValueID: Handle of the value element.
        referenceID: New reference ID string.

    Returns:
        bool: True if updated, False otherwise.
    """
    cev = _resolve_configurable_element_value(configurableElementValueID)
    if cev is None:
        return False
    cev.reference_id = referenceID
    return True


def setConfigurableElementValueValue(configurableElementValueID: str, expression: str) -> bool:
    """Set the expression text of a configurable element value.

    Section: F.7.32.6.

    Args:
        configurableElementValueID: Handle of the value element.
        expression: New expression/value string.

    Returns:
        bool: True if updated, False otherwise.
    """
    return setConfigurableElementValue(configurableElementValueID, expression)
