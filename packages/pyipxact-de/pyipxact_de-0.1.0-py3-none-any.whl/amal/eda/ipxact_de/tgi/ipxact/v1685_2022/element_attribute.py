"""Element attribute category TGI functions (IEEE 1685-2022).

Implements BASE (F.7.43) and EXTENDED (F.7.44) *Element attribute* functions.

Design goals:
* Provide exact public API surface mandated by Annex F – no extra helpers.
* Keep implementation data-driven to avoid hand-maintaining ~280 functions.
* Maintain uniform error semantics (invalid handles => INVALID_ID, coercion
  failures => INVALID_ARGUMENT) matching other rewritten category modules.

Previous generic helper functions (getElementVendor, getElementLibrary, ...)
have been superseded by the exhaustive spec-defined function set and were
removed intentionally to honor the "no more, no less" requirement. Their
removal is recorded here to retain historical context (project rule: do not
remove comments / commented code) – see version control for prior content.
"""

from collections.abc import Callable
from dataclasses import is_dataclass
from typing import Any

from .core import TgiError, TgiFaultCode, get_handle, resolve_handle

# ---------------------------------------------------------------------------
# BASE getter specification (subset excerpt – full list per spec F.7.43).
# Each tuple: (functionName, attributeName, coerceType, kind)
# kind: 'str' | 'bool' | 'int' | 'float' | 'ref' (return handle of referenced object)
# ---------------------------------------------------------------------------

