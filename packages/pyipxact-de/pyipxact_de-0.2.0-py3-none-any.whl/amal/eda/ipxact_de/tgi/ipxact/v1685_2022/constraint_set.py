"""Constraint Set category TGI functions (IEEE 1685-2022).

Implements only the public API defined in Annex F sections:

* F.7.35 Constraint Set (BASE)
* F.7.36 Constraint Set (EXTENDED)

Per the 2022 specification these sections currently define exactly two
functions:

* getConstraintSetTimingConstraints (F.7.35.1)
* addConstraintSetTimingConstraint (F.7.36.1)

Previous convenience traversal/getter helpers have been removed to satisfy
the requirement that this module expose *no more and no less* than the
standard TGI functions. Historical comment section markers are preserved to
conform to project guidelines about retaining comments.

Invalid handles raise :class:`TgiError` with ``TgiFaultCode.INVALID_ID``.
Mutation routines return a Boolean status (true on success) unless the spec
defines a different return (adding returns the new element handle).
"""
# ruff: noqa: I001

from org.accellera.ipxact.v1685_2022.constraint_set import ConstraintSet
from org.accellera.ipxact.v1685_2022.timing_constraint import TimingConstraint

from .core import TgiError, TgiFaultCode, get_handle, resolve_handle, register_parent

__all__ = [
    "getConstraintSetTimingConstraints",  # F.7.35.1 (BASE)
    "addConstraintSetTimingConstraint",  # F.7.36.1 (EXTENDED)
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _resolve_constraint_set(csID: str) -> ConstraintSet | None:
    """Helper: resolve handle to ``ConstraintSet`` or ``None``."""
    obj = resolve_handle(csID)
    return obj if isinstance(obj, ConstraintSet) else None


# ---------------------------------------------------------------------------
# Traversal
# ---------------------------------------------------------------------------

def getConstraintSetTimingConstraints(constraintSetID: str) -> list[float]:
    """Return all timingConstraint values for the given constraintSet.

    Section: F.7.35.1.

    Args:
        constraintSetID: Handle referencing a ``constraintSet`` element.

    Returns:
        list[float]: The list of timing constraint numeric values (empty if none).

    Raises:
        TgiError: If the handle does not reference a ``ConstraintSet``.
    """
    cs = _resolve_constraint_set(constraintSetID)
    if cs is None:
        raise TgiError("Invalid constraintSet handle", TgiFaultCode.INVALID_ID)
    values: list[float] = []
    for tc in getattr(cs, "timing_constraint", []):  # type: ignore[attr-defined]
        if isinstance(tc, TimingConstraint) and tc.value is not None:  # defensive
            values.append(tc.value)
    return values


# ---------------------------------------------------------------------------
# Getters
# ---------------------------------------------------------------------------

def addConstraintSetTimingConstraint(constraintSetID: str, value: float, clockName: str) -> str:
    """Add a new timingConstraint to the given constraintSet.

    Section: F.7.36.1.

    Args:
        constraintSetID: Handle referencing a ``constraintSet`` element.
        value: Timing constraint value (0.0 – 100.0 inclusive per schema range).
        clockName: Name of the associated clock.

    Returns:
        str: Handle of the newly created ``timingConstraint`` element.

    Raises:
        TgiError: If the parent handle is invalid or value cannot be applied.
    """
    cs = _resolve_constraint_set(constraintSetID)
    if cs is None:
        raise TgiError("Invalid constraintSet handle", TgiFaultCode.INVALID_ID)
    tc = TimingConstraint(value=value, clock_name=clockName)  # type: ignore[arg-type]
    # The timing_constraint field is an iterable list (list default factory in schema)
    getattr(cs, "timing_constraint", []).append(tc)  # type: ignore[attr-defined]
    register_parent(tc, cs, ("timing_constraint",), "list")
    return get_handle(tc)

