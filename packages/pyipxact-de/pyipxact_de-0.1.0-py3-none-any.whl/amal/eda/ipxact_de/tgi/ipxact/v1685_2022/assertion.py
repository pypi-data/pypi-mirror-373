"""Assertion category TGI functions (IEEE 1685-2022).

Implements BASE (F.7.15) and EXTENDED (F.7.16) Assertion functions.

Assertions appear inside several schema elements (component, abstraction
definition, bus definition, design, design configuration, abstractor, type
definitions, generator chain). Each such container MAY include an
``assertions`` element containing one or more ``assertion`` child elements.

The BASE API provides enumeration and value/expression retrieval. The
EXTENDED API allows adding, removing and setting textual metadata and the
assert expression itself. Where the underlying schema does not model a
feature mentioned in the spec (e.g. a dedicated failure message separate
from description), a setter will either map to the closest schema field or
raise ``TgiError`` with ``TgiFaultCode.UNSUPPORTED_OPERATION``.

All getters return ``None`` when the requested value is absent. Mutators
create intermediate containers on demand (e.g. the ``assertions`` wrapper)
consistent with other category implementations.
"""

from collections.abc import Iterable
from typing import Any

from org.accellera.ipxact.v1685_2022 import Assertion
from org.accellera.ipxact.v1685_2022.description import Description
from org.accellera.ipxact.v1685_2022.display_name import DisplayName
from org.accellera.ipxact.v1685_2022.short_description import ShortDescription
from org.accellera.ipxact.v1685_2022.unsigned_bit_expression import UnsignedBitExpression

# ruff: noqa: I001 (import ordering intentionally mirrors sibling modules)

from .core import (
    TgiError,
    TgiFaultCode,
    get_handle,
    resolve_handle,
    register_parent,
    detach_child_by_handle,
)

__all__: list[str] = [
    # BASE (F.7.15)
    "getAssertionIDs",
    "getAssertionName",
    "getAssertionDisplayName",
    "getAssertionShortDescription",
    "getAssertionDescription",
    "getAssertionExpression",
    "getAssertionExpressionID",
    # EXTENDED (F.7.16)
    "addAssertion",
    "removeAssertion",
    "setAssertionName",
    "setAssertionDisplayName",
    "setAssertionShortDescription",
    "setAssertionDescription",
    "setAssertionExpression",
]


# ---------------------------------------------------------------------------
# Helpers (non-spec)
# ---------------------------------------------------------------------------

