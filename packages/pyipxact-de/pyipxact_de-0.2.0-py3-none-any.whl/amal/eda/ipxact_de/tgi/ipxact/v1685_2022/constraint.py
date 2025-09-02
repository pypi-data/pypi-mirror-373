# ruff: noqa: I001
"""Constraint category TGI functions (IEEE 1685-2022).

Implements BASE (F.7.33) and EXTENDED (F.7.34) functions providing read and
write access to constraint related schema elements: ``constraintSet``,
``constraintSetRef``, ``driveConstraint``, ``loadConstraint`` and
``timingConstraint`` along with the nested ``cellSpecification`` and vector
range expressions.

Only the public functions defined in sections F.7.33 and F.7.34 are exported;
no convenience helpers. Invalid handles raise :class:`TgiError` with
``TgiFaultCode.INVALID_ID``. Operations that cannot be performed because of
schema state raise ``TgiFaultCode.INVALID_ARGUMENT``.
"""

from org.accellera.ipxact.v1685_2022.cell_specification import CellSpecification
from org.accellera.ipxact.v1685_2022.constraint_set import ConstraintSet
from org.accellera.ipxact.v1685_2022.constraint_set_ref import ConstraintSetRef
from org.accellera.ipxact.v1685_2022.drive_constraint import DriveConstraint
from org.accellera.ipxact.v1685_2022.load_constraint import LoadConstraint
from org.accellera.ipxact.v1685_2022.timing_constraint import TimingConstraint
from org.accellera.ipxact.v1685_2022.unsigned_int_expression import UnsignedIntExpression
from org.accellera.ipxact.v1685_2022.unsigned_positive_int_expression import UnsignedPositiveIntExpression

from .core import (
    TgiError,
    TgiFaultCode,
    get_handle,
    resolve_handle,
    register_parent,
    detach_child_by_handle,
)

__all__ = [
    # BASE (F.7.33)
    "getCellSpecificationCellClass",
    "getCellSpecificationCellFunction",
    "getCellSpecificationCellFunctionID",
    "getConstraintSetDriveConstraintCellSpecificationID",
    "getConstraintSetLoadConstraintID",
    "getConstraintSetRefLocalName",
    "getConstraintSetReferenceName",
    "getConstraintSetTimingConstraintIDs",
    "getConstraintSetVector",
    "getConstraintSetVectorExpression",
    "getConstraintSetVectorLeftID",
    "getConstraintSetVectorRightID",
    "getDriveConstraintOther",
    "getDriveConstraintType",
    "getDriveConstraintValue",
    "getLoadConstraintCellSpecificationID",
    "getLoadConstraintCount",
    "getLoadConstraintCountExpression",
    "getLoadConstraintCountID",
    "getLoadConstraintOther",
    "getLoadConstraintType",
    "getLoadConstraintValue",
    "getTimingConstraintValue",
    # EXTENDED (F.7.34)
    "removeConstraintSetDriveConstraint",
    "removeConstraintSetLoadConstraint",
    "removeConstraintSetTimingConstraint",
    "removeConstraintSetVector",
    "removeLoadConstraintCount",
    "setCellSpecificationCellClass",
    "setCellSpecificationCellFunction",
    "setConstraintSetDriveConstraint",
    "setConstraintSetLoadConstraint",
    "setConstraintSetReferenceName",
    "setConstraintSetVector",
    "setDriveConstraintOtherValue",
    "setDriveConstraintValue",
    "setLoadConstraintCellSpecification",
    "setLoadConstraintCount",
    "setLoadConstraintOtherValue",
    "setTimingConstraintValue",
]


# ---------------------------------------------------------------------------
# Internal helpers (non-spec)
# ---------------------------------------------------------------------------

def _as_cell_specification(handle: str) -> CellSpecification | None:
    obj = resolve_handle(handle)
    return obj if isinstance(obj, CellSpecification) else None


def _as_constraint_set(handle: str) -> ConstraintSet | None:
    obj = resolve_handle(handle)
    return obj if isinstance(obj, ConstraintSet) else None


def _as_drive_constraint(handle: str) -> DriveConstraint | None:
    obj = resolve_handle(handle)
    return obj if isinstance(obj, DriveConstraint) else None


def _as_load_constraint(handle: str) -> LoadConstraint | None:
    obj = resolve_handle(handle)
    return obj if isinstance(obj, LoadConstraint) else None


