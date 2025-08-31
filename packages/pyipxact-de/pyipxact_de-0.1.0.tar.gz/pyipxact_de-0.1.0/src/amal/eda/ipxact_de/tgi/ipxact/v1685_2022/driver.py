"""Driver category TGI functions (IEEE 1685-2022).

Implements BASE (F.7.41) and EXTENDED (F.7.42) public TGI functions for
``driver`` elements. A driver represents value-driving semantics for wire
ports – clock drivers, single-shot drivers, default values and optional range
and viewRef associations. Only the API defined in Annex F is exported (no more,
no less).

Mutator functions return ``True`` on success; remove* functions return ``False``
when the target element/attribute was absent. All functions raise
``TgiError`` with ``TgiFaultCode.INVALID_ID`` for invalid handles. Value/
expression getters return ``None`` when the element does not exist.
"""

# ruff: noqa: I001
from __future__ import annotations

from org.accellera.ipxact.v1685_2022 import (
    Driver,
    ClockDriver,
    SingleShotDriver,
    DefaultValue,
    DriverType,
)
from org.accellera.ipxact.v1685_2022.clock_driver_type import ClockDriverType
from org.accellera.ipxact.v1685_2022.single_shot_driver import SingleShotDriver as SingleShotDriverClass
from org.accellera.ipxact.v1685_2022.range import Range as RangeClass
from org.accellera.ipxact.v1685_2022.left import Left
from org.accellera.ipxact.v1685_2022.right import Right

from .core import (
    TgiError,
    TgiFaultCode,
    resolve_handle,
    get_handle,
    register_parent,
    detach_child_by_handle,
)

__all__ = [
    # BASE (F.7.41)
    "getClockDriverClockPeriod",
    "getClockDriverClockPeriodExpression",
    "getClockDriverClockPeriodID",
    "getClockDriverClockPulseDuration",
    "getClockDriverClockPulseDurationExpression",
    "getClockDriverClockPulseDurationID",
    "getClockDriverClockPulseOffset",
    "getClockDriverClockPulseOffsetExpression",
    "getClockDriverClockPulseOffsetID",
    "getClockDriverClockPulseValue",
    "getClockDriverClockPulseValueExpression",
    "getClockDriverClockPulseValueID",
    "getDriverClockDriverID",
    "getDriverDefaultValue",
    "getDriverDefaultValueExpression",
    "getDriverDefaultValueID",
    "getDriverLeftID",
    "getDriverRange",
    "getDriverRangeExpression",
    "getDriverRightID",
    # EXTENDED (F.7.42)
    "addDriverSingleShotDriver",
    "addDriverViewRef",
    "removeDriverClockDriver",
    "removeDriverRange",
    "removeDriverSingleShotDriver",
    "removeDriverViewRef",
    "setClockDriverClockPeriod",
    "setClockDriverClockPulseDuration",
    "setClockDriverClockPulseOffset",
    "setClockDriverClockPulseValue",
    "setDriverClockDriver",
    "setDriverSingleShotDriver",
    "setDriverDefaultValue",
    "setDriverRange",
    "setOtherClockDriverClockPeriod",
    "setOtherClockDriverClockPulseDuration",
    "setOtherClockDriverClockPulseOffset",
    "setOtherClockDriverClockPulseValue",
    "setSingleShotDriverSingleShotDuration",
    "setSingleShotDriverSingleShotOffset",
]


# ---------------------------------------------------------------------------
# Helpers (non-spec)
# ---------------------------------------------------------------------------

def _resolve_driver(driverID: str) -> Driver | None:
    obj = resolve_handle(driverID)
    return obj if isinstance(obj, Driver) else None


def _resolve_clock_driver(clockDriverID: str) -> ClockDriver | None:
    obj = resolve_handle(clockDriverID)
    return obj if isinstance(obj, ClockDriver) else None


def _resolve_single_shot(singleShotDriverID: str) -> SingleShotDriver | None:
    obj = resolve_handle(singleShotDriverID)
    return obj if isinstance(obj, SingleShotDriver) else None


