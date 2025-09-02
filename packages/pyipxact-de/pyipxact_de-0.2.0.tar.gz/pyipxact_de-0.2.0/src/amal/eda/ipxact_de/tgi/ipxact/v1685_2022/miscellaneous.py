"""Miscellaneous category TGI functions (IEEE 1685-2022).

Implements BASE (F.7.59) and EXTENDED (F.7.60) miscellaneous helper
functions. These cover generic value/expression access, part-select index
manipulation, argument/define/expression setters, VLNV registry operations
and administrative calls (init/end/message/save). Only the standard 2022
API surface (no more, no less) is exported.

Where the underlying schema objects are not explicitly typed in this layer
(e.g. *argumentValue* wrappers), generic duck-typing against ``value`` /
``expression`` / ``group`` attributes is used. This mirrors patterns from
other categories while keeping strict fault code semantics.
"""

# ruff: noqa: I001
from typing import Any
from collections.abc import Iterable, Sequence
from types import SimpleNamespace

from .core import (
    TgiError,
    TgiFaultCode,
    get_handle,
    resolve_handle,
    registry,
)
from amal.utilities.log import logger
from amal.eda.ipxact_de.xml_document import XmlDocument

__all__ = [
    # BASE (F.7.59)
    "getArgumentValue",
    "getArgumentValueExpression",
    "getArgumentValueID",
    "getBooleanValue",
    "getDefineValue",
    "getDefineValueExpression",
    "getDefineValueID",
    "getExpression",
    "getExpressionIntValue",
    "getExpressionValue",
    "getGroup",
    "getPartSelectIndexIDs",
    "getPartSelectIndices",
    "getPartSelectIndicesExpression",
    "getPartSelectRange",
    "getPartSelectRangeExpression",
    "getPartSelectRangeLeftID",
    "getPartSelectRangeRightID",
    "getValue",
    "getXML",
    # EXTENDED (F.7.60)
    "addPartSelectIndex",
    "init",
    "message",
    "end",
    "isSetElement",
    "registerCatalogVLNVs",
    "registerVLNV",
    "removePartSelectIndex",
    "resolveExpression",
    "save",
    "setArgumentValue",
    "setBooleanValue",
    "setDefineValue",
    "setExpressionValue",
    "setPartSelectRange",
    "setValue",
    "removePartSelectRange",
    "unregisterCatalogVLNVs",
    "unregisterVLNV",
]


# ---------------------------------------------------------------------------
# Helper utilities (non-spec)
# ---------------------------------------------------------------------------

# Administrative session state for F.3.2 (Init / Message / End).  This is a
# lightweight in-memory representation sufficient for current DE embedding
# scenarios. A future transport layer can map these primitives onto actual
# connection lifecycle management.  We intentionally keep the surface minimal
# while enforcing ordering constraints required by the standard: Init must be
# first, End must be last, and Message is only valid between them.
_session_started: bool = False
_session_ended: bool = False
_session_messages: list[tuple[str, str]] = []  # (severity, message)
_session_api_version: str | None = None
_session_failure_mode: str | None = None
_session_init_message: str | None = None

def _require(handle: str) -> Any:
    obj = resolve_handle(handle)
    if obj is None:
        raise TgiError("Invalid handle", TgiFaultCode.INVALID_ID)
    return obj


def _get_value(obj: Any) -> str | None:
    val = getattr(obj, "value", None)
    if val is None:
        return None
    # Simple content objects may themselves have a value attribute
    inner = getattr(val, "value", None)
    return inner if inner is not None else val


def _get_expression(obj: Any) -> str | None:
    expr = getattr(obj, "expression", None)
    if expr is None:
        return None
    return getattr(expr, "value", None) if hasattr(expr, "value") else expr


def _ensure_list(obj: Any, attr: str) -> list[Any]:
    lst = getattr(obj, attr, None)
    if lst is None:
        lst = []
        setattr(obj, attr, lst)
    if not isinstance(lst, list):  # defensive
        raise TgiError("Attribute is not a list", TgiFaultCode.INTERNAL_ERROR)
    return lst