def _as_timing_constraint(handle: str) -> TimingConstraint | None:
    obj = resolve_handle(handle)
    return obj if isinstance(obj, TimingConstraint) else None


def _as_constraint_set_ref(handle: str) -> ConstraintSetRef | None:
    obj = resolve_handle(handle)
    return obj if isinstance(obj, ConstraintSetRef) else None


# ---------------------------------------------------------------------------
# BASE (F.7.33)
# ---------------------------------------------------------------------------

def getCellSpecificationCellClass(cellSpecificationID: str) -> str | None:
    """Return the ``cellClass`` enumeration value of a cellSpecification.

    Section: F.7.33.1.
    """
    cs = _as_cell_specification(cellSpecificationID)
    if cs is None:
        raise TgiError("Invalid cellSpecification handle", TgiFaultCode.INVALID_ID)
    return getattr(cs, "cell_class", None)


def getCellSpecificationCellFunction(cellSpecificationID: str) -> str | None:
    """Return the ``cellFunction`` enumeration value of a cellSpecification.

    Section: F.7.33.2.
    """
    cs = _as_cell_specification(cellSpecificationID)
    if cs is None:
        raise TgiError("Invalid cellSpecification handle", TgiFaultCode.INVALID_ID)
    cf = getattr(cs, "cell_function", None)
    return None if cf is None else getattr(cf, "value", None)


def getCellSpecificationCellFunctionID(cellSpecificationID: str) -> str | None:
    """Return handle of the ``cellFunction`` element of a cellSpecification.

    Section: F.7.33.3.
    """
    cs = _as_cell_specification(cellSpecificationID)
    if cs is None:
        raise TgiError("Invalid cellSpecification handle", TgiFaultCode.INVALID_ID)
    if cs.cell_function is None:
        return None
    return get_handle(cs.cell_function)


def getConstraintSetDriveConstraintCellSpecificationID(constraintSetID: str) -> str | None:
    """Return handle of ``cellSpecification`` inside the driveConstraint.

    Section: F.7.33.4.
    """
    cs = _as_constraint_set(constraintSetID)
    if cs is None:
        raise TgiError("Invalid constraintSet handle", TgiFaultCode.INVALID_ID)
    dc = cs.drive_constraint
    if dc is None or dc.cell_specification is None:
        return None
    return get_handle(dc.cell_specification)


def getConstraintSetLoadConstraintID(constraintSetID: str) -> str | None:
    """Return handle of the ``loadConstraint`` element.

    Section: F.7.33.5.
    """
    cs = _as_constraint_set(constraintSetID)
    if cs is None:
        raise TgiError("Invalid constraintSet handle", TgiFaultCode.INVALID_ID)
    lc = cs.load_constraint
    return None if lc is None else get_handle(lc)


def getConstraintSetRefLocalName(constraintSetRefID: str) -> str | None:
    """Return the local name value of a constraintSetRef.

    Section: F.7.33.6.
    """
    ref = _as_constraint_set_ref(constraintSetRefID)
    if ref is None:
        raise TgiError("Invalid constraintSetRef handle", TgiFaultCode.INVALID_ID)
    return getattr(ref, "value", None)


def getConstraintSetReferenceName(constraintSetID: str) -> str | None:
    """Return the ``constraintSetId`` attribute of a constraintSet.

    Section: F.7.33.7.
    """
    cs = _as_constraint_set(constraintSetID)
    if cs is None:
        raise TgiError("Invalid constraintSet handle", TgiFaultCode.INVALID_ID)
    return getattr(cs, "constraint_set_id", None)


def getConstraintSetTimingConstraintIDs(constraintSetID: str) -> list[str]:
    """Return handles of all ``timingConstraint`` children of a constraintSet.

    Section: F.7.33.8.
    """
    cs = _as_constraint_set(constraintSetID)
    if cs is None:
        raise TgiError("Invalid constraintSet handle", TgiFaultCode.INVALID_ID)
    return [get_handle(t) for t in getattr(cs, "timing_constraint", [])]


def getConstraintSetVector(constraintSetID: str) -> list[int | None]:
    """Return [left, right] evaluated integer values of constraintSet vector.

    Section: F.7.33.9. Returns [None, None] if vector absent or expressions unevaluated.
    """
    cs = _as_constraint_set(constraintSetID)
    if cs is None:
        raise TgiError("Invalid constraintSet handle", TgiFaultCode.INVALID_ID)
    vec = cs.vector
    if vec is None:
        return [None, None]
    left = getattr(vec.left, "value", None) if vec.left is not None else None
    right = getattr(vec.right, "value", None) if vec.right is not None else None
    return [left, right]