_BASE_ATTRIBUTE_VALUE_FUNCS: list[tuple[str, str, str, str]] = [
    ("getAddressBlockRefAttribute", "addressBlockRef", "str", "str"),
    ("getAddressBlockRefAttributeByID", "addressBlockRef", "ref", "ref"),
    ("getAddressSpaceRefAttribute", "addressSpaceRef", "str", "str"),
    ("getAddressSpaceRefAttributeByID", "addressSpaceRef", "ref", "ref"),
    ("getAllBitsBooleanAttribute", "allBits", "bool", "bool"),
    ("getAllLogicalDirectionsAllowedBooleanAttribute", "allLogicalDirectionsAllowed", "bool", "bool"),
    ("getAllLogicalInitiativesAllowedBooleanAttribute", "allLogicalInitiativesAllowed", "bool", "bool"),
    ("getAlternateRegisterRefAttribute", "alternateRegisterRef", "str", "str"),
    ("getAlternateRegisterRefAttributeByID", "alternateRegisterRef", "ref", "ref"),
    ("getAppendBooleanAttribute", "append", "bool", "bool"),
    ("getArrayIdAttribute", "arrayId", "str", "str"),
    ("getBankAlignmentAttribute", "bankAlignment", "str", "str"),
    ("getBankRefAttribute", "bankRef", "str", "str"),
    ("getBankRefAttributeByID", "bankRef", "ref", "ref"),
    ("getBusRefAttribute", "busRef", "str", "str"),
    ("getBusRefAttributeByID", "busRef", "ref", "ref"),
    ("getCellStrengthAttribute", "cellStrength", "str", "str"),
    ("getChoiceRefAttribute", "choiceRef", "str", "str"),
    ("getChoiceRefAttributeByID", "choiceRef", "ref", "ref"),
    ("getClockEdgeAttribute", "clockEdge", "str", "str"),
    ("getClockNameAttribute", "clockName", "str", "str"),
    ("getClockSourceAttribute", "clockSource", "str", "str"),
    ("getComponentInstanceRefAttribute", "componentInstanceRef", "str", "str"),
    ("getComponentInstanceRefAttributeByID", "componentInstanceRef", "ref", "ref"),
    ("getComponentRefAttribute", "componentRef", "str", "str"),
    ("getComponentRefAttributeByID", "componentRef", "ref", "ref"),
    ("getConfigGroupsAttribute", "configGroups", "str", "str"),
    ("getConstrainedAttributeValues", "constrained", "str", "str"),
    ("getConstraintSetIdAttribute", "constraintSetId", "str", "str"),
    ("getCustomAttribute", "custom", "str", "str"),
    ("getDataTypeAttribute", "dataType", "str", "str"),
    ("getDataTypeDefinitionAttribute", "dataTypeDefinition", "str", "str"),
    ("getDefaultBooleanAttribute", "default", "bool", "bool"),
    ("getDelayTypeAttribute", "delayType", "str", "str"),
    ("getDirectionAttribute", "direction", "str", "str"),
    ("getDriverTypeAttribute", "driverType", "str", "str"),
    ("getExactBooleanAttribute", "exact", "bool", "bool"),
    ("getExternalDeclarationsBooleanAttribute", "externalDeclarations", "bool", "bool"),
    ("getFieldRefAttribute", "fieldRef", "str", "str"),
    ("getFieldRefAttributeByID", "fieldRef", "ref", "ref"),
    ("getFileIdAttribute", "fileId", "str", "str"),
    ("getFlowTypeAttribute", "flowType", "str", "str"),
    ("getForceBooleanAttribute", "force", "bool", "bool"),
    ("getGroupAttribute", "group", "str", "str"),
    ("getHelpAttribute", "help", "str", "str"),
    ("getHiddenBooleanAttribute", "hidden", "bool", "bool"),
    ("getIdAttribute", "id", "str", "str"),
    ("getImageIdAttribute", "imageId", "str", "str"),
    ("getImageTypeAttribute", "imageType", "str", "str"),
    ("getImplicitBooleanAttribute", "implicit", "bool", "bool"),
    ("getIndexVarAttribute", "indexVar", "str", "str"),
    ("getInitiatorRefAttribute", "initiatorRef", "str", "str"),
    ("getInitiatorRefAttributeByID", "initiatorRef", "ref", "ref"),
    ("getInterfaceModeAttribute", "interfaceMode", "str", "str"),
    ("getInvertAttribute", "invert", "bool", "bool"),
    ("getIsIOBooleanAttribute", "isIO", "bool", "bool"),
    ("getLevelAttribute", "level", "str", "str"),
    ("getLibextAttribute", "libext", "str", "str"),
    ("getLibraryAttribute", "library", "str", "str"),
    ("getMandatoryBooleanAttribute", "mandatory", "bool", "bool"),
    ("getMaximumAttribute", "maximum", "str", "str"),
    ("getMaximumDoubleAttribute", "maximum", "float", "float"),
    ("getMaximumIntAttribute", "maximum", "int", "int"),
    ("getMemoryMapRefAttribute", "memoryMapRef", "str", "str"),
    ("getMemoryMapRefAttributeByID", "memoryMapRef", "ref", "ref"),
    ("getMemoryReMapRefAttributeByID", "memoryReMapRef", "ref", "ref"),
    ("getMemoryRemapRefAttribute", "memoryRemapRef", "str", "str"),
    ("getMinimumAttribute", "minimum", "str", "str"),
    ("getMinimumDoubleAttribute", "minimum", "float", "float"),
    ("getMinimumIntAttribute", "minimum", "int", "int"),
    ("getMisalignmentAllowedBooleanAttribute", "misalignmentAllowed", "bool", "bool"),
    ("getModeRefAttribute", "modeRef", "str", "str"),
    ("getModifyAttribute", "modify", "str", "str"),
    ("getMultipleGroupSelectionOperatorAttribute", "multipleGroupSelectionOperator", "str", "str"),
    ("getNameAttribute", "name", "str", "str"),
    ("getOrderFloatAttribute", "order", "float", "float"),
    ("getOtherAnyAttribute", "otherAny", "str", "str"),
    ("getOtherAttribute", "other", "str", "str"),
    ("getOtherAttributes", "others", "str", "str"),
    ("getPackedBooleanAttribute", "packed", "bool", "bool"),
    ("getParameterIdAttribute", "parameterId", "str", "str"),
    ("getPathAttribute", "path", "str", "str"),
    ("getPhantomBooleanAttribute", "phantom", "bool", "bool"),
    ("getPortRefAttribute", "portRef", "str", "str"),
    ("getPortRefAttributeByID", "portRef", "ref", "ref"),
    ("getPowerDomainRefAttribute", "powerDomainRef", "str", "str"),
    ("getPowerDomainRefAttributeByID", "powerDomainRef", "ref", "ref"),
    ("getPrefixAttribute", "prefix", "str", "str"),
    ("getPriorityIntAttribute", "priority", "int", "int"),
    ("getPromptAttribute", "prompt", "str", "str"),
    ("getReferenceIdAttribute", "referenceId", "str", "str"),
    ("getRegisterFileRefAttribute", "registerFileRef", "str", "str"),
    ("getRegisterFileRefAttributeByID", "registerFileRef", "ref", "ref"),
    ("getRegisterRefAttribute", "registerRef", "str", "str"),
    ("getReplicateBooleanAttribute", "replicate", "bool", "bool"),
    ("getResetTypeRefAttribute", "resetTypeRef", "str", "str"),
    ("getResetTypeRefAttributeByID", "resetTypeRef", "ref", "ref"),
    ("getResolveAttribute", "resolve", "str", "str"),
    ("getScopeAttribute", "scope", "str", "str"),
    ("getSegmentRefAttribute", "segmentRef", "str", "str"),
    ("getSegmentRefAttributeByID", "segmentRef", "ref", "ref"),
    ("getSignAttribute", "sign", "str", "str"),
    ("getStrictBooleanAttribute", "strict", "bool", "bool"),
    ("getSubPortRefAttribute", "subPortRef", "str", "str"),
    ("getSubPortRefAttributeByID", "subPortRef", "ref", "ref"),
    ("getTestConstraintAttribute", "testConstraint", "str", "str"),
    ("getTextAttribute", "text", "str", "str"),
    ("getTypeAttribute", "type", "str", "str"),
    ("getTypeDefinitionsAttribute", "typeDefinitions", "str", "str"),
    ("getUniqueBooleanAttribute", "unique", "bool", "bool"),
    ("getUnitAttribute", "unit", "str", "str"),
    ("getUnitsAttribute", "units", "str", "str"),
    ("getUsageAttribute", "usage", "str", "str"),
    ("getUsageTypeAttribute", "usageType", "str", "str"),
    ("getUserAttribute", "user", "str", "str"),
    ("getVectorIdAttribute", "vectorId", "str", "str"),
    ("getVendorAttribute", "vendor", "str", "str"),
    ("getVersionAttribute", "version", "str", "str"),
    ("getViewRefAttribute", "viewRef", "str", "str"),
    ("getViewRefAttributeByID", "viewRef", "ref", "ref"),
]