def _ensure_clock(driver: Driver) -> ClockDriver:
    if driver.clock_driver is None:
        driver.clock_driver = ClockDriver(  # type: ignore[assignment]
            clock_period=ClockDriverType.ClockPeriod(),
            clock_pulse_offset=ClockDriverType.ClockPulseOffset(),
            clock_pulse_value=None,  # will be set by setter
            clock_pulse_duration=ClockDriverType.ClockPulseDuration(),
        )
        register_parent(driver.clock_driver, driver, ("clock_driver",), "single")
    return driver.clock_driver  # type: ignore[return-value]


def _ensure_single_shot(driver: Driver) -> SingleShotDriver:
    if driver.single_shot_driver is None:
        driver.single_shot_driver = SingleShotDriverClass(  # type: ignore[assignment]
            single_shot_offset=SingleShotDriverClass.SingleShotOffset(),
            single_shot_value=None,
            single_shot_duration=SingleShotDriverClass.SingleShotDuration(),
        )
        register_parent(driver.single_shot_driver, driver, ("single_shot_driver",), "single")
    return driver.single_shot_driver  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# BASE (F.7.41)
# ---------------------------------------------------------------------------

def getClockDriverClockPeriod(clockDriverID: str) -> float | None:
    """Return numeric value of ``clockPeriod``.

    Section: F.7.41.1.
    """
    cd = _resolve_clock_driver(clockDriverID)
    if cd is None:
        raise TgiError("Invalid clockDriver handle", TgiFaultCode.INVALID_ID)
    cp = cd.clock_period
    return None if cp is None else getattr(cp, "value", None)


def getClockDriverClockPeriodExpression(clockDriverID: str) -> str | None:
    """Return expression string of ``clockPeriod`` if present.

    Section: F.7.41.2.
    """
    cd = _resolve_clock_driver(clockDriverID)
    if cd is None:
        raise TgiError("Invalid clockDriver handle", TgiFaultCode.INVALID_ID)
    cp = cd.clock_period
    return None if cp is None else getattr(cp, "expression", None)


def getClockDriverClockPeriodID(clockDriverID: str) -> str | None:
    """Return handle of ``clockPeriod`` element.

    Section: F.7.41.3.
    """
    cd = _resolve_clock_driver(clockDriverID)
    if cd is None:
        raise TgiError("Invalid clockDriver handle", TgiFaultCode.INVALID_ID)
    cp = cd.clock_period
    return None if cp is None else get_handle(cp)


def getClockDriverClockPulseDuration(clockDriverID: str) -> float | None:
    """Return numeric value of ``clockPulseDuration``.

    Section: F.7.41.4.
    """
    cd = _resolve_clock_driver(clockDriverID)
    if cd is None:
        raise TgiError("Invalid clockDriver handle", TgiFaultCode.INVALID_ID)
    val = cd.clock_pulse_duration
    return None if val is None else getattr(val, "value", None)


def getClockDriverClockPulseDurationExpression(clockDriverID: str) -> str | None:
    """Return expression for ``clockPulseDuration``.

    Section: F.7.41.5.
    """
    cd = _resolve_clock_driver(clockDriverID)
    if cd is None:
        raise TgiError("Invalid clockDriver handle", TgiFaultCode.INVALID_ID)
    val = cd.clock_pulse_duration
    return None if val is None else getattr(val, "expression", None)


def getClockDriverClockPulseDurationID(clockDriverID: str) -> str | None:
    """Return handle of ``clockPulseDuration``.

    Section: F.7.41.6.
    """
    cd = _resolve_clock_driver(clockDriverID)
    if cd is None:
        raise TgiError("Invalid clockDriver handle", TgiFaultCode.INVALID_ID)
    val = cd.clock_pulse_duration
    return None if val is None else get_handle(val)


def getClockDriverClockPulseOffset(clockDriverID: str) -> float | None:
    """Return numeric value of ``clockPulseOffset``.

    Section: F.7.41.7.
    """
    cd = _resolve_clock_driver(clockDriverID)
    if cd is None:
        raise TgiError("Invalid clockDriver handle", TgiFaultCode.INVALID_ID)
    val = cd.clock_pulse_offset
    return None if val is None else getattr(val, "value", None)