def getConstraintSetVectorExpression(constraintSetID: str) -> list[str | None]:
    """Return [leftExpr, rightExpr] textual expressions of vector bounds.

    Section: F.7.33.10.
    """
    cs = _as_constraint_set(constraintSetID)
    if cs is None:
        raise TgiError("Invalid constraintSet handle", TgiFaultCode.INVALID_ID)
    vec = cs.vector
    if vec is None:
        return [None, None]
    left_expr = getattr(vec.left, "value", None) if vec.left is not None else None
    right_expr = getattr(vec.right, "value", None) if vec.right is not None else None
    return [left_expr, right_expr]


def getConstraintSetVectorLeftID(constraintSetID: str) -> str | None:
    """Return handle of left side expression element of vector.

    Section: F.7.33.11.
    """
    cs = _as_constraint_set(constraintSetID)
    if cs is None:
        raise TgiError("Invalid constraintSet handle", TgiFaultCode.INVALID_ID)
    vec = cs.vector
    if vec is None or vec.left is None:
        return None
    return get_handle(vec.left)


def getConstraintSetVectorRightID(constraintSetID: str) -> str | None:
    """Return handle of right side expression element of vector.

    Section: F.7.33.12.
    """
    cs = _as_constraint_set(constraintSetID)
    if cs is None:
        raise TgiError("Invalid constraintSet handle", TgiFaultCode.INVALID_ID)
    vec = cs.vector
    if vec is None or vec.right is None:
        return None
    return get_handle(vec.right)


def getDriveConstraintOther(driveConstraintID: str) -> str | None:
    """Return the ``other`` attribute of driveConstraint.cellSpecification.cellFunction.

    Section: F.7.33.13.
    """
    dc = _as_drive_constraint(driveConstraintID)
    if dc is None:
        raise TgiError("Invalid driveConstraint handle", TgiFaultCode.INVALID_ID)
    cspec = dc.cell_specification
    if cspec is None or cspec.cell_function is None:
        return None
    return getattr(cspec.cell_function, "other", None)


def getDriveConstraintType(driveConstraintID: str) -> str | None:
    """Return type of driveConstraint (cellFunction value or cellClass value).

    Section: F.7.33.14.
    """
    dc = _as_drive_constraint(driveConstraintID)
    if dc is None:
        raise TgiError("Invalid driveConstraint handle", TgiFaultCode.INVALID_ID)
    cspec = dc.cell_specification
    if cspec is None:
        return None
    if cspec.cell_function is not None and getattr(cspec.cell_function, "value", None) is not None:
        return getattr(cspec.cell_function, "value", None)
    return getattr(cspec, "cell_class", None)


def getDriveConstraintValue(driveConstraintID: str) -> str | None:
    """Return the drive constraint strength value (cellStrength attribute).

    Section: F.7.33.15.
    """
    dc = _as_drive_constraint(driveConstraintID)
    if dc is None:
        raise TgiError("Invalid driveConstraint handle", TgiFaultCode.INVALID_ID)
    cspec = dc.cell_specification
    return None if cspec is None else getattr(cspec, "cell_strength", None)


def getLoadConstraintCellSpecificationID(loadConstraintID: str) -> str | None:
    """Return handle of the ``cellSpecification`` of a loadConstraint.

    Section: F.7.33.16.
    """
    lc = _as_load_constraint(loadConstraintID)
    if lc is None:
        raise TgiError("Invalid loadConstraint handle", TgiFaultCode.INVALID_ID)
    if lc.cell_specification is None:
        return None
    return get_handle(lc.cell_specification)


def getLoadConstraintCount(loadConstraintID: str) -> int | None:
    """Return numeric count of a loadConstraint.

    Section: F.7.33.17.
    """
    lc = _as_load_constraint(loadConstraintID)
    if lc is None:
        raise TgiError("Invalid loadConstraint handle", TgiFaultCode.INVALID_ID)
    cnt = lc.count
    return getattr(cnt, "value", None) if cnt is not None else None


def getLoadConstraintCountExpression(loadConstraintID: str) -> str | None:
    """Return textual count expression of a loadConstraint.

    Section: F.7.33.18.
    """
    # Count expression stored in same value field; convert to string if present.
    val = getLoadConstraintCount(loadConstraintID)
    return None if val is None else str(val)