# EXTENDED specification (F.7.44). For brevity only attribute name & kind (set/remove).
_EXTENDED_ATTRIBUTE_FUNCS: list[tuple[str, str | None, str | None]] = [
    ("addConstrainedAttribute", "constrained", "add"),
    ("isSetAttribute", None, None),
    ("removeAllBitsAttribute", "allBits", None),
    ("removeAppendAttribute", "append", None),
    ("removeArrayIdAttribute", "arrayId", None),
    ("removeAttribute", None, None),  # generic removal by name
    ("removeCellStrengthAttribute", "cellStrength", None),
    ("removeChoiceRefAttribute", "choiceRef", None),
    ("removeClockEdgeAttribute", "clockEdge", None),
    ("removeClockNameAttribute", "clockName", None),
    ("removeClockSourceAttribute", "clockSource", None),
    ("removeConstrainedAttribute", "constrained", None),
    ("removeConstraintSetIdAttribute", "constraintSetId", None),
    ("removeDataTypeAttribute", "dataType", None),
    ("removeDataTypeDefinitionAttribute", "dataTypeDefinition", None),
    ("removeDefaultAttribute", "default", None),
    ("removeDelayTypeAttribute", "delayType", None),
    ("removeDirectionAttribute", "direction", None),
    ("removeDriverTypeAttribute", "driverType", None),
    ("removeExternalDeclarationsAttribute", "externalDeclarations", None),
    ("removeFileIdAttribute", "fileId", None),
    ("removeFlowTypeAttribute", "flowType", None),
    ("removeForceAttribute", "force", None),
    ("removeGroupAttribute", "group", None),
    ("removeHelpAttribute", "help", None),
    ("removeHiddenAttribute", "hidden", None),
    ("removeIdAttribute", "id", None),
    ("removeImageTypeAttribute", "imageType", None),
    ("removeImplicitAttribute", "implicit", None),
    ("removeInvertAttribute", "invert", None),
    ("removeIsIOAttribute", "isIO", None),
    ("removeLevelAttribute", "level", None),
    ("removeLibextAttribute", "libext", None),
    ("removeMaximumAttribute", "maximum", None),
    ("removeMinimumAttribute", "minimum", None),
    ("removeMisalignmentAllowedAttribute", "misalignmentAllowed", None),
    ("removeModeAttribute", "modeRef", None),
    ("removeModifyAttribute", "modify", None),
    ("removeMultipleGroupSelectionOperatorAttribute", "multipleGroupSelectionOperator", None),
    ("removeOrderAttribute", "order", None),
    ("removeOtherAnyAttribute", "otherAny", None),
    ("removeOtherAttribute", "other", None),
    ("removePackedAttribute", "packed", None),
    ("removeParameterIdAttribute", "parameterId", None),
    ("removePathAttribute", "path", None),
    ("removePhantomAttribute", "phantom", None),
    ("removePowerDomainRefAttribute", "powerDomainRef", None),
    ("removePrefixAttribute", "prefix", None),
    ("removePromptAttribute", "prompt", None),
    ("removeReplicateAttribute", "replicate", None),
    ("removeResetTypeRefAttribute", "resetTypeRef", None),
    ("removeResolveAttribute", "resolve", None),
    ("removeScopeAttribute", "scope", None),
    ("removeSegmentRefAttribute", "segmentRef", None),
    ("removeSignAttribute", "sign", None),
    ("removeStrictAttribute", "strict", None),
    ("removeTestConstraintAttribute", "testConstraint", None),
    ("removeTextAttribute", "text", None),
    ("removeTypeAttribute", "type", None),
    ("removeTypeDefinitionsAttribute", "typeDefinitions", None),
    ("removeUniqueAttribute", "unique", None),
    ("removeUnitAttribute", "unit", None),
    ("removeUnitsAttribute", "units", None),
    ("removeUsageTypeAttribute", "usageType", None),
    ("removeUserAttribute", "user", None),
    ("removeVectorIdAttribute", "vectorId", None),
    # setters
    ("setAddressBlockRefAttribute", "addressBlockRef", "set"),
    ("setAddressSpaceRefAttribute", "addressSpaceRef", "set"),
    ("setAllBitsBooleanAttribute", "allBits", "set"),
    ("setAllLogicalDirectionsAllowedBooleanAttribute", "allLogicalDirectionsAllowed", "set"),
    ("setAllLogicalInitiativesAllowedBooleanAttribute", "allLogicalInitiativesAllowed", "set"),
    ("setAlternateRegisterRefAttribute", "alternateRegisterRef", "set"),
    ("setAppendBooleanAttribute", "append", "set"),
    ("setArrayIdAttribute", "arrayId", "set"),
    ("setBankAlignmentAttribute", "bankAlignment", "set"),
    ("setBankRefAttribute", "bankRef", "set"),
    ("setBusRefAttribute", "busRef", "set"),
    ("setCellStrengthAttribute", "cellStrength", "set"),
    ("setChoiceRefAttribute", "choiceRef", "set"),
    ("setClockEdgeAttribute", "clockEdge", "set"),
    ("setClockNameAttribute", "clockName", "set"),
    ("setClockSourceAttribute", "clockSource", "set"),
    ("setComponentInstanceRefAttribute", "componentInstanceRef", "set"),
    ("setComponentRefAttribute", "componentRef", "set"),
    ("setConfigGroupsAttribute", "configGroups", "set"),
    ("setConstraintSetIdAttribute", "constraintSetId", "set"),
    ("setCustomAttribute", "custom", "set"),
    ("setDataTypeAttribute", "dataType", "set"),
    ("setDataTypeDefinitionAttribute", "dataTypeDefinition", "set"),
    ("setDefaultBooleanAttribute", "default", "set"),
    ("setDelayTypeAttribute", "delayType", "set"),
    ("setDirectionAttribute", "direction", "set"),
    ("setDriverTypeAttribute", "driverType", "set"),
    ("setExactBooleanAttribute", "exact", "set"),
    ("setExternalDeclarationsBooleanAttribute", "externalDeclarations", "set"),
    ("setFieldRefAttribute", "fieldRef", "set"),
    ("setFileIdAttribute", "fileId", "set"),
    ("setFlowTypeAttribute", "flowType", "set"),
    ("setForceBooleanAttribute", "force", "set"),
    ("setGroupAttribute", "group", "set"),
    ("setHelpAttribute", "help", "set"),
    ("setHiddenBooleanAttribute", "hidden", "set"),
    ("setIdAttribute", "id", "set"),
    ("setImageIdAttribute", "imageId", "set"),
    ("setImageTypeAttribute", "imageType", "set"),
    ("setImplicitBooleanAttribute", "implicit", "set"),
    ("setIndexVarAttribute", "indexVar", "set"),
    ("setInitiatorRefAttribute", "initiatorRef", "set"),
    ("setInterfaceModeAttribute", "interfaceMode", "set"),
    ("setInvertAttribute", "invert", "set"),
    ("setIsIOBooleanAttribute", "isIO", "set"),
    ("setLevelAttribute", "level", "set"),
    ("setLibextAttribute", "libext", "set"),
    ("setLibraryAttribute", "library", "set"),
    ("setMandatoryBooleanAttribute", "mandatory", "set"),
    ("setMaximumAttribute", "maximum", "set"),
    ("setMaximumDoubleAttribute", "maximum", "set"),
    ("setMaximumIntAttribute", "maximum", "set"),
    ("setMemoryMapRefAttribute", "memoryMapRef", "set"),
    ("setMemoryRemapRefAttribute", "memoryRemapRef", "set"),
    ("setMinimumAttribute", "minimum", "set"),
    ("setMinimumDoubleAttribute", "minimum", "set"),
    ("setMinimumIntAttribute", "minimum", "set"),
    ("setMisalignmentAllowedBooleanAttribute", "misalignmentAllowed", "set"),
    ("setModeRefAttribute", "modeRef", "set"),
    ("setModifyAttribute", "modify", "set"),
    ("setMultipleGroupSelectionOperatorAttribute", "multipleGroupSelectionOperator", "set"),
    ("setNameAttribute", "name", "set"),
    ("setOrderFloatAttribute", "order", "set"),
    ("setOtherAnyAttribute", "otherAny", "set"),
    ("setOtherAttribute", "other", "set"),
    ("setPackedBooleanAttribute", "packed", "set"),
    ("setParameterIdAttribute", "parameterId", "set"),
    ("setPathAttribute", "path", "set"),
    ("setPhantomBooleanAttribute", "phantom", "set"),
    ("setPortRefAttribute", "portRef", "set"),
    ("setPowerDomainRefAttribute", "powerDomainRef", "set"),
    ("setPrefixAttribute", "prefix", "set"),
    ("setPriorityIntAttribute", "priority", "set"),
    ("setPromptAttribute", "prompt", "set"),
    ("setReferenceIdAttribute", "referenceId", "set"),
    ("setRegisterFileRefAttribute", "registerFileRef", "set"),
    ("setRegisterRefAttribute", "registerRef", "set"),
    ("setReplicateBooleanAttribute", "replicate", "set"),
    ("setResetTypeRefAttribute", "resetTypeRef", "set"),
    ("setResolveAttribute", "resolve", "set"),
    ("setScopeAttribute", "scope", "set"),
    ("setSegmentRefAttribute", "segmentRef", "set"),
    ("setSignAttribute", "sign", "set"),
    ("setStrictBooleanAttribute", "strict", "set"),
    ("setSubPortRefAttribute", "subPortRef", "set"),
    ("setTestConstraintAttribute", "testConstraint", "set"),
    ("setTextAttribute", "text", "set"),
    ("setTypeAttribute", "type", "set"),
    ("setTypeDefinitionsAttribute", "typeDefinitions", "set"),
    ("setUniqueBooleanAttribute", "unique", "set"),
    ("setUnitAttribute", "unit", "set"),
    ("setUnitsAttribute", "units", "set"),
    ("setUsageAttribute", "usage", "set"),
    ("setUsageTypeAttribute", "usageType", "set"),
    ("setUserAttribute", "user", "set"),
    ("setVectorIdAttribute", "vectorId", "set"),
    ("setVendorAttribute", "vendor", "set"),
    ("setVersionAttribute", "version", "set"),
    ("setViewRefAttribute", "viewRef", "set"),
]