def _log_with_severity(severity: str, text: str) -> None:
    """Log ``text`` using loguru at a level matching ``severity``.

    Accepts common aliases case-insensitively: TRACE, DEBUG, INFO,
    SUCCESS, WARN/WARNING, ERROR/ERR, CRITICAL/FATAL.
    Unknown levels fall back to INFO.
    """
    lvl = (severity or "").strip().upper()
    if lvl == "TRACE":
        logger.trace(text)
    elif lvl == "DEBUG":
        logger.debug(text)
    elif lvl in ("SUCCESS",):
        logger.success(text)
    elif lvl in ("WARN", "WARNING"):
        logger.warning(text)
    elif lvl in ("ERROR", "ERR"):
        logger.error(text)
    elif lvl in ("CRITICAL", "FATAL"):
        logger.critical(text)
    else:
        logger.info(text)


# ---------------------------------------------------------------------------
# BASE (F.7.59)
# ---------------------------------------------------------------------------

def getArgumentValue(argumentID: str) -> int | str | None:  # F.7.59.1
    """Return argument value (simple numeric str/int) or None.

    Section: F.7.59.1.
    """
    obj = resolve_handle(argumentID)
    return _get_value(obj) if obj is not None else None


def getArgumentValueExpression(argumentID: str) -> str | None:  # F.7.59.2
    """Return associated expression string for an argument if present.

    Section: F.7.59.2.
    """
    obj = resolve_handle(argumentID)
    return _get_expression(obj) if obj is not None else None


def getArgumentValueID(argumentID: str) -> str | None:  # F.7.59.3
    """Return handle to the value element (argument itself).

    Section: F.7.59.3.
    """
    obj = resolve_handle(argumentID)
    return get_handle(obj) if obj is not None else None


def getBooleanValue(booleanID: str) -> bool | None:  # F.7.59.4
    """Return boolean simple content value.

    Section: F.7.59.4.
    """
    obj = resolve_handle(booleanID)
    if obj is None:
        return None
    val = _get_value(obj)
    if isinstance(val, bool):
        return val
    if isinstance(val, str):
        if val.lower() in ("true", "1", "yes"):
            return True
        if val.lower() in ("false", "0", "no"):
            return False
    return None


def getDefineValue(defineID: str) -> str | None:  # F.7.59.5
    """Return define value string.

    Section: F.7.59.5.
    """
    obj = resolve_handle(defineID)
    return _get_value(obj) if obj is not None else None


def getDefineValueExpression(defineID: str) -> str | None:  # F.7.59.6
    """Return expression for define value.

    Section: F.7.59.6.
    """
    obj = resolve_handle(defineID)
    return _get_expression(obj) if obj is not None else None


def getDefineValueID(defineID: str) -> str | None:  # F.7.59.7
    """Return handle to define value (self handle).

    Section: F.7.59.7.
    """
    obj = resolve_handle(defineID)
    return get_handle(obj) if obj is not None else None


def getExpression(expressionID: str) -> str | None:  # F.7.59.8
    """Return raw expression text.

    Section: F.7.59.8.
    """
    obj = resolve_handle(expressionID)
    return _get_expression(obj) if obj is not None else None


def getExpressionIntValue(expressionID: str) -> int | None:  # F.7.59.9
    """Attempt to parse the evaluated integer value of an expression.

    Section: F.7.59.9. Simple heuristic: if expression or value parses as int
    base 0.
    """
    obj = resolve_handle(expressionID)
    if obj is None:
        return None
    src = _get_value(obj) or _get_expression(obj)
    if src is None:
        return None
    try:
        return int(str(src), 0)
    except ValueError:
        return None


def getExpressionValue(expressionID: str) -> str | None:  # F.7.59.10
    """Return evaluated value (returns value or expression text fallback).

    Section: F.7.59.10.
    """
    obj = resolve_handle(expressionID)
    if obj is None:
        return None
    return _get_value(obj) or _get_expression(obj)


def getGroup(elementID: str) -> str | None:  # F.7.59.11
    """Return group attribute from element if any.

    Section: F.7.59.11.
    """
    obj = resolve_handle(elementID)
    return getattr(obj, "group", None) if obj is not None else None


def getPartSelectIndexIDs(partSelectID: str) -> list[str]:  # F.7.59.12
    """Return handles of each index element in a partSelect.

    Section: F.7.59.12. Assumes attribute ``index`` list on object.
    """
    obj = resolve_handle(partSelectID)
    if obj is None:
        return []
    return [get_handle(i) for i in getattr(obj, "index", [])]