def getClockDriverClockPulseOffsetExpression(clockDriverID: str) -> str | None:
    """Return expression of ``clockPulseOffset``.

    Section: F.7.41.8.
    """
    cd = _resolve_clock_driver(clockDriverID)
    if cd is None:
        raise TgiError("Invalid clockDriver handle", TgiFaultCode.INVALID_ID)
    val = cd.clock_pulse_offset
    return None if val is None else getattr(val, "expression", None)


def getClockDriverClockPulseOffsetID(clockDriverID: str) -> str | None:
    """Return handle of ``clockPulseOffset``.

    Section: F.7.41.9.
    """
    cd = _resolve_clock_driver(clockDriverID)
    if cd is None:
        raise TgiError("Invalid clockDriver handle", TgiFaultCode.INVALID_ID)
    val = cd.clock_pulse_offset
    return None if val is None else get_handle(val)


def getClockDriverClockPulseValue(clockDriverID: str) -> int | None:
    """Return numeric bit value of ``clockPulseValue``.

    Section: F.7.41.10.
    """
    cd = _resolve_clock_driver(clockDriverID)
    if cd is None:
        raise TgiError("Invalid clockDriver handle", TgiFaultCode.INVALID_ID)
    val = cd.clock_pulse_value
    return None if val is None else getattr(val, "value", None)


def getClockDriverClockPulseValueExpression(clockDriverID: str) -> str | None:
    """Return expression of ``clockPulseValue``.

    Section: F.7.41.11.
    """
    cd = _resolve_clock_driver(clockDriverID)
    if cd is None:
        raise TgiError("Invalid clockDriver handle", TgiFaultCode.INVALID_ID)
    val = cd.clock_pulse_value
    return None if val is None else getattr(val, "expression", None)


def getClockDriverClockPulseValueID(clockDriverID: str) -> str | None:
    """Return handle of ``clockPulseValue`` element.

    Section: F.7.41.12.
    """
    cd = _resolve_clock_driver(clockDriverID)
    if cd is None:
        raise TgiError("Invalid clockDriver handle", TgiFaultCode.INVALID_ID)
    val = cd.clock_pulse_value
    return None if val is None else get_handle(val)


def getDriverClockDriverID(driverID: str) -> str | None:
    """Return handle of ``clockDriver`` child of a driver.

    Section: F.7.41.13.
    """
    d = _resolve_driver(driverID)
    if d is None:
        raise TgiError("Invalid driver handle", TgiFaultCode.INVALID_ID)
    cd = d.clock_driver
    return None if cd is None else get_handle(cd)


def getDriverDefaultValue(driverID: str) -> int | str | None:
    """Return defaultValue numeric or string value.

    Section: F.7.41.14.
    """
    d = _resolve_driver(driverID)
    if d is None:
        raise TgiError("Invalid driver handle", TgiFaultCode.INVALID_ID)
    dv = d.default_value
    return None if dv is None else getattr(dv, "value", None)


def getDriverDefaultValueExpression(driverID: str) -> str | None:
    """Return expression of defaultValue.

    Section: F.7.41.15.
    """
    d = _resolve_driver(driverID)
    if d is None:
        raise TgiError("Invalid driver handle", TgiFaultCode.INVALID_ID)
    dv = d.default_value
    return None if dv is None else getattr(dv, "expression", None)


def getDriverDefaultValueID(driverID: str) -> str | None:
    """Return handle of defaultValue element.

    Section: F.7.41.16.
    """
    d = _resolve_driver(driverID)
    if d is None:
        raise TgiError("Invalid driver handle", TgiFaultCode.INVALID_ID)
    dv = d.default_value
    return None if dv is None else get_handle(dv)


def getDriverLeftID(driverID: str) -> str | None:
    """Return handle of range.left.

    Section: F.7.41.17.
    """
    d = _resolve_driver(driverID)
    if d is None:
        raise TgiError("Invalid driver handle", TgiFaultCode.INVALID_ID)
    rng = d.range
    if rng is None or rng.left is None:
        return None
    return get_handle(rng.left)