__all__: list[str] = [n for n, *_ in _BASE_ATTRIBUTE_VALUE_FUNCS] + [n for n, *_ in _EXTENDED_ATTRIBUTE_FUNCS]


def _resolve(elementID: str) -> Any:
    """Resolve a handle ID to its underlying object.

    Args:
        elementID: Handle identifying an IP-XACT element instance.

    Raises:
        TgiError: With INVALID_ID if the handle is unknown.
    """
    obj = resolve_handle(elementID)
    if obj is None:
        raise TgiError("Invalid element handle", TgiFaultCode.INVALID_ID)
    return obj


def _unwrap(value: Any) -> Any:
    """Return primitive value for generated wrapper dataclasses.

    Many generated classes wrap textual content or simple values inside a
    dataclass that exposes a 'value' attribute. This helper unwraps at most two
    nested levels to arrive at the primitive.
    """
    if value is None:
        return None
    inner = getattr(value, "value", value)
    return getattr(inner, "value", inner)


def _coerce(value: Any, target: str) -> Any:
    """Coerce a raw value into the requested primitive type.

    Args:
        value: Original (possibly string) value.
        target: 'str', 'bool', 'int', 'float'.

    Returns:
        Coerced value or None.

    Raises:
        TgiError: If coercion fails.
    """
    if value is None:
        return None
    try:
        if target == "bool":
            if isinstance(value, bool):
                return value
            if isinstance(value, int | float):
                return bool(value)
            return str(value).lower() in {"1", "true", "yes", "on"}
        if target == "int":
            return int(value)
        if target == "float":
            return float(value)
        return str(value)
    except Exception as exc:  # pragma: no cover - defensive
        raise TgiError(f"Cannot coerce attribute to {target}: {exc}", TgiFaultCode.INVALID_ARGUMENT) from exc