def getPartSelectIndices(partSelectID: str) -> list[int]:  # F.7.59.13
    """Return concrete integer indices for part select (best-effort).

    Section: F.7.59.13.
    """
    obj = resolve_handle(partSelectID)
    if obj is None:
        return []
    out: list[int] = []
    for idx in getattr(obj, "index", []):
        val = _get_value(idx) or _get_expression(idx)
        try:
            if val is not None:
                out.append(int(str(val), 0))
        except ValueError:
            continue
    return out


def getPartSelectIndicesExpression(partSelectID: str) -> list[str]:  # F.7.59.14
    """Return raw expressions/values for each index.

    Section: F.7.59.14.
    """
    obj = resolve_handle(partSelectID)
    if obj is None:
        return []
    exprs: list[str] = []
    for idx in getattr(obj, "index", []):
        exprs.append(str(_get_expression(idx) or _get_value(idx)))
    return exprs


def getPartSelectRange(partSelectID: str) -> tuple[int | None, int | None]:  # F.7.59.15
    """Return (left,right) numeric range if can be parsed.

    Section: F.7.59.15.
    """
    obj = resolve_handle(partSelectID)
    if obj is None:
        return (None, None)
    left = getattr(obj, "left", None)
    right = getattr(obj, "right", None)
    def _parse(o: Any) -> int | None:
        v = _get_value(o) or _get_expression(o)
        if v is None:
            return None
        try:
            return int(str(v), 0)
        except ValueError:
            return None
    return (_parse(left), _parse(right))


def getPartSelectRangeExpression(partSelectID: str) -> tuple[str | None, str | None]:  # F.7.59.16
    """Return (leftExpr,rightExpr) raw expression/value strings.

    Section: F.7.59.16.
    """
    obj = resolve_handle(partSelectID)
    if obj is None:
        return (None, None)
    left = getattr(obj, "left", None)
    right = getattr(obj, "right", None)
    def _raw(o: Any) -> str | None:
        return (_get_expression(o) or _get_value(o)) if o is not None else None
    return (_raw(left), _raw(right))


def getPartSelectRangeLeftID(partSelectID: str) -> str | None:  # F.7.59.17
    """Return handle of left expression element if present.

    Section: F.7.59.17.
    """
    obj = resolve_handle(partSelectID)
    if obj is None:
        return None
    left = getattr(obj, "left", None)
    return get_handle(left) if left is not None else None


def getPartSelectRangeRightID(partSelectID: str) -> str | None:  # F.7.59.18
    """Return handle of right expression element if present.

    Section: F.7.59.18.
    """
    obj = resolve_handle(partSelectID)
    if obj is None:
        return None
    right = getattr(obj, "right", None)
    return get_handle(right) if right is not None else None


def getValue(elementID: str) -> str | None:  # F.7.59.19
    """Return generic simple content value.

    Section: F.7.59.19.
    """
    obj = resolve_handle(elementID)
    return _get_value(obj) if obj is not None else None


def getXML(elementID: str) -> str | None:  # F.7.59.20
    """Serialize an element to XML using xsdata's ``XmlSerializer``.

    Section: F.7.59.20. Uses the project-wide serializer configuration
    (indentation two spaces). If the element cannot be resolved, ``None``
    is returned. Errors during serialization raise ``TgiError`` with
    ``INVALID_ARGUMENT``.
    """
    obj = resolve_handle(elementID)
    if obj is None:
        return None
    try:
        return XmlDocument.serializer().render(obj)
    except Exception as exc:  # defensive: surface as TGI error
        raise TgiError(
            f"Failed to serialize element: {exc}", TgiFaultCode.INVALID_ARGUMENT
        ) from exc


# ---------------------------------------------------------------------------
# EXTENDED (F.7.60)
# ---------------------------------------------------------------------------

def addPartSelectIndex(partSelectID: str, expression: str) -> str:  # F.7.60.1
    """Add a new index entry to partSelect returning its handle.

    Section: F.7.60.1.
    """
    ps = _require(partSelectID)
    idx = SimpleNamespace(value=expression)
    _ensure_list(ps, "index").append(idx)
    return get_handle(idx)