def getDriverRange(driverID: str) -> tuple[int | None, int | None]:
    """Return (leftValue, rightValue) of range.

    Section: F.7.41.18.
    """
    d = _resolve_driver(driverID)
    if d is None:
        raise TgiError("Invalid driver handle", TgiFaultCode.INVALID_ID)
    rng = d.range
    if rng is None:
        return (None, None)
    left_v = getattr(rng.left, "value", None) if rng.left is not None else None
    right_v = getattr(rng.right, "value", None) if rng.right is not None else None
    return (left_v, right_v)


def getDriverRangeExpression(driverID: str) -> tuple[str | None, str | None]:
    """Return (leftExpression, rightExpression) of range.

    Section: F.7.41.19.
    """
    d = _resolve_driver(driverID)
    if d is None:
        raise TgiError("Invalid driver handle", TgiFaultCode.INVALID_ID)
    rng = d.range
    if rng is None:
        return (None, None)
    left_e = getattr(rng.left, "expression", None) if rng.left is not None else None
    right_e = getattr(rng.right, "expression", None) if rng.right is not None else None
    return (left_e, right_e)


def getDriverRightID(driverID: str) -> str | None:
    """Return handle of range.right.

    Section: F.7.41.20.
    """
    d = _resolve_driver(driverID)
    if d is None:
        raise TgiError("Invalid driver handle", TgiFaultCode.INVALID_ID)
    rng = d.range
    if rng is None or rng.right is None:
        return None
    return get_handle(rng.right)


# ---------------------------------------------------------------------------
# EXTENDED (F.7.42)
# ---------------------------------------------------------------------------

def addDriverSingleShotDriver(driverID: str) -> str:
    """Create singleShotDriver (empty skeleton) if absent and return handle.

    Section: F.7.42.1.
    """
    d = _resolve_driver(driverID)
    if d is None:
        raise TgiError("Invalid driver handle", TgiFaultCode.INVALID_ID)
    ssd = _ensure_single_shot(d)
    return get_handle(ssd)


def addDriverViewRef(driverID: str, viewRef: str) -> str:
    """Append a ``viewRef`` value reference and return its handle.

    Section: F.7.42.2.
    """
    d = _resolve_driver(driverID)
    if d is None:
        raise TgiError("Invalid driver handle", TgiFaultCode.INVALID_ID)
    vr = DriverType.ViewRef(value=viewRef)
    d.view_ref.append(vr)  # type: ignore[attr-defined]
    register_parent(vr, d, ("view_ref",), "list")
    return get_handle(vr)


def removeDriverClockDriver(clockDriverID: str) -> bool:
    """Remove the clockDriver element.

    Section: F.7.42.3.
    """
    cd = _resolve_clock_driver(clockDriverID)
    if cd is None:
        return False
    return detach_child_by_handle(clockDriverID)


def removeDriverRange(driverID: str) -> bool:
    """Remove the range child of a driver.

    Section: F.7.42.4.
    """
    d = _resolve_driver(driverID)
    if d is None:
        raise TgiError("Invalid driver handle", TgiFaultCode.INVALID_ID)
    if d.range is None:
        return False
    d.range = None
    return True


def removeDriverSingleShotDriver(singleShotDriverID: str) -> bool:
    """Remove the singleShotDriver element.

    Section: F.7.42.5.
    """
    ssd = _resolve_single_shot(singleShotDriverID)
    if ssd is None:
        return False
    return detach_child_by_handle(singleShotDriverID)


def removeDriverViewRef(viewRefID: str) -> bool:
    """Remove a viewRef entry.

    Section: F.7.42.6.
    """
    obj = resolve_handle(viewRefID)
    if not isinstance(obj, DriverType.ViewRef):  # type: ignore[attr-defined]
        return False
    return detach_child_by_handle(viewRefID)


def setClockDriverClockPeriod(clockDriverID: str, value: float, expression: str | None = None) -> bool:
    """Set clockPeriod value/expression of an existing clockDriver.

    Section: F.7.42.7.
    """
    cd = _resolve_clock_driver(clockDriverID)
    if cd is None:
        raise TgiError("Invalid clockDriver handle", TgiFaultCode.INVALID_ID)
    if cd.clock_period is None:
        cd.clock_period = ClockDriverType.ClockPeriod()
    cd.clock_period.value = value  # type: ignore[attr-defined]
    if expression is not None:
        cd.clock_period.expression = expression  # type: ignore[attr-defined]
    return True