def _iter(value: Any) -> Iterable[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    try:  # pragma: no cover
        return list(value)
    except Exception:  # pragma: no cover
        return []


def _resolve_assertion(assertionID: str) -> Assertion:
    obj = resolve_handle(assertionID)
    if not isinstance(obj, Assertion):
        raise TgiError("Invalid assertion handle", TgiFaultCode.INVALID_ID)
    return obj


def _text_value(obj: Any, field: str) -> str | None:
    if obj is None:
        return None
    f = getattr(obj, field, None)
    if f is None:
        return None
    return getattr(f, "value", f) if not isinstance(f, str) else f


# ---------------------------------------------------------------------------
# BASE (F.7.15)
# ---------------------------------------------------------------------------

def getAssertionIDs(parentID: str) -> list[str]:  # F.7.15.1
    """Return handles of ``assertion`` children under a parent.

    Section: F.7.15.1.

    Args:
        parentID: Handle referencing any object which MAY own an
            ``assertions`` container.

    Returns:
        list[str]: Handles (possibly empty) of assertion elements.

    Raises:
        TgiError: If the parent handle is invalid.
    """
    parent = resolve_handle(parentID)
    if parent is None:
        raise TgiError("Invalid parent handle", TgiFaultCode.INVALID_ID)
    container = getattr(parent, "assertions", None)
    if container is None:
        return []
    items = getattr(container, "assertion", [])
    result: list[str] = []
    for a in _iter(items):
        if isinstance(a, Assertion):
            result.append(get_handle(a))
    return result


def getAssertionName(assertionID: str) -> str | None:  # F.7.15.2
    """Return the assertion ``name``.

    Section: F.7.15.2.
    """
    a = _resolve_assertion(assertionID)
    return getattr(a, "name", None)


def getAssertionDisplayName(assertionID: str) -> str | None:  # F.7.15.3
    """Return ``displayName`` value.

    Section: F.7.15.3.
    """
    return _text_value(_resolve_assertion(assertionID), "display_name")


def getAssertionShortDescription(assertionID: str) -> str | None:  # F.7.15.4
    """Return ``shortDescription`` value.

    Section: F.7.15.4.
    """
    return _text_value(_resolve_assertion(assertionID), "short_description")


def getAssertionDescription(assertionID: str) -> str | None:  # F.7.15.5
    """Return ``description`` value.

    Section: F.7.15.5.
    """
    return _text_value(_resolve_assertion(assertionID), "description")


def getAssertionExpression(assertionID: str) -> str | None:  # F.7.15.6
    """Return the assert expression string value.

    Section: F.7.15.6. Maps to ``assert_value.value`` in the schema.
    """
    a = _resolve_assertion(assertionID)
    expr = getattr(a, "assert_value", None)
    return getattr(expr, "value", None) if expr is not None else None


def getAssertionExpressionID(assertionID: str) -> str | None:  # F.7.15.7
    """Return handle of the underlying expression object.

    Section: F.7.15.7.
    """
    a = _resolve_assertion(assertionID)
    expr = getattr(a, "assert_value", None)
    return get_handle(expr) if expr is not None else None


# ---------------------------------------------------------------------------
# EXTENDED (F.7.16)
# ---------------------------------------------------------------------------

def addAssertion(parentID: str, name: str, expression: str) -> str:  # F.7.16.1
    """Create and append a new ``assertion`` element.

    Section: F.7.16.1.

    The parent must support an ``assertions.assertion`` list. The container
    will be created if absent.

    Args:
        parentID: Parent element handle.
        name: Assertion name.
        expression: Expression string for the assert condition.

    Returns:
        str: Handle of created assertion.

    Raises:
        TgiError: If parent handle invalid.
    """
    parent = resolve_handle(parentID)
    if parent is None:
        raise TgiError("Invalid parent handle", TgiFaultCode.INVALID_ID)
    # Create container dynamically if necessary (duck-typed to have 'assertion' list)
    if getattr(parent, "assertions", None) is None:
        class AssertionsContainer:  # minimal dynamic wrapper
            def __init__(self):
                self.assertion: list[Assertion] = []

        parent.assertions = AssertionsContainer()  # type: ignore[attr-defined]
    a = Assertion()
    a.name = name
    a.assert_value = UnsignedBitExpression(value=expression)
    parent.assertions.assertion.append(a)  # type: ignore[attr-defined]
    register_parent(a, parent, ("assertions",), "list")
    return get_handle(a)


def removeAssertion(assertionID: str) -> bool:  # F.7.16.2
    """Remove an ``assertion`` element.

    Section: F.7.16.2.

    Args:
        assertionID: Assertion handle.

    Returns:
        bool: True if removed else False.
    """
    return detach_child_by_handle(assertionID)


def setAssertionName(assertionID: str, name: str) -> bool:  # F.7.16.3
    """Set assertion ``name``.

    Section: F.7.16.3.
    """
    a = _resolve_assertion(assertionID)
    a.name = name
    return True


def setAssertionDisplayName(assertionID: str, value: str) -> bool:  # F.7.16.4
    """Set or create ``displayName``.

    Section: F.7.16.4.
    """
    a = _resolve_assertion(assertionID)
    a.display_name = DisplayName(value=value)
    return True


def setAssertionShortDescription(assertionID: str, value: str) -> bool:  # F.7.16.5
    """Set or create ``shortDescription``.

    Section: F.7.16.5.
    """
    a = _resolve_assertion(assertionID)
    a.short_description = ShortDescription(value=value)
    return True


def setAssertionDescription(assertionID: str, value: str) -> bool:  # F.7.16.6
    """Set or create ``description``.

    Section: F.7.16.6.
    """
    a = _resolve_assertion(assertionID)
    a.description = Description(value=value)
    return True


def setAssertionExpression(assertionID: str, expression: str) -> bool:  # F.7.16.7
    """Set the assert expression string.

    Section: F.7.16.7. Creates the expression container if absent.
    """
    a = _resolve_assertion(assertionID)
    a.assert_value = UnsignedBitExpression(value=expression)
    return True