def getLoadConstraintCountID(loadConstraintID: str) -> str | None:
    """Return handle of the ``count`` expression element.

    Section: F.7.33.19.
    """
    lc = _as_load_constraint(loadConstraintID)
    if lc is None:
        raise TgiError("Invalid loadConstraint handle", TgiFaultCode.INVALID_ID)
    cnt = lc.count
    return None if cnt is None else get_handle(cnt)


def getLoadConstraintOther(loadConstraintID: str) -> str | None:
    """Return the ``other`` attribute (cellFunction based specification only).

    Section: F.7.33.20.
    """
    lc = _as_load_constraint(loadConstraintID)
    if lc is None:
        raise TgiError("Invalid loadConstraint handle", TgiFaultCode.INVALID_ID)
    cspec = lc.cell_specification
    if cspec is None or cspec.cell_function is None:
        return None
    return getattr(cspec.cell_function, "other", None)


def getLoadConstraintType(loadConstraintID: str) -> str | None:
    """Return type of a loadConstraint (cellFunction value or cellClass value).

    Section: F.7.33.21.
    """
    lc = _as_load_constraint(loadConstraintID)
    if lc is None:
        raise TgiError("Invalid loadConstraint handle", TgiFaultCode.INVALID_ID)
    cspec = lc.cell_specification
    if cspec is None:
        return None
    if cspec.cell_function is not None and getattr(cspec.cell_function, "value", None) is not None:
        return getattr(cspec.cell_function, "value", None)
    return getattr(cspec, "cell_class", None)


def getLoadConstraintValue(loadConstraintID: str) -> str | None:
    """Return the load constraint strength value (cellStrength attribute).

    Section: F.7.33.22.
    """
    lc = _as_load_constraint(loadConstraintID)
    if lc is None:
        raise TgiError("Invalid loadConstraint handle", TgiFaultCode.INVALID_ID)
    cspec = lc.cell_specification
    return None if cspec is None else getattr(cspec, "cell_strength", None)


def getTimingConstraintValue(timingConstraintID: str) -> float | None:
    """Return numeric value of a timingConstraint.

    Section: F.7.33.23.
    """
    tc = _as_timing_constraint(timingConstraintID)
    if tc is None:
        raise TgiError("Invalid timingConstraint handle", TgiFaultCode.INVALID_ID)
    return getattr(tc, "value", None)


# ---------------------------------------------------------------------------
# EXTENDED (F.7.34)
# ---------------------------------------------------------------------------

def removeConstraintSetDriveConstraint(constraintSetID: str) -> bool:
    """Remove the driveConstraint child from a constraintSet.

    Section: F.7.34.1.
    """
    cs = _as_constraint_set(constraintSetID)
    if cs is None:
        raise TgiError("Invalid constraintSet handle", TgiFaultCode.INVALID_ID)
    if cs.drive_constraint is None:
        return False
    handle = get_handle(cs.drive_constraint)
    cs.drive_constraint = None
    detach_child_by_handle(handle)
    return True


def removeConstraintSetLoadConstraint(constraintSetID: str) -> bool:
    """Remove the loadConstraint child from a constraintSet.

    Section: F.7.34.2.
    """
    cs = _as_constraint_set(constraintSetID)
    if cs is None:
        raise TgiError("Invalid constraintSet handle", TgiFaultCode.INVALID_ID)
    if cs.load_constraint is None:
        return False
    handle = get_handle(cs.load_constraint)
    cs.load_constraint = None
    detach_child_by_handle(handle)
    return True


def removeConstraintSetTimingConstraint(timingConstraintID: str) -> bool:
    """Remove a timingConstraint element.

    Section: F.7.34.3.
    """
    tc = _as_timing_constraint(timingConstraintID)
    if tc is None:
        return False
    return detach_child_by_handle(timingConstraintID)


def removeConstraintSetVector(constraintSetID: str) -> bool:
    """Remove vector element from a constraintSet.

    Section: F.7.34.4.
    """
    cs = _as_constraint_set(constraintSetID)
    if cs is None:
        raise TgiError("Invalid constraintSet handle", TgiFaultCode.INVALID_ID)
    if cs.vector is None:
        return False
    handle_left = get_handle(cs.vector.left) if cs.vector.left is not None else None
    handle_right = get_handle(cs.vector.right) if cs.vector.right is not None else None
    cs.vector = None
    if handle_left:
        detach_child_by_handle(handle_left)
    if handle_right:
        detach_child_by_handle(handle_right)
    return True