def setClockDriverClockPulseDuration(clockDriverID: str, value: float, expression: str | None = None) -> bool:
    """Set clockPulseDuration fields.

    Section: F.7.42.8.
    """
    cd = _resolve_clock_driver(clockDriverID)
    if cd is None:
        raise TgiError("Invalid clockDriver handle", TgiFaultCode.INVALID_ID)
    if cd.clock_pulse_duration is None:
        cd.clock_pulse_duration = ClockDriverType.ClockPulseDuration()
    cd.clock_pulse_duration.value = value  # type: ignore[attr-defined]
    if expression is not None:
        cd.clock_pulse_duration.expression = expression  # type: ignore[attr-defined]
    return True


def setClockDriverClockPulseOffset(clockDriverID: str, value: float, expression: str | None = None) -> bool:
    """Set clockPulseOffset fields.

    Section: F.7.42.9.
    """
    cd = _resolve_clock_driver(clockDriverID)
    if cd is None:
        raise TgiError("Invalid clockDriver handle", TgiFaultCode.INVALID_ID)
    if cd.clock_pulse_offset is None:
        cd.clock_pulse_offset = ClockDriverType.ClockPulseOffset()
    cd.clock_pulse_offset.value = value  # type: ignore[attr-defined]
    if expression is not None:
        cd.clock_pulse_offset.expression = expression  # type: ignore[attr-defined]
    return True


def setClockDriverClockPulseValue(clockDriverID: str, value: int, expression: str | None = None) -> bool:
    """Set clockPulseValue fields.

    Section: F.7.42.10.
    """
    cd = _resolve_clock_driver(clockDriverID)
    if cd is None:
        raise TgiError("Invalid clockDriver handle", TgiFaultCode.INVALID_ID)
    # UnsignedBitExpression imported inside to avoid circular imports if any
    from org.accellera.ipxact.v1685_2022.unsigned_bit_expression import UnsignedBitExpression

    ub = cd.clock_pulse_value
    if ub is None:
        ub = UnsignedBitExpression()
        cd.clock_pulse_value = ub
        register_parent(ub, cd, ("clock_pulse_value",), "single")
    ub.value = value  # type: ignore[attr-defined]
    if expression is not None:
        ub.expression = expression  # type: ignore[attr-defined]
    return True


def setDriverClockDriver(driverID: str) -> str:
    """Ensure clockDriver exists (creating if necessary) and return its handle.

    Section: F.7.42.11.
    """
    d = _resolve_driver(driverID)
    if d is None:
        raise TgiError("Invalid driver handle", TgiFaultCode.INVALID_ID)
    cd = _ensure_clock(d)
    return get_handle(cd)


def setDriverSingleShotDriver(driverID: str) -> str:
    """Ensure singleShotDriver exists and return its handle.

    Section: F.7.42.12.
    """
    d = _resolve_driver(driverID)
    if d is None:
        raise TgiError("Invalid driver handle", TgiFaultCode.INVALID_ID)
    ssd = _ensure_single_shot(d)
    return get_handle(ssd)


def setDriverDefaultValue(driverID: str, value: int | str, expression: str | None = None) -> bool:
    """Set defaultValue contents (creating element if missing).

    Section: F.7.42.13.
    """
    d = _resolve_driver(driverID)
    if d is None:
        raise TgiError("Invalid driver handle", TgiFaultCode.INVALID_ID)
    dv = d.default_value
    if dv is None:
        dv = DefaultValue()
        d.default_value = dv
        register_parent(dv, d, ("default_value",), "single")
    dv.value = value  # type: ignore[attr-defined]
    if expression is not None:
        dv.expression = expression  # type: ignore[attr-defined]
    return True


