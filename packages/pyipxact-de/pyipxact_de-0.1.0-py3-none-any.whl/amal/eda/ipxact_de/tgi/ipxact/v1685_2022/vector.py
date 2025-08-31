"""Vector category TGI functions (IEEE 1685-2022).

Implements BASE (F.7.83) and EXTENDED (F.7.84) vector functions. A *vector*
is any element with left/right sub-elements representing integer or
expression endpoints. The spec defines an API that allows traversal of
vector endpoints and mutation (setting / removing ends) in EXTENDED mode.

Design notes:
* BASE getters are tolerant: invalid handles yield neutral values (``None``
  or empty list) rather than faults, consistent with other category modules.
* EXTENDED functions raise :class:`TgiError` with
  ``TgiFaultCode.INVALID_ID`` for unknown handles and
  ``TgiFaultCode.INVALID_ARGUMENT`` for semantic issues.
* Some schema objects embed a nested object (e.g. ``vector``) containing
  ``left`` and ``right``; we transparently descend if necessary.
"""
from types import SimpleNamespace  # ruff: noqa: I001
from typing import Any

from .core import TgiError, TgiFaultCode, get_handle, resolve_handle

__all__ = [
    # BASE (F.7.83)
    "getVectorIDs",
    "getVectorIdAttribute",
    "getVectorLeftID",
    "getVectorRange",
    "getVectorRangeExpression",
    "getVectorRightID",
    # EXTENDED (F.7.84)
    "removeVectorLeft",
    "removeVectorRight",
    "setVector",
    "setVectorIdAttribute",
    "setVectorLeft",
    "setVectorRight",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _resolve(objID: str):
    return resolve_handle(objID)


def _resolve_vector(vectorID: str) -> Any | None:
    obj = _resolve(vectorID)
    if obj is None:
        return None
    # Allow direct left/right
    if hasattr(obj, "left") and hasattr(obj, "right"):
        return obj
    # Allow nested attribute named 'vector'
    inner = getattr(obj, "vector", None)
    if inner is not None and hasattr(inner, "left") and hasattr(inner, "right"):
        return inner
    return None


def _ensure_vector(vectorID: str):
    vec = _resolve_vector(vectorID)
    if vec is None:
        raise TgiError("Invalid ID", TgiFaultCode.INVALID_ID)
    return vec


def _make_endpoint(value: str | int | None, expression: str | None = None):
    if value is None and expression is None:
        return None
    # Represent endpoint with structure having .value (and optional .expression)
    ns = SimpleNamespace(value=value)
    if expression is not None:
        ns.expression = expression  # type: ignore[attr-defined]
    return ns


def _get_endpoint_value(ep) -> int | None:
    if ep is None:
        return None
    val = getattr(ep, "value", None)
    return val if isinstance(val, int) else None


def _get_endpoint_expr(ep) -> str | None:
    if ep is None:
        return None
    return getattr(ep, "expression", None)


# ---------------------------------------------------------------------------
# BASE (F.7.83)
# ---------------------------------------------------------------------------

def getVectorIDs(vectorContainerID: str) -> list[str]:  # F.7.83.1
    container = _resolve(vectorContainerID)
    if container is None:
        return []
    # Accept patterns: direct list attribute 'vector', or left/right pair considered singular vector
    ids: list[str] = []
    vectors = []
    if hasattr(container, "vector") and isinstance(container.vector, list):  # type: ignore[attr-defined]
        vectors = container.vector  # type: ignore[attr-defined]
    elif hasattr(container, "left") and hasattr(container, "right"):
        return [get_handle(container)]
    for v in vectors:
        if hasattr(v, "left") and hasattr(v, "right"):
            ids.append(get_handle(v))
    return ids


def getVectorIdAttribute(elementID: str) -> str | None:  # F.7.83.2
    obj = _resolve(elementID)
    if obj is None:
        return None
    return getattr(obj, "vector_id", None)  # optional attribute


def getVectorLeftID(vectorID: str) -> str | None:  # F.7.83.3
    vec = _resolve_vector(vectorID)
    if vec is None:
        return None
    left = getattr(vec, "left", None)
    return get_handle(left) if left is not None else None


def getVectorRange(vectorID: str) -> list[int | None] | None:  # F.7.83.4
    vec = _resolve_vector(vectorID)
    if vec is None:
        return None
    left = getattr(vec, "left", None)
    right = getattr(vec, "right", None)
    return [_get_endpoint_value(left), _get_endpoint_value(right)]


def getVectorRangeExpression(vectorID: str) -> list[str | None] | None:  # F.7.83.5
    vec = _resolve_vector(vectorID)
    if vec is None:
        return None
    left = getattr(vec, "left", None)
    right = getattr(vec, "right", None)
    return [_get_endpoint_expr(left), _get_endpoint_expr(right)]


def getVectorRightID(vectorID: str) -> str | None:  # F.7.83.6
    vec = _resolve_vector(vectorID)
    if vec is None:
        return None
    right = getattr(vec, "right", None)
    return get_handle(right) if right is not None else None


# ---------------------------------------------------------------------------
# EXTENDED (F.7.84)
# ---------------------------------------------------------------------------

def removeVectorLeft(vectorID: str) -> bool:  # F.7.84.1
    vec = _ensure_vector(vectorID)
    if getattr(vec, "left", None) is None:
        return True
    vec.left = None  # type: ignore[attr-defined]
    return True


def removeVectorRight(vectorID: str) -> bool:  # F.7.84.2
    vec = _ensure_vector(vectorID)
    if getattr(vec, "right", None) is None:
        return True
    vec.right = None  # type: ignore[attr-defined]
    return True


def setVector(vectorID: str, left: str | int | None, right: str | int | None) -> bool:  # F.7.84.3
    vec = _ensure_vector(vectorID)
    vec.left = _make_endpoint(left)  # type: ignore[attr-defined]
    vec.right = _make_endpoint(right)  # type: ignore[attr-defined]
    return True


def setVectorIdAttribute(elementID: str, vectorId: str | None) -> bool:  # F.7.84.4
    obj = _resolve(elementID)
    if obj is None:
        raise TgiError("Invalid ID", TgiFaultCode.INVALID_ID)
    if vectorId is None:
        if hasattr(obj, "vector_id"):
            delattr(obj, "vector_id")
    else:
        obj.vector_id = vectorId  # type: ignore[attr-defined]
    return True


def setVectorLeft(vectorID: str, left: str | int | None) -> bool:  # F.7.84.5
    vec = _ensure_vector(vectorID)
    vec.left = _make_endpoint(left)  # type: ignore[attr-defined]
    return True


def setVectorRight(vectorID: str, right: str | int | None) -> bool:  # F.7.84.6
    vec = _ensure_vector(vectorID)
    vec.right = _make_endpoint(right)  # type: ignore[attr-defined]
    return True