def removeLoadConstraintCount(loadConstraintID: str) -> bool:
    """Remove ``count`` element from a loadConstraint.

    Section: F.7.34.5.
    """
    lc = _as_load_constraint(loadConstraintID)
    if lc is None:
        raise TgiError("Invalid loadConstraint handle", TgiFaultCode.INVALID_ID)
    if lc.count is None:
        return False
    handle = get_handle(lc.count)
    lc.count = None
    detach_child_by_handle(handle)
    return True


def setCellSpecificationCellClass(cellSpecificationID: str, cellClass: str) -> bool:
    """Set ``cellClass`` enumeration of a cellSpecification (clears cellFunction).

    Section: F.7.34.6.
    """
    cs = _as_cell_specification(cellSpecificationID)
    if cs is None:
        raise TgiError("Invalid cellSpecification handle", TgiFaultCode.INVALID_ID)
    cs.cell_function = None
    cs.cell_class = cellClass  # type: ignore[assignment]
    return True


def setCellSpecificationCellFunction(cellSpecificationID: str, cellFunction: str) -> bool:
    """Set ``cellFunction`` enumeration of a cellSpecification (clears cellClass).

    Section: F.7.34.7.
    """
    cs = _as_cell_specification(cellSpecificationID)
    if cs is None:
        raise TgiError("Invalid cellSpecification handle", TgiFaultCode.INVALID_ID)
    from org.accellera.ipxact.v1685_2022.cell_specification import (  # local import to avoid cycle
        CellSpecification as CS,
    )

    cs.cell_class = None
    cs.cell_function = CS.CellFunction(value=cellFunction)  # type: ignore[arg-type]
    return True


def setConstraintSetDriveConstraint(constraintSetID: str, cellFunctionOrCellClass: str) -> bool:
    """Create/replace driveConstraint with given type (function or class).

    Section: F.7.34.8. Strength left unspecified (None) until separately set.
    """
    cs = _as_constraint_set(constraintSetID)
    if cs is None:
        raise TgiError("Invalid constraintSet handle", TgiFaultCode.INVALID_ID)
    # Determine if value matches canonical cell function names vs class.
    functions = {"nand2", "buf", "inv", "mux21", "dff", "latch", "xor2", "other"}
    spec = CellSpecification()
    if cellFunctionOrCellClass in functions:
        from org.accellera.ipxact.v1685_2022.cell_specification import CellSpecification as CS  # noqa: F401

        spec.cell_function = CS.CellFunction(value=cellFunctionOrCellClass)  # type: ignore[arg-type]
    else:
        spec.cell_class = cellFunctionOrCellClass  # type: ignore[assignment]
    dc = DriveConstraint(cell_specification=spec)
    cs.drive_constraint = dc
    register_parent(dc, cs, ("drive_constraint",), "single")
    return True


def setConstraintSetLoadConstraint(constraintSetID: str, cellFunctionOrCellClass: str) -> bool:
    """Create/replace loadConstraint with given type (function or class).

    Section: F.7.34.9.
    """
    cs = _as_constraint_set(constraintSetID)
    if cs is None:
        raise TgiError("Invalid constraintSet handle", TgiFaultCode.INVALID_ID)
    functions = {"nand2", "buf", "inv", "mux21", "dff", "latch", "xor2", "other"}
    spec = CellSpecification()
    if cellFunctionOrCellClass in functions:
        from org.accellera.ipxact.v1685_2022.cell_specification import CellSpecification as CS

        spec.cell_function = CS.CellFunction(value=cellFunctionOrCellClass)  # type: ignore[arg-type]
    else:
        spec.cell_class = cellFunctionOrCellClass  # type: ignore[assignment]
    lc = LoadConstraint(cell_specification=spec)
    cs.load_constraint = lc
    register_parent(lc, cs, ("load_constraint",), "single")
    return True


def setConstraintSetReferenceName(constraintSetID: str, referenceName: str) -> bool:
    """Set the ``constraintSetId`` attribute of a constraintSet.

    Section: F.7.34.10.
    """
    cs = _as_constraint_set(constraintSetID)
    if cs is None:
        raise TgiError("Invalid constraintSet handle", TgiFaultCode.INVALID_ID)
    cs.constraint_set_id = referenceName
    return True