def _define_base_functions() -> None:
    """Create BASE getter functions dynamically to avoid boilerplate."""
    g = globals()
    for func_name, attr_name, rtype, kind in _BASE_ATTRIBUTE_VALUE_FUNCS:
        if func_name in g:  # pragma: no cover - defensive
            continue  # pragma: no cover - should not happen

        def _make(a: str, r: str, k: str, _fn: str) -> Callable[[str], Any]:
            def _getter(elementID: str, *, _attr=a, _rtype=r, _kind=k) -> Any:  # bind loop vars
                """Return the value (or handle) of the specified attribute.

                Section: F.7.43.* (exact subsection per function name).

                Args:
                    elementID: Element handle.

                Returns:
                    Attribute value coerced to the appropriate primitive or
                    handle (for *ByID functions) or None if unset.
                """
                obj = _resolve(elementID)
                raw = getattr(obj, _attr, None)
                if _kind == "ref":
                    return None if raw is None else get_handle(raw)
                value = _unwrap(raw)
                return _coerce(value, _rtype) if _rtype in {"bool", "int", "float", "str"} else value

            _getter.__name__ = _fn
            return _getter

        g[func_name] = _make(attr_name, rtype, kind, func_name)


_define_base_functions()


def _set_attr(obj: Any, attr: str, value: Any) -> None:
    """Assign attribute value on an element (wrapper-aware)."""
    current = getattr(obj, attr, None)
    if current is not None and is_dataclass(current) and hasattr(current, "value"):
        try:
            current.value = value  # type: ignore[attr-defined]
            return
        except Exception:  # pragma: no cover - fallback
            pass
    setattr(obj, attr, value)


