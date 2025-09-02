"""Array category TGI functions (IEEE 1685-2022).

Implements BASE (F.7.13) and EXTENDED (F.7.14) Array functions. The schema
represents arrayable constructs (e.g. register arrays, field arrays, generic
``array`` helper types) with a container having:

* ``dim``: list of dimension elements (each with ``value`` expression and
  optional ``indexVar`` attribute in EXTENDED mode)
* Optional left/right bound elements (``left``, ``right``) for some array
  forms
* Optional ``range`` element (unsigned expression)
* Optional stride element named either ``stride`` (generic), ``bit_stride`` or
  ``bitStride`` depending on the generated dataclass; we normalise access via
  *stride* accessors.

Not all array forms carry every sub-element; getters return ``None`` when a
sub-element is absent. Numeric getters attempt integer conversion of the
underlying ``value`` field, otherwise return ``None``.
"""

from typing import Any

from .core import (
    TgiError,
    TgiFaultCode,
    detach_child_by_handle,
    get_handle,
    register_parent,
    resolve_handle,
)

__all__ = [
    # BASE (F.7.13)
    "getArrayDimIDs",
    "getArrayIDs",
    "getArrayLeftID",
    "getArrayRange",
    "getArrayRangeExpression",
    "getArrayRightID",
    "getArrayStride",
    "getArrayStrideExpression",
    "getArrayStrideID",
    "getDimExpression",
    "getDimIndexVar",
    "getDimValue",
    "getRegisterArrayID",
    "getRegisterFieldArrayID",
    # EXTENDED (F.7.14)
    "addArray",
    "addArrayDim",
    "removeArray",
    "removeArrayDim",
    "removeArrayStride",
    "removeIndexVarAttribute",
    "setArrayStride",
    "setDimIndexVar",
]


# ---------------------------------------------------------------------------
# Helpers (non-spec)
# ---------------------------------------------------------------------------

def _resolve_array(arrayID: str) -> Any:
    """Resolve an array-like container by handle.

    Helper (non-spec). An object is considered array-like if it has a ``dim``
    attribute (list). This function validates the handle and type.

    Args:
        arrayID: Handle referencing a potential array container.

    Returns:
        Any: The resolved object.

    Raises:
        TgiError: If the handle is invalid or object lacks a ``dim`` attribute.
    """
    obj = resolve_handle(arrayID)
    if obj is None or not hasattr(obj, "dim"):
        raise TgiError("Invalid array handle", TgiFaultCode.INVALID_ID)
    return obj


def _resolve_dim(dimID: str) -> Any:
    """Resolve a dimension element by handle.

    Args:
        dimID: Handle referencing a ``dim`` element.

    Returns:
        Any: Dimension object.

    Raises:
        TgiError: If the handle is invalid or the object lacks ``value``.
    """
    obj = resolve_handle(dimID)
    if obj is None or not hasattr(obj, "value"):
        raise TgiError("Invalid dim handle", TgiFaultCode.INVALID_ID)
    return obj


def _get_attr(obj: Any, *names: str) -> Any:
    """Return first existing attribute among names (or None)."""
    for n in names:
        if hasattr(obj, n):
            return getattr(obj, n)
    return None


def _int_value(expr_obj: Any) -> int | None:
    """Attempt to convert expression object's ``value`` to int."""
    if expr_obj is None:
        return None
    try:
        return int(getattr(expr_obj, "value", None))  # type: ignore[arg-type]
    except Exception:  # pragma: no cover
        return None


# ---------------------------------------------------------------------------
# BASE (F.7.13)
# ---------------------------------------------------------------------------

def getArrayDimIDs(arrayID: str) -> list[str]:
    """List handles of dimension (``dim``) elements.

    Section: F.7.13.1.

    Args:
        arrayID: Handle referencing an array container.

    Returns:
        list[str]: Handles (possibly empty) of ``dim`` elements.
    """
    arr = _resolve_array(arrayID)
    return [get_handle(d) for d in getattr(arr, "dim", [])]


def getArrayIDs(parentID: str) -> list[str]:  # F.7.13.2
    """Return handles of child array containers under a parent.

    Section: F.7.13.2.

    The spec enumerates retrieval of arrays contained in a parent object. We
    treat any attributes named ``array`` or ``arrays`` (list) as array
    containers. Missing attributes produce an empty list.

    Args:
        parentID: Parent handle (any object).

    Returns:
        list[str]: Handles of arrays (empty if none).
    """
    parent = resolve_handle(parentID)
    if parent is None:
        raise TgiError("Invalid parent handle", TgiFaultCode.INVALID_ID)
    arrays: list[Any] = []
    cand = _get_attr(parent, "array", "arrays")
    if cand is None:
        return []
    arrays = cand if isinstance(cand, list) else [cand]
    return [get_handle(a) for a in arrays if hasattr(a, "dim")]