def setDriverRange(
    driverID: str,
    leftValue: int,
    rightValue: int,
    leftExpression: str | None = None,
    rightExpression: str | None = None,
) -> bool:
    """Set range bounds creating range if required.

    Section: F.7.42.14.
    """
    d = _resolve_driver(driverID)
    if d is None:
        raise TgiError("Invalid driver handle", TgiFaultCode.INVALID_ID)
    rng = d.range
    if rng is None:
        rng = RangeClass(left=Left(), right=Right())
        d.range = rng
        register_parent(rng, d, ("range",), "single")
    if rng.left is None:
        rng.left = Left()
    if rng.right is None:
        rng.right = Right()
    rng.left.value = leftValue  # type: ignore[attr-defined]
    rng.right.value = rightValue  # type: ignore[attr-defined]
    if leftExpression is not None:
        rng.left.expression = leftExpression  # type: ignore[attr-defined]
    if rightExpression is not None:
        rng.right.expression = rightExpression  # type: ignore[attr-defined]
    return True


def setOtherClockDriverClockPeriod(driverID: str, value: float, expression: str | None = None) -> bool:
    """Create/ensure clockDriver then set clockPeriod.

    Section: F.7.42.15.
    """
    d = _resolve_driver(driverID)
    if d is None:
        raise TgiError("Invalid driver handle", TgiFaultCode.INVALID_ID)
    cd = _ensure_clock(d)
    return setClockDriverClockPeriod(get_handle(cd), value, expression)


def setOtherClockDriverClockPulseDuration(driverID: str, value: float, expression: str | None = None) -> bool:
    """Ensure clockDriver then set clockPulseDuration.

    Section: F.7.42.16.
    """
    d = _resolve_driver(driverID)
    if d is None:
        raise TgiError("Invalid driver handle", TgiFaultCode.INVALID_ID)
    cd = _ensure_clock(d)
    return setClockDriverClockPulseDuration(get_handle(cd), value, expression)


def setOtherClockDriverClockPulseOffset(driverID: str, value: float, expression: str | None = None) -> bool:
    """Ensure clockDriver then set clockPulseOffset.

    Section: F.7.42.17.
    """
    d = _resolve_driver(driverID)
    if d is None:
        raise TgiError("Invalid driver handle", TgiFaultCode.INVALID_ID)
    cd = _ensure_clock(d)
    return setClockDriverClockPulseOffset(get_handle(cd), value, expression)


def setOtherClockDriverClockPulseValue(driverID: str, value: int, expression: str | None = None) -> bool:
    """Ensure clockDriver then set clockPulseValue.

    Section: F.7.42.18.
    """
    d = _resolve_driver(driverID)
    if d is None:
        raise TgiError("Invalid driver handle", TgiFaultCode.INVALID_ID)
    cd = _ensure_clock(d)
    return setClockDriverClockPulseValue(get_handle(cd), value, expression)


def setSingleShotDriverSingleShotDuration(singleShotDriverID: str, value: float, expression: str | None = None) -> bool:
    """Set duration field of an existing singleShotDriver.

    Section: F.7.42.19.
    """
    ssd = _resolve_single_shot(singleShotDriverID)
    if ssd is None:
        raise TgiError("Invalid singleShotDriver handle", TgiFaultCode.INVALID_ID)
    if ssd.single_shot_duration is None:
        ssd.single_shot_duration = SingleShotDriverClass.SingleShotDuration()
    ssd.single_shot_duration.value = value  # type: ignore[attr-defined]
    if expression is not None:
        ssd.single_shot_duration.expression = expression  # type: ignore[attr-defined]
    return True


def setSingleShotDriverSingleShotOffset(singleShotDriverID: str, value: float, expression: str | None = None) -> bool:
    """Set offset field of an existing singleShotDriver.

    Section: F.7.42.20.
    """
    ssd = _resolve_single_shot(singleShotDriverID)
    if ssd is None:
        raise TgiError("Invalid singleShotDriver handle", TgiFaultCode.INVALID_ID)
    if ssd.single_shot_offset is None:
        ssd.single_shot_offset = SingleShotDriverClass.SingleShotOffset()
    ssd.single_shot_offset.value = value  # type: ignore[attr-defined]
    if expression is not None:
        ssd.single_shot_offset.expression = expression  # type: ignore[attr-defined]
    return True