def setConstraintSetVector(constraintSetID: str, vector: list[str]) -> bool:
    """Set vector left/right expression values for a constraintSet.

    Section: F.7.34.11. Expects list/tuple of two strings.
    """
    if len(vector) != 2:
        raise TgiError("Vector must have two expressions", TgiFaultCode.INVALID_ARGUMENT)
    cs = _as_constraint_set(constraintSetID)
    if cs is None:
        raise TgiError("Invalid constraintSet handle", TgiFaultCode.INVALID_ID)
    left_expr, right_expr = vector
    vec = ConstraintSet.Vector(
        left=UnsignedIntExpression(value=left_expr),  # type: ignore[arg-type]
        right=UnsignedIntExpression(value=right_expr),  # type: ignore[arg-type]
    )
    cs.vector = vec
    register_parent(vec, cs, ("vector",), "single")
    return True


def setDriveConstraintOtherValue(driveConstraintID: str, other: str) -> bool:
    """Set ``other`` attribute for driveConstraint cellFunction variant.

    Section: F.7.34.12.
    """
    dc = _as_drive_constraint(driveConstraintID)
    if dc is None:
        raise TgiError("Invalid driveConstraint handle", TgiFaultCode.INVALID_ID)
    cspec = dc.cell_specification
    if cspec is None or cspec.cell_function is None:
        return False
    cspec.cell_function.other = other
    return True


def setDriveConstraintValue(driveConstraintID: str, value: str) -> bool:
    """Set cellStrength (value) for driveConstraint cellSpecification.

    Section: F.7.34.13.
    """
    dc = _as_drive_constraint(driveConstraintID)
    if dc is None:
        raise TgiError("Invalid driveConstraint handle", TgiFaultCode.INVALID_ID)
    if dc.cell_specification is None:
        return False
    dc.cell_specification.cell_strength = value  # type: ignore[assignment]
    return True


def setLoadConstraintCellSpecification(loadConstraintID: str, cellFunctionOrCellClass: str) -> bool:
    """Replace loadConstraint cellSpecification definition.

    Section: F.7.34.14.
    """
    lc = _as_load_constraint(loadConstraintID)
    if lc is None:
        raise TgiError("Invalid loadConstraint handle", TgiFaultCode.INVALID_ID)
    functions = {"nand2", "buf", "inv", "mux21", "dff", "latch", "xor2", "other"}
    spec = CellSpecification()
    if cellFunctionOrCellClass in functions:
        from org.accellera.ipxact.v1685_2022.cell_specification import CellSpecification as CS

        spec.cell_function = CS.CellFunction(value=cellFunctionOrCellClass)  # type: ignore[arg-type]
    else:
        spec.cell_class = cellFunctionOrCellClass  # type: ignore[assignment]
    lc.cell_specification = spec
    return True


def setLoadConstraintCount(loadConstraintID: str, count: str) -> bool:
    """Set numeric count (expression) of loadConstraint.

    Section: F.7.34.15.
    """
    lc = _as_load_constraint(loadConstraintID)
    if lc is None:
        raise TgiError("Invalid loadConstraint handle", TgiFaultCode.INVALID_ID)
    lc.count = UnsignedPositiveIntExpression(value=count)  # type: ignore[arg-type]
    return True


def setLoadConstraintOtherValue(loadConstraintID: str, other: str) -> bool:
    """Set ``other`` attribute for loadConstraint cellFunction variant.

    Section: F.7.34.16.
    """
    lc = _as_load_constraint(loadConstraintID)
    if lc is None:
        raise TgiError("Invalid loadConstraint handle", TgiFaultCode.INVALID_ID)
    cspec = lc.cell_specification
    if cspec is None or cspec.cell_function is None:
        return False
    cspec.cell_function.other = other
    return True


def setTimingConstraintValue(timingConstraintID: str, value: str) -> bool:
    """Set ``value`` of a timingConstraint (stored as float).

    Section: F.7.34.17.
    """
    tc = _as_timing_constraint(timingConstraintID)
    if tc is None:
        raise TgiError("Invalid timingConstraint handle", TgiFaultCode.INVALID_ID)
    try:
        tc.value = float(value)  # type: ignore[assignment]
    except ValueError as exc:  # pragma: no cover
        raise TgiError("Invalid timingConstraint value", TgiFaultCode.INVALID_ARGUMENT) from exc
    return True