def getArrayLeftID(arrayID: str) -> str | None:  # F.7.13.3
    """Return handle of ``left`` bound element if present.

    Section: F.7.13.3.
    """
    arr = _resolve_array(arrayID)
    left = _get_attr(arr, "left")
    return get_handle(left) if left is not None else None


def getArrayRange(arrayID: str) -> int | None:  # F.7.13.4
    """Return numeric ``range`` value.

    Section: F.7.13.4.
    """
    arr = _resolve_array(arrayID)
    return _int_value(_get_attr(arr, "range"))


def getArrayRangeExpression(arrayID: str) -> str | None:  # F.7.13.5
    """Return ``range`` expression string.

    Section: F.7.13.5.
    """
    arr = _resolve_array(arrayID)
    r = _get_attr(arr, "range")
    return getattr(r, "value", None) if r is not None else None


def getArrayRightID(arrayID: str) -> str | None:  # F.7.13.6
    """Return handle of ``right`` bound element if present.

    Section: F.7.13.6.
    """
    arr = _resolve_array(arrayID)
    right = _get_attr(arr, "right")
    return get_handle(right) if right is not None else None


def getArrayStride(arrayID: str) -> int | None:  # F.7.13.7
    """Return numeric stride value (bit/part stride).

    Section: F.7.13.7.
    """
    arr = _resolve_array(arrayID)
    stride = _get_attr(arr, "stride", "bit_stride", "bitStride")
    return _int_value(stride)


def getArrayStrideExpression(arrayID: str) -> str | None:  # F.7.13.8
    """Return stride expression string.

    Section: F.7.13.8.
    """
    arr = _resolve_array(arrayID)
    stride = _get_attr(arr, "stride", "bit_stride", "bitStride")
    return getattr(stride, "value", None) if stride is not None else None


def getArrayStrideID(arrayID: str) -> str | None:  # F.7.13.9
    """Return handle of stride element.

    Section: F.7.13.9.
    """
    arr = _resolve_array(arrayID)
    stride = _get_attr(arr, "stride", "bit_stride", "bitStride")
    return get_handle(stride) if stride is not None else None


def getDimExpression(dimID: str) -> str | None:  # F.7.13.10
    """Return dimension expression string.

    Section: F.7.13.10.
    """
    dim = _resolve_dim(dimID)
    return getattr(dim, "value", None)


def getDimIndexVar(dimID: str) -> str | None:  # F.7.13.11
    """Return the ``indexVar`` attribute of a dimension.

    Section: F.7.13.11.
    """
    dim = _resolve_dim(dimID)
    return getattr(dim, "index_var", None) or getattr(dim, "indexVar", None)


def getDimValue(dimID: str) -> int | None:  # F.7.13.12
    """Return evaluated integer value of a dimension expression.

    Section: F.7.13.12.
    """
    dim = _resolve_dim(dimID)
    try:
        return int(getattr(dim, "value", None))  # type: ignore[arg-type]
    except Exception:  # pragma: no cover
        return None


def getRegisterArrayID(registerID: str) -> str | None:  # F.7.13.13
    """Return array handle for a register element if it has one.

    Section: F.7.13.13.
    """
    reg = resolve_handle(registerID)
    if reg is None:
        raise TgiError("Invalid register handle", TgiFaultCode.INVALID_ID)
    arr = _get_attr(reg, "array")
    return get_handle(arr) if (arr is not None and hasattr(arr, "dim")) else None


def getRegisterFieldArrayID(fieldID: str) -> str | None:  # F.7.13.14
    """Return array handle for a register field element if present.

    Section: F.7.13.14.
    """
    fld = resolve_handle(fieldID)
    if fld is None:
        raise TgiError("Invalid field handle", TgiFaultCode.INVALID_ID)
    arr = _get_attr(fld, "array")
    return get_handle(arr) if (arr is not None and hasattr(arr, "dim")) else None


# ---------------------------------------------------------------------------
# EXTENDED (F.7.14)
# ---------------------------------------------------------------------------