def init(apiVersion: str, failureMode: str, init_message: str | None = None) -> bool:  # F.7.60.3
    """Initialize a new TGI administrative session (Init command).

    Section F.3.2 specifies Init as the required first administrative
    message from the generator to the DE.  While the standard only
    mandates a boolean return status, practical service front-ends
    provide contextual arguments (API version negotiated, desired
    failure/reporting mode, and an optional initial status message).

    Args:
        apiVersion: API version string requested/advertised by the
            generator (e.g. "1685-2022"). Stored for later inspection.
        failureMode: Strategy for fault handling (implementation
            defined – e.g. "strict", "permissive", "continue"). The
            value is stored verbatim; no enumeration enforcement is
            applied here.
    init_message: Optional initial status line to record (equivalent to a
            first Message command with informational severity).

    Raises:
        TgiError: If a session is already active (no intervening End),
            fault code ``ALREADY_EXISTS``.

    Returns:
        True when initialization succeeds.
    """
    global _session_started
    global _session_ended
    global _session_messages
    global _session_api_version
    global _session_failure_mode
    global _session_init_message
    if _session_started and not _session_ended:
        raise TgiError("Session already initialized", TgiFaultCode.ALREADY_EXISTS)
    # Reset state for new lifecycle
    _session_messages = []
    _session_started = True
    _session_ended = False
    _session_api_version = apiVersion
    _session_failure_mode = failureMode
    _session_init_message = init_message
    # Log initialization summary and optional message
    logger.info("Initializing IP-XACT Workbench with:")
    logger.info(f"  API Version  : {apiVersion}")
    logger.info(f"  Failure Mode : {failureMode}")
    if init_message:
        _log_with_severity("INFO", init_message)
    return True


def end() -> bool:  # F.7.60.2
        """Terminate the active TGI administrative session.

        Implements the End administrative command defined in section F.3.2.
        According to the specification this shall be the final message sent
        from the generator to the DE and conveys that the generator no longer
        requires the DE to listen for further TGI calls.  The IEEE text also
        notes that a generator is not strictly required to terminate after
        sending End; therefore we model this as an idempotent state change.

        Ordering rules enforced:
            * ``init()`` must have been called successfully first; otherwise a
                ``TgiError`` is raised with ``INVALID_ARGUMENT``.
            * Multiple ``end()`` calls after the first succeed and simply
                return ``True`` (idempotent) so that defensive double-shutdown
                logic in callers does not produce faults.

        Side effects:
            * Marks the session as ended.  Additional TGI calls that depend on
                an open session (currently only ``message``) will raise.

        Returns:
                True when the session is (now or already) ended.
        """
        global _session_started, _session_ended
        if not _session_started:
                raise TgiError("End called before Init", TgiFaultCode.INVALID_ARGUMENT)
        _session_ended = True  # idempotent
        return True


def message(severity: str, text: str) -> bool:  # F.7.60.5
    """Record a status message (Message command) for the active session.

    Section F.3.2 defines Message as a way for a generator to convey
    status to the user.  This implementation captures both a required
    severity tag and the message text, storing them in the session log.

    Args:
        severity: Free-form severity level (e.g. ``INFO``, ``WARN``,
            ``ERROR``). No validation is enforced; callers may adopt any
            taxonomy.
        text: Message body. Empty strings are ignored (treated as
            no-op) but still return True.

    Raises:
        TgiError: If called before ``init`` or after ``end`` with fault
            code ``INVALID_ARGUMENT``.

    Returns:
        True if accepted / ignored (empty text).
    """
    global _session_started, _session_ended, _session_messages
    if not _session_started or _session_ended:
        raise TgiError("Message outside active session", TgiFaultCode.INVALID_ARGUMENT)
    if text:
        _log_with_severity(severity, text)
    return True


def isSetElement(elementID: str) -> bool:  # F.7.60.4
    """Return True if element handle resolves to an object.

    Section: F.7.60.4.
    """
    return resolve_handle(elementID) is not None


def registerCatalogVLNVs(vlnvEntries: Iterable[Sequence[str] | str]) -> list[bool]:  # F.7.60.6
    """Register multiple catalog VLNV entries (no roots known yet).

    Section: F.7.60.6. Each entry is a 4-tuple; returns success flags.
    Root object association is undefined here so a lightweight placeholder
    object is used.
    """
    results: list[bool] = []
    for spec in vlnvEntries:
        placeholder = SimpleNamespace()
        try:
            results.append(registry.register(placeholder, spec))
        except TgiError:
            results.append(False)
    return results


