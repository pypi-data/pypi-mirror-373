"""Name group category TGI functions (IEEE 1685-2022).

Implements BASE (F.7.63) and EXTENDED (F.7.64) functions operating on the
standard IP-XACT NameGroup (``name``, ``displayName``, ``description``,
``shortDescription``) which is reused across many schema elements. Handles
refer to any object possessing the corresponding attributes.

Design decisions:
* Getters never raise for missing handles; they return ``None``.
* Set/remove calls raise ``TgiError`` with ``INVALID_ID`` for unknown handles.
* Removal sets the attribute to ``None`` and returns True if the element
  existed before removal else False.
* Setting creates/overwrites simple string content; empty string is allowed.
"""

from typing import Any

from .core import TgiError, TgiFaultCode, resolve_handle

__all__ = [
    # BASE (F.7.63)
    "getDescription",
    "getDisplayName",
    "getName",
    "getShortDescription",
    # EXTENDED (F.7.64)
    "removeDescription",
    "removeDisplayName",
    "removeName",
    "removeShortDescription",
    "setDescription",
    "setDisplayName",
    "setName",
    "setShortDescription",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _resolve(objID: str) -> Any | None:  # non-spec helper
    return resolve_handle(objID)


def _get_text(obj: Any, attr: str) -> str | None:
    if obj is None:
        return None
    val = getattr(obj, attr, None)
    if val is None:
        return None
    # Some generated classes wrap text in a Value-type with 'value'
    inner = getattr(val, "value", None)
    return inner if inner is not None else val


def _set_text(obj: Any, attr: str, value: str | None) -> bool:
    if obj is None:
        raise TgiError("Invalid handle", TgiFaultCode.INVALID_ID)
    if value is None:
        setattr(obj, attr, None)
        return True
    # If attribute already present and has 'value', set nested value
    existing = getattr(obj, attr, None)
    if existing is not None and hasattr(existing, "value"):
        existing.value = value  # type: ignore[assignment]
    else:
        setattr(obj, attr, value)
    return True


def _remove_attr(obj: Any, attr: str) -> bool:
    if obj is None:
        raise TgiError("Invalid handle", TgiFaultCode.INVALID_ID)
    if getattr(obj, attr, None) is None:
        return False
    setattr(obj, attr, None)
    return True


# ---------------------------------------------------------------------------
# BASE (F.7.63)
# ---------------------------------------------------------------------------

def getDescription(elementID: str) -> str | None:  # F.7.63.1
    """Return description text.

    Section: F.7.63.1.
    """
    return _get_text(_resolve(elementID), "description")


def getDisplayName(elementID: str) -> str | None:  # F.7.63.2
    """Return displayName text.

    Section: F.7.63.2.
    """
    return _get_text(_resolve(elementID), "display_name") or _get_text(_resolve(elementID), "displayName")


def getName(elementID: str) -> str | None:  # F.7.63.3
    """Return name text.

    Section: F.7.63.3.
    """
    return _get_text(_resolve(elementID), "name")


def getShortDescription(elementID: str) -> str | None:  # F.7.63.4
    """Return shortDescription text.

    Section: F.7.63.4.
    """
    return _get_text(_resolve(elementID), "short_description") or _get_text(_resolve(elementID), "shortDescription")


# ---------------------------------------------------------------------------
# EXTENDED (F.7.64)
# ---------------------------------------------------------------------------

def removeDescription(elementID: str) -> bool:  # F.7.64.1
    """Remove description element.

    Section: F.7.64.1.
    """
    return _remove_attr(_resolve(elementID), "description")


def removeDisplayName(elementID: str) -> bool:  # F.7.64.2
    """Remove displayName element.

    Section: F.7.64.2.
    """
    obj = _resolve(elementID)
    # handle both naming variants
    if getattr(obj, "display_name", None) is not None:
        return _remove_attr(obj, "display_name")
    return _remove_attr(obj, "displayName")


def removeName(elementID: str) -> bool:  # F.7.64.3
    """Remove name element.

    Section: F.7.64.3.
    """
    return _remove_attr(_resolve(elementID), "name")


def removeShortDescription(elementID: str) -> bool:  # F.7.64.4
    """Remove shortDescription element.

    Section: F.7.64.4.
    """
    obj = _resolve(elementID)
    if getattr(obj, "short_description", None) is not None:
        return _remove_attr(obj, "short_description")
    return _remove_attr(obj, "shortDescription")


def setDescription(elementID: str, value: str | None) -> bool:  # F.7.64.5
    """Set description text (None clears).

    Section: F.7.64.5.
    """
    return _set_text(_resolve(elementID), "description", value)


def setDisplayName(elementID: str, value: str | None) -> bool:  # F.7.64.6
    """Set displayName text (None clears). Handles both naming variants.

    Section: F.7.64.6.
    """
    obj = _resolve(elementID)
    # prefer existing attribute variant if present
    if hasattr(obj, "display_name") or not hasattr(obj, "displayName"):
        return _set_text(obj, "display_name", value)
    return _set_text(obj, "displayName", value)


def setName(elementID: str, value: str | None) -> bool:  # F.7.64.7
    """Set name text (None clears).

    Section: F.7.64.7.
    """
    return _set_text(_resolve(elementID), "name", value)


def setShortDescription(elementID: str, value: str | None) -> bool:  # F.7.64.8
    """Set shortDescription text (None clears). Supports both variants.

    Section: F.7.64.8.
    """
    obj = _resolve(elementID)
    if hasattr(obj, "short_description") or not hasattr(obj, "shortDescription"):
        return _set_text(obj, "short_description", value)
    return _set_text(obj, "shortDescription", value)