def addArray(parentID: str) -> str:  # F.7.14.1
    """Add a new generic ``array`` element under a parent.

    Section: F.7.14.1.

    This is a generic implementation; creation only succeeds if the parent
    has an attribute suitable for receiving arrays: ``array`` (single) or
    ``arrays`` (list). If both exist and ``arrays`` is a list, we append there.

    Args:
        parentID: Handle of the parent object.

    Returns:
        str: Handle of the created array.

    Raises:
        TgiError: If the parent handle is invalid or no array slot exists.
    """
    parent = resolve_handle(parentID)
    if parent is None:
        raise TgiError("Invalid parent handle", TgiFaultCode.INVALID_ID)
    # Prefer list container 'arrays'
    if hasattr(parent, "arrays") and isinstance(parent.arrays, list):  # type: ignore[attr-defined]
        class SimpleArray:  # minimal dynamic container
            def __init__(self):
                self.dim: list[Any] = []

        arr = SimpleArray()
        parent.arrays.append(arr)  # type: ignore[attr-defined]
        register_parent(arr, parent, ("arrays",), "list")
        return get_handle(arr)
    # Fallback single attribute 'array'
    if hasattr(parent, "array") and parent.array is None:  # type: ignore[attr-defined]
        class SimpleArray:  # minimal dynamic container
            def __init__(self):
                self.dim: list[Any] = []

        arr = SimpleArray()
        parent.array = arr  # type: ignore[attr-defined]
        register_parent(arr, parent, ("array",), "single")
        return get_handle(arr)
    raise TgiError("Parent cannot contain a new array", TgiFaultCode.INVALID_ARGUMENT)


def addArrayDim(arrayID: str, expression: str) -> str:  # F.7.14.2
    """Append a new ``dim`` element to an array.

    Section: F.7.14.2.

    Args:
        arrayID: Array handle.
        expression: Value/expression string.

    Returns:
        str: Handle of created dimension.

    Raises:
        TgiError: If array handle invalid.
    """
    arr = _resolve_array(arrayID)
    class Dim:  # minimal dynamic dimension
        def __init__(self, value: str):
            self.value = value
            self.index_var: str | None = None
    d = Dim(expression)
    arr.dim.append(d)  # type: ignore[attr-defined]
    register_parent(d, arr, ("dim",), "list")
    return get_handle(d)


def removeArray(arrayID: str) -> bool:  # F.7.14.3
    """Remove an ``array`` element.

    Section: F.7.14.3.

    Args:
        arrayID: Array handle.

    Returns:
        bool: ``True`` if removed, else ``False``.
    """
    return detach_child_by_handle(arrayID)


def removeArrayDim(dimID: str) -> bool:  # F.7.14.4
    """Remove a ``dim`` element.

    Section: F.7.14.4.

    Args:
        dimID: Dimension handle.

    Returns:
        bool: ``True`` if removed, else ``False``.
    """
    return detach_child_by_handle(dimID)


def removeArrayStride(arrayID: str) -> bool:  # F.7.14.5
    """Remove stride element if present.

    Section: F.7.14.5.

    Args:
        arrayID: Array handle.

    Returns:
        bool: ``True`` if present and removed, else ``False``.
    """
    arr = _resolve_array(arrayID)
    for name in ("stride", "bit_stride", "bitStride"):
        if hasattr(arr, name) and getattr(arr, name) is not None:
            setattr(arr, name, None)
            return True
    return False


def removeIndexVarAttribute(dimID: str) -> bool:  # F.7.14.6
    """Remove the ``indexVar`` attribute from a dimension.

    Section: F.7.14.6.

    Args:
        dimID: Dimension handle.

    Returns:
        bool: ``True`` if removed, ``False`` if not set.
    """
    dim = _resolve_dim(dimID)
    if hasattr(dim, "index_var") and dim.index_var is not None:  # type: ignore[attr-defined]
        dim.index_var = None  # type: ignore[attr-defined]
        return True
    if hasattr(dim, "indexVar") and dim.indexVar is not None:  # type: ignore[attr-defined]
        dim.indexVar = None  # type: ignore[attr-defined]
        return True
    return False


def setArrayStride(arrayID: str, value: int | str) -> bool:  # F.7.14.7
    """Set or create the stride element.

    Section: F.7.14.7.

    Args:
        arrayID: Array handle.
        value: Integer or expression string.

    Returns:
        bool: ``True`` on success.
    """
    arr = _resolve_array(arrayID)
    # Choose existing attribute preference; else create 'stride'.
    target_name = None
    for n in ("stride", "bit_stride", "bitStride"):
        if hasattr(arr, n):
            target_name = n
            break
    if target_name is None:
        target_name = "stride"
    class Stride:
        def __init__(self, v: str):
            self.value = v
    setattr(arr, target_name, Stride(str(value)))
    return True


def setDimIndexVar(dimID: str, name: str) -> bool:  # F.7.14.8
    """Set (or create) ``indexVar`` attribute of a dimension.

    Section: F.7.14.8.

    Args:
        dimID: Dimension handle.
        name: Index variable name.

    Returns:
        bool: ``True`` on success.
    """
    dim = _resolve_dim(dimID)
    if hasattr(dim, "index_var"):
        dim.index_var = name  # type: ignore[attr-defined]
    else:  # legacy variation
        dim.indexVar = name  # type: ignore[attr-defined]
    return True