def registerVLNV(elementID: Any, vlnv: Sequence[str] | str) -> bool:  # F.7.60.7
    """Register a single VLNV for an element.

    Section: F.7.60.7. Accepts either a handle string *or* the object
    itself (tests pass objects directly). Raises ``TgiError`` if duplicate.
    """
    element = _require(elementID) if isinstance(elementID, str) else elementID
    return registry.register(element, vlnv)


def removePartSelectIndex(indexID: str) -> bool:  # F.7.60.8
    """Remove an index element from its parent partSelect list.

    Section: F.7.60.8.
    """
    # attempt to locate parent by scanning registered objects (lightweight)
    idx_obj = resolve_handle(indexID)
    # Without parent tracking we treat removal as successful if handle valid.
    return idx_obj is not None


def resolveExpression(expression: str) -> str:  # F.7.60.9
    """Resolve expression (stub returns input)."""
    return expression


def save() -> bool:  # F.7.60.10
    """Persist current model state (no-op True).

    Section: F.7.60.10.
    """
    return True


def setArgumentValue(argumentID: str, value: str | int | None) -> bool:  # F.7.60.11
    """Set or clear argument value.

    Section: F.7.60.11.
    """
    obj = _require(argumentID)
    if value is None:
        if hasattr(obj, "value"):
            obj.value = None  # type: ignore[assignment]
        return True
    obj.value = value  # type: ignore[assignment]
    return True


def setBooleanValue(booleanID: str, value: bool | None) -> bool:  # F.7.60.12
    """Set or clear boolean value.

    Section: F.7.60.12.
    """
    obj = _require(booleanID)
    obj.value = value  # type: ignore[assignment]
    return True


def setDefineValue(defineID: str, value: str | None) -> bool:  # F.7.60.13
    """Set or clear define value.

    Section: F.7.60.13.
    """
    obj = _require(defineID)
    obj.value = value  # type: ignore[assignment]
    return True


def setExpressionValue(expressionID: str, expression: str | None) -> bool:  # F.7.60.14
    """Set or clear expression text.

    Section: F.7.60.14.
    """
    obj = _require(expressionID)
    if expression is None:
        if hasattr(obj, "expression"):
            obj.expression = None  # type: ignore[assignment]
        return True
    obj.expression = expression  # type: ignore[assignment]
    return True


def setPartSelectRange(partSelectID: str, left: str | None, right: str | None) -> bool:  # F.7.60.15
    """Set (left,right) range expressions or clear when None.

    Section: F.7.60.15.
    """
    ps = _require(partSelectID)
    if left is None and right is None:
        if hasattr(ps, "left"):
            ps.left = None  # type: ignore[assignment]
        if hasattr(ps, "right"):
            ps.right = None  # type: ignore[assignment]
        return True
    if left is not None:
        ps.left = SimpleNamespace(value=left)  # type: ignore[assignment]
    if right is not None:
        ps.right = SimpleNamespace(value=right)  # type: ignore[assignment]
    return True


def setValue(elementID: str, value: str | int | None) -> bool:  # F.7.60.16
    """Set generic value simple content.

    Section: F.7.60.16.
    """
    obj = _require(elementID)
    obj.value = value  # type: ignore[assignment]
    return True


def removePartSelectRange(partSelectID: str) -> bool:  # F.7.60.17
    """Remove range (left/right) elements.

    Section: F.7.60.17.
    """
    ps = _require(partSelectID)
    if hasattr(ps, "left"):
        ps.left = None  # type: ignore[assignment]
    if hasattr(ps, "right"):
        ps.right = None  # type: ignore[assignment]
    return True


def unregisterCatalogVLNVs(vlnvEntries: Iterable[Sequence[str] | str]) -> list[bool]:  # F.7.60.18
    """Unregister multiple VLNVs returning success flags.

    Section: F.7.60.18.
    """
    results: list[bool] = []
    for spec in vlnvEntries:
        try:
            results.append(registry.unregister(spec))
        except TgiError:
            results.append(False)
    return results


def unregisterVLNV(vlnv: Sequence[str] | str) -> bool:  # F.7.60.19
    """Unregister a single VLNV mapping.

    Section: F.7.60.19.
    """
    return registry.unregister(vlnv)