def _del_attr(obj: Any, attr: str) -> bool:
    """Clear (set to None) an attribute if present.

    Returns:
        True if the attribute existed and was cleared, else False.
    """
    if not hasattr(obj, attr) or getattr(obj, attr) is None:
        return False
    setattr(obj, attr, None)
    return True


def addConstrainedAttribute(elementID: str, constrained: str) -> bool:  # F.7.44.1
    """Add or replace the 'constrained' attribute.

    Section: F.7.44.1.

    Args:
        elementID: Element handle.
        constrained: Attribute value string.

    Returns:
        True on success.
    """
    obj = _resolve(elementID)
    _set_attr(obj, "constrained", constrained)
    return True


def isSetAttribute(elementID: str, attributeName: str) -> bool:  # F.7.44.2
    """Return True if a named attribute exists and is not None.

    Section: F.7.44.2.

    Args:
        elementID: Element handle.
        attributeName: Raw attribute field name in data model.

    Returns:
        True if set, else False.
    """
    obj = _resolve(elementID)
    return getattr(obj, attributeName, None) is not None


def removeAttribute(elementID: str, attributeName: str) -> bool:  # Generic removal
    """Remove (clear) an arbitrary attribute by name.

    Args:
        elementID: Element handle.
        attributeName: Attribute field name to clear.

    Returns:
        True if removed; False if it was not set.
    """
    obj = _resolve(elementID)
    return _del_attr(obj, attributeName)


# Auto-generate the explicit remove*/set* functions declared in spec.
for fname, attr, _kind in _EXTENDED_ATTRIBUTE_FUNCS:
    if fname in {"addConstrainedAttribute", "isSetAttribute", "removeAttribute"}:
        continue
    if fname.startswith("remove") and attr:
        def _make_remove(a: str, fn: str):
            def _rem(elementID: str) -> bool:
                """Remove attribute if present (spec EXTENDED remove function).

                Args:
                    elementID: Element handle.

                Returns:
                    True if removed; False if absent.
                """
                obj = _resolve(elementID)
                return _del_attr(obj, a)
            _rem.__name__ = fn
            return _rem
        globals()[fname] = _make_remove(attr, fname)
    elif fname.startswith("set") and attr:
        def _make_set(a: str, fn: str):
            def _set(elementID: str, value: Any) -> bool:
                """Set (create or replace) attribute value.

                Args:
                    elementID: Element handle.
                    value: New attribute value.

                Returns:
                    Always True.
                """
                obj = _resolve(elementID)
                _set_attr(obj, a, value)
                return True
            _set.__name__ = fn
            return _set
        globals()[fname] = _make_set(attr, fname)


