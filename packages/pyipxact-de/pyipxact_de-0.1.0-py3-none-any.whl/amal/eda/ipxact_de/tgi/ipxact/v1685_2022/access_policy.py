"""Access policy category TGI functions (IEEE 1685-2022 Annex F).

Implements full BASE and EXTENDED coverage:
* F.7.6: Legacy single getter (kept for continuity).
* F.7.9: 49 BASE traversal / getter functions.
* F.7.10: 49 EXTENDED add/remove/set functions.

Conventions:
* Docstrings start with "Section: F.x.y.z" mirroring the specification numbering.
* Absent optional XML -> None (scalar) or [] (collections).
* Invalid / mismatched handles raise TgiError(TgiFaultCode.INVALID_ID).
* Semantic misuse raises TgiError(TgiFaultCode.INVALID_ARGUMENT).
* Parent/child relationships registered via register_parent; removals delegate to detach_child_by_handle.
* Only specification defined public functions are exported in __all__.

NOTE: Some spec items (e.g. externalTypeDefinitions link) are schema absent in the
generated model; these raise INVALID_ARGUMENT to indicate unsupported elements
rather than silently omitting the API.
"""
from collections.abc import Iterable, Sequence
from typing import Any

from .core import TgiError, TgiFaultCode, detach_child_by_handle, get_handle, register_parent, resolve_handle

__all__: list[str] = [
    # F.7.6
    "getFieldAccessPolicyModeRefByID",
    # F.7.9 (BASE)
    "getAccessPolicyAccess",
    "getAccessPolicyModeRefByID",
    "getAccessPolicyModeRefByNames",
    "getAccessPolicyModeRefIDs",
    "getAccessRestrictionModeRefIDs",
    "getAccessRestrictionModeRefbyID",
    "getAccessRestrictionModeRefbyNames",
    "getAccessRestrictionReadAccessMask",
    "getAccessRestrictionReadAccessMaskExpression",
    "getAccessRestrictionReadAccessMaskID",
    "getAccessRestrictionWriteAccessMask",
    "getAccessRestrictionWriteAccessMaskExpression",
    "getAccessRestrictionWriteAccessMaskID",
    "getAlternateRegisterAccessPolicyIDs",
    "getBankAccessPoliciesIDs",
    "getFieldAccessPoliciesFieldAccessPolicyIDs",
    "getFieldAccessPolicyAccess",
    "getFieldAccessPolicyAccessRestrictionIDs",
    "getFieldAccessPolicyFieldAccessPolicyDefinitionRefByExternalTypeDefID",
    "getFieldAccessPolicyFieldAccessPolicyDefinitionRefByID",
    "getFieldAccessPolicyFieldAccessPolicyDefinitionRefByName",
    "getFieldAccessPolicyFieldAccessPolicyDefinitionRefID",
    "getFieldAccessPolicyModeRefByName",
    "getFieldAccessPolicyModeRefIDs",
    "getFieldAccessPolicyModifiedWriteValue",
    "getFieldAccessPolicyModifiedWriteValueID",
    "getFieldAccessPolicyReadAction",
    "getFieldAccessPolicyReadActionID",
    "getFieldAccessPolicyReadResponse",
    "getFieldAccessPolicyReadResponseExpression",
    "getFieldAccessPolicyReadResponseID",
    "getFieldAccessPolicyReserved",
    "getFieldAccessPolicyReservedExpression",
    "getFieldAccessPolicyReservedID",
    "getFieldAccessPolicyTestable",
    "getFieldAccessPolicyTestableID",
    "getFieldAccessPolicyWriteValueConstraintID",
    "getFieldAccesspolicyBroadcastToIDs",
    "getRegisterAccessPolicyIDs",
    "getRegisterFieldFieldAccessPoliciesID",
    "getTypeDefinitionsFieldAccessPolicyDefinitionIDs",
    "getWriteValueConstraintMaximum",
    "getWriteValueConstraintMaximumExpression",
    "getWriteValueConstraintMaximumID",
    "getWriteValueConstraintMinimum",
    "getWriteValueConstraintMinimumExpression",
    "getWriteValueConstraintMinimumID",
    "getWriteValueConstraintUseEnumeratedValues",
    "getWriteValueConstraintWriteAsRead",
    # FieldAccessPolicyDefinition subset (spec grouped under F.7.9)
    "getFieldAccessPolicyDefinitionIDs",
    "getFieldAccessPolicyDefinitionName",
    "getFieldAccessPolicyDefinitionDisplayName",
    "getFieldAccessPolicyDefinitionShortDescription",
    "getFieldAccessPolicyDefinitionDescription",
    "getFieldAccessPolicyDefinitionAccess",
    "getFieldAccessPolicyDefinitionModifiedWriteValue",
    "getFieldAccessPolicyDefinitionWriteValueConstraint",
    "getFieldAccessPolicyDefinitionReadAction",
    "getFieldAccessPolicyDefinitionReadResponse",
    # F.7.10 (EXTENDED)
    "addAccessRestrictionModeRef",
    "addAddressBlockAccessPolicy",
    "addAlternateRegisterAccessPolicy",
    "addExternalTypeDefinitionsResetTypeLink",
    "addFieldAccessPoliciesFieldAccessPolicy",
    "addFieldAccessPolicyAccessRestriction",
    "addFieldAccessPolicyBroadcastTo",
    "addFieldAccessPolicyModeRef",
    "addFieldDefinitionFieldAccessPolicy",
    "addRegisterAccessPolicy",
    "addRegisterFileAccessPolicy",
    "removeAccessPolicyAccess",
    "removeAccessRestrictionModeRef",
    "removeAccessRestrictionReadAccessMask",
    "removeAccessRestrictionWriteAccessMask",
    "removeAddressBlockAccessPolicyID",
    "removeAlternateRegisterAccessPolicy",
    "removeFieldAccessPoliciesFieldAccessPolicy",
    "removeFieldAccessPolicyAccess",
    "removeFieldAccessPolicyAccessRestriction",
    "removeFieldAccessPolicyBroadcastTo",
    "removeFieldAccessPolicyFieldAccessPolicyDefinitionRef",
    "removeFieldAccessPolicyModeRef",
    "removeFieldAccessPolicyModifiedWriteValue",
    "removeFieldAccessPolicyReadAction",
    "removeFieldAccessPolicyReadResponse",
    "removeFieldAccessPolicyReserved",
    "removeFieldAccessPolicyTestable",
    "removeFieldAccessPolicyWriteValueConstraint",
    "removeFieldDefinitionFieldAccessPolicy",
    "removeRegisterAccessPolicy",
    "removeRegisterFileAccessPolicy",
    "setAccessPolicyAccess",
    "setAccessRestrictionReadAccessMask",
    "setAccessRestrictionWriteAccessMask",
    "setFieldAccessPolicyAccess",
    "setFieldAccessPolicyFieldAccessPolicyDefinitionRef",
    "setFieldAccessPolicyModifiedWriteValue",
    "setFieldAccessPolicyReadAction",
    "setFieldAccessPolicyReadResponse",
    "setFieldAccessPolicyReserved",
    "setFieldAccessPolicyTestable",
    "setFieldAccessPolicyWriteValueConstraintMinMax",
    "setFieldAccessPolicyWriteValueConstraintUseEnumeratedValue",
    "setFieldAccessPolicyWriteValueConstraintWriteAsRead",
    "setWriteValueConstraintMaximum",
    "setWriteValueConstraintMinimum",
    "setWriteValueConstraintUseEnumeratedValues",
    "setWriteValueConstraintWriteAsRead",
]

Numeric = int  # Long numeric expressions represented as Python int / expression string wrappers.


# ---------------------------------------------------------------------------
# Internal helpers (non-spec)
# ---------------------------------------------------------------------------

def _is_definition(obj: Any) -> bool:  # FieldAccessPolicyDefinition heuristic
    return (
        obj is not None
        and hasattr(obj, "modified_write_value")
        and hasattr(obj, "write_value_constraint")
        and not hasattr(obj, "mode_ref")  # inline policies have mode_ref
    )


def _is_inline_field_policy(obj: Any) -> bool:
    return obj is not None and hasattr(obj, "field_access_policy_definition_ref") and hasattr(obj, "mode_ref")


def _definition_container_to_defs(containerID: str) -> list[Any]:
    container = resolve_handle(containerID)
    if container is None or not hasattr(container, "field_access_policy_definition"):
        raise TgiError("Invalid fieldAccessPolicyDefinitions handle", TgiFaultCode.INVALID_ID)
    return list(getattr(container, "field_access_policy_definition", []))


def _ids(iterable: Iterable[Any]) -> list[str]:
    return [get_handle(o) for o in iterable]


def _scalar(obj: Any, attr: str) -> str | None:
    v = getattr(obj, attr, None)
    if v is None:
        return None
    return getattr(v, "value", v)


def _scalar_bool(obj: Any, attr: str) -> bool | None:
    v = getattr(obj, attr, None)
    if v is None:
        return None
    return getattr(v, "value", v)


def _get_access_restrictions(policy: Any) -> list[Any]:
    cont = getattr(policy, "access_restrictions", None)
    if cont is None:
        return []
    return list(getattr(cont, "access_restriction", []))


def _get_write_value_constraint(policy: Any) -> Any | None:
    return getattr(policy, "write_value_constraint", None)


def _get_inline_field_policy(policyID: str) -> Any:
    obj = resolve_handle(policyID)
    if not _is_inline_field_policy(obj):
        raise TgiError("Invalid fieldAccessPolicy handle", TgiFaultCode.INVALID_ID)
    return obj


def _get_access_policy(accessPolicyID: str) -> Any:
    obj = resolve_handle(accessPolicyID)
    if obj is None or not hasattr(obj, "mode_ref") or hasattr(obj, "field_access_policy_definition_ref"):
        raise TgiError("Invalid accessPolicy handle", TgiFaultCode.INVALID_ID)
    return obj


def _get_access_restriction_handle(restrictionID: str) -> Any:
    obj = resolve_handle(restrictionID)
    if obj is None or not hasattr(obj, "read_access_mask") or not hasattr(obj, "mode_ref"):
        raise TgiError("Invalid accessRestriction handle", TgiFaultCode.INVALID_ID)
    return obj


def _get_write_value_constraint_handle(wvcID: str) -> Any:
    obj = resolve_handle(wvcID)
    if obj is None or not hasattr(obj, "minimum") or not hasattr(obj, "maximum"):
        raise TgiError("Invalid writeValueConstraint handle", TgiFaultCode.INVALID_ID)
    return obj


def _first(it: Sequence[Any], pred) -> Any | None:
    for x in it:
        if pred(x):
            return x
    return None


# ---------------------------------------------------------------------------
# FieldAccessPolicyDefinition getters (subset of F.7.9 grouping)
# ---------------------------------------------------------------------------
def getFieldAccessPolicyDefinitionIDs(fieldAccessPolicyDefinitionsID: str) -> list[str]:
    """Section: F.7.9 Return handles of fieldAccessPolicyDefinition children."""
    return _ids(_definition_container_to_defs(fieldAccessPolicyDefinitionsID))


def _get_definition(definitionID: str) -> Any:
    obj = resolve_handle(definitionID)
    if not _is_definition(obj):
        raise TgiError("Invalid FieldAccessPolicyDefinition handle", TgiFaultCode.INVALID_ID)
    return obj


def getFieldAccessPolicyDefinitionName(definitionID: str) -> str | None:
    """Section: F.7.9 Get name of a fieldAccessPolicyDefinition."""
    return _scalar(_get_definition(definitionID), "name")


def getFieldAccessPolicyDefinitionDisplayName(definitionID: str) -> str | None:
    """Section: F.7.9 Get displayName of a fieldAccessPolicyDefinition."""
    return _scalar(_get_definition(definitionID), "display_name")


def getFieldAccessPolicyDefinitionShortDescription(definitionID: str) -> str | None:
    """Section: F.7.9 Get shortDescription of a fieldAccessPolicyDefinition."""
    return _scalar(_get_definition(definitionID), "short_description")


def getFieldAccessPolicyDefinitionDescription(definitionID: str) -> str | None:
    """Section: F.7.9 Get description of a fieldAccessPolicyDefinition."""
    return _scalar(_get_definition(definitionID), "description")


def getFieldAccessPolicyDefinitionAccess(definitionID: str) -> str | None:
    """Section: F.7.9 Get access value of a fieldAccessPolicyDefinition."""
    return _scalar(_get_definition(definitionID), "access")


def getFieldAccessPolicyDefinitionModifiedWriteValue(definitionID: str) -> str | None:
    """Section: F.7.9 Get modifiedWriteValue of a fieldAccessPolicyDefinition."""
    return _scalar(_get_definition(definitionID), "modified_write_value")


def getFieldAccessPolicyDefinitionWriteValueConstraint(definitionID: str) -> str | None:
    """Section: F.7.9 Get writeValueConstraint (string) of a fieldAccessPolicyDefinition."""
    return _scalar(_get_definition(definitionID), "write_value_constraint")


def getFieldAccessPolicyDefinitionReadAction(definitionID: str) -> str | None:
    """Section: F.7.9 Get readAction of a fieldAccessPolicyDefinition."""
    return _scalar(_get_definition(definitionID), "read_action")


def getFieldAccessPolicyDefinitionReadResponse(definitionID: str) -> str | None:
    """Section: F.7.9 Get readResponse of a fieldAccessPolicyDefinition."""
    return _scalar(_get_definition(definitionID), "read_response")


# ---------------------------------------------------------------------------
# F.7.6 legacy compatibility
# ---------------------------------------------------------------------------
def getFieldAccessPolicyModeRefByID(fieldAccessPolicyID: str, modeRefID: int) -> str | None:  # F.7.6.1
    """Section: F.7.6.1 Return handle of indexed modeRef of a fieldAccessPolicy."""
    pol = _get_inline_field_policy(fieldAccessPolicyID)
    refs = list(getattr(pol, "mode_ref", []))
    if 0 <= modeRefID < len(refs):
        return get_handle(refs[modeRefID])
    return None


# ---------------------------------------------------------------------------
# F.7.9 BASE AccessPolicy and related getters (full coverage)
# ---------------------------------------------------------------------------
def getAccessPolicyAccess(accessPolicyID: str) -> str | None:  # F.7.9.1
    """Section: F.7.9.1 Return access value of an accessPolicy."""
    return _scalar(_get_access_policy(accessPolicyID), "access")


def getAccessPolicyModeRefByID(accessPolicyID: str, modeRef: str) -> str | None:  # F.7.9.2
    """Section: F.7.9.2 Return handle of named modeRef in accessPolicy."""
    ap = _get_access_policy(accessPolicyID)
    m = _first(getattr(ap, "mode_ref", []), lambda r: getattr(r, "value", None) == modeRef)
    return None if m is None else get_handle(m)


def getAccessPolicyModeRefByNames(accessPolicyID: str) -> list[str]:  # F.7.9.3
    """Section: F.7.9.3 Return list of modeRef names in accessPolicy."""
    ap = _get_access_policy(accessPolicyID)
    return [getattr(r, "value", "") for r in getattr(ap, "mode_ref", [])]


def getAccessPolicyModeRefIDs(accessPolicyID: str) -> list[str]:  # F.7.9.4
    """Section: F.7.9.4 Return handles of modeRef elements in accessPolicy."""
    ap = _get_access_policy(accessPolicyID)
    return _ids(getattr(ap, "mode_ref", []))


def getAccessRestrictionModeRefIDs(accessRestrictionID: str) -> list[str]:  # F.7.9.5
    """Section: F.7.9.5 Return modeRef handles of an accessRestriction."""
    ar = _get_access_restriction_handle(accessRestrictionID)
    return _ids(getattr(ar, "mode_ref", []))


def getAccessRestrictionModeRefbyID(accessRestrictionID: str, modeRef: str) -> str | None:  # F.7.9.6
    """Section: F.7.9.6 Return handle of named modeRef in accessRestriction."""
    ar = _get_access_restriction_handle(accessRestrictionID)
    m = _first(getattr(ar, "mode_ref", []), lambda r: getattr(r, "value", None) == modeRef)
    return None if m is None else get_handle(m)


def getAccessRestrictionModeRefbyNames(accessRestrictionID: str) -> list[str]:  # F.7.9.7
    """Section: F.7.9.7 Return list of modeRef names in accessRestriction."""
    ar = _get_access_restriction_handle(accessRestrictionID)
    return [getattr(r, "value", "") for r in getattr(ar, "mode_ref", [])]


def getAccessRestrictionReadAccessMask(accessRestrictionID: str) -> Numeric | None:  # F.7.9.8
    """Section: F.7.9.8 Return numeric readAccessMask value (if simple expression)."""
    ar = _get_access_restriction_handle(accessRestrictionID)
    m = getattr(ar, "read_access_mask", None)
    return getattr(m, "value", None) if m is not None else None


def getAccessRestrictionReadAccessMaskExpression(accessRestrictionID: str) -> str | None:  # F.7.9.9
    """Section: F.7.9.9 Return readAccessMask expression string."""
    val = getAccessRestrictionReadAccessMask(accessRestrictionID)
    return None if val is None else str(val)


def getAccessRestrictionReadAccessMaskID(accessRestrictionID: str) -> str | None:  # F.7.9.10
    """Section: F.7.9.10 Return handle of readAccessMask element."""
    ar = _get_access_restriction_handle(accessRestrictionID)
    m = getattr(ar, "read_access_mask", None)
    return get_handle(m) if m is not None else None


def getAccessRestrictionWriteAccessMask(accessRestrictionID: str) -> Numeric | None:  # F.7.9.11
    """Section: F.7.9.11 Return numeric writeAccessMask value."""
    ar = _get_access_restriction_handle(accessRestrictionID)
    m = getattr(ar, "write_access_mask", None)
    return getattr(m, "value", None) if m is not None else None


def getAccessRestrictionWriteAccessMaskExpression(accessRestrictionID: str) -> str | None:  # F.7.9.12
    """Section: F.7.9.12 Return writeAccessMask expression string."""
    val = getAccessRestrictionWriteAccessMask(accessRestrictionID)
    return None if val is None else str(val)


def getAccessRestrictionWriteAccessMaskID(accessRestrictionID: str) -> str | None:  # F.7.9.13
    """Section: F.7.9.13 Return handle of writeAccessMask element."""
    ar = _get_access_restriction_handle(accessRestrictionID)
    m = getattr(ar, "write_access_mask", None)
    return get_handle(m) if m is not None else None


def _collect_access_policies(parentID: str, attr_name: str) -> list[Any]:
    parent = resolve_handle(parentID)
    if parent is None:
        raise TgiError("Invalid parent handle", TgiFaultCode.INVALID_ID)
    cont = getattr(parent, attr_name, None)
    if cont is None:
        return []
    return list(getattr(cont, "access_policy", []))


def getAlternateRegisterAccessPolicyIDs(alternateRegisterID: str) -> list[str]:  # F.7.9.14
    """Section: F.7.9.14 Return accessPolicy handles of an alternateRegister."""
    return _ids(_collect_access_policies(alternateRegisterID, "access_policies"))


def getBankAccessPoliciesIDs(bankID: str) -> list[str]:  # F.7.9.15
    """Section: F.7.9.15 Return accessPolicy handles of a bank."""
    return _ids(_collect_access_policies(bankID, "access_policies"))


def getFieldAccessPoliciesFieldAccessPolicyIDs(fieldAccessPoliciesID: str) -> list[str]:  # F.7.9.16
    """Section: F.7.9.16 Return fieldAccessPolicy handles inside fieldAccessPolicies."""
    cont = resolve_handle(fieldAccessPoliciesID)
    if cont is None or not hasattr(cont, "field_access_policy"):
        raise TgiError("Invalid fieldAccessPolicies handle", TgiFaultCode.INVALID_ID)
    return _ids(getattr(cont, "field_access_policy", []))


def getFieldAccessPolicyAccess(fieldAccessPolicyID: str) -> str | None:  # F.7.9.17
    """Section: F.7.9.17 Return access value of a fieldAccessPolicy."""
    return _scalar(_get_inline_field_policy(fieldAccessPolicyID), "access")


def getFieldAccessPolicyAccessRestrictionIDs(fieldAccessPolicyID: str) -> list[str]:  # F.7.9.18
    """Section: F.7.9.18 Return accessRestriction handles of a fieldAccessPolicy."""
    pol = _get_inline_field_policy(fieldAccessPolicyID)
    return _ids(_get_access_restrictions(pol))


def getFieldAccessPolicyFieldAccessPolicyDefinitionRefByExternalTypeDefID(
    fieldAccessPolicyID: str,
) -> str | None:  # F.7.9.19
    """Section: F.7.9.19 externalTypeDefinitions not represented -> raise INVALID_ARGUMENT."""
    raise TgiError("externalTypeDefinitions unsupported in generated schema", TgiFaultCode.INVALID_ARGUMENT)


def getFieldAccessPolicyFieldAccessPolicyDefinitionRefByID(fieldAccessPolicyID: str) -> str | None:  # F.7.9.20
    """Section: F.7.9.20 Definition reference resolves by name only -> return None."""
    _get_inline_field_policy(fieldAccessPolicyID)
    return None  # Name-based indirection only, no direct object handle in schema


def getFieldAccessPolicyFieldAccessPolicyDefinitionRefByName(fieldAccessPolicyID: str) -> str | None:  # F.7.9.21
    """Section: F.7.9.21 Return definition name from fieldAccessPolicyDefinitionRef."""
    pol = _get_inline_field_policy(fieldAccessPolicyID)
    ref = getattr(pol, "field_access_policy_definition_ref", None)
    return getattr(ref, "value", None) if ref is not None else None


def getFieldAccessPolicyFieldAccessPolicyDefinitionRefID(fieldAccessPolicyID: str) -> str | None:  # F.7.9.22
    """Section: F.7.9.22 Return handle of fieldAccessPolicyDefinitionRef element."""
    pol = _get_inline_field_policy(fieldAccessPolicyID)
    ref = getattr(pol, "field_access_policy_definition_ref", None)
    return get_handle(ref) if ref is not None else None


def getFieldAccessPolicyModeRefByName(fieldAccessPolicyID: str) -> list[str]:  # F.7.9.23
    """Section: F.7.9.23 Return list of modeRef names of a fieldAccessPolicy."""
    pol = _get_inline_field_policy(fieldAccessPolicyID)
    return [getattr(r, "value", "") for r in getattr(pol, "mode_ref", [])]


def getFieldAccessPolicyModeRefIDs(fieldAccessPolicyID: str) -> list[str]:  # F.7.9.24
    """Section: F.7.9.24 Return modeRef handles for a fieldAccessPolicy."""
    pol = _get_inline_field_policy(fieldAccessPolicyID)
    return _ids(getattr(pol, "mode_ref", []))


def getFieldAccessPolicyModifiedWriteValue(fieldAccessPolicyID: str) -> str | None:  # F.7.9.25
    """Section: F.7.9.25 Return modifiedWriteValue value."""
    return _scalar(_get_inline_field_policy(fieldAccessPolicyID), "modified_write_value")


def getFieldAccessPolicyModifiedWriteValueID(fieldAccessPolicyID: str) -> str | None:  # F.7.9.26
    """Section: F.7.9.26 Return handle of modifiedWriteValue element."""
    pol = _get_inline_field_policy(fieldAccessPolicyID)
    mv = getattr(pol, "modified_write_value", None)
    return get_handle(mv) if mv is not None else None


def getFieldAccessPolicyReadAction(fieldAccessPolicyID: str) -> str | None:  # F.7.9.27
    """Section: F.7.9.27 Return readAction value."""
    return _scalar(_get_inline_field_policy(fieldAccessPolicyID), "read_action")


def getFieldAccessPolicyReadActionID(fieldAccessPolicyID: str) -> str | None:  # F.7.9.28
    """Section: F.7.9.28 Return handle of readAction element."""
    pol = _get_inline_field_policy(fieldAccessPolicyID)
    ra = getattr(pol, "read_action", None)
    return get_handle(ra) if ra is not None else None


def getFieldAccessPolicyReadResponse(fieldAccessPolicyID: str) -> Numeric | None:  # F.7.9.29
    """Section: F.7.9.29 Return numeric readResponse value."""
    pol = _get_inline_field_policy(fieldAccessPolicyID)
    rr = getattr(pol, "read_response", None)
    return getattr(rr, "value", None) if rr is not None else None


def getFieldAccessPolicyReadResponseExpression(fieldAccessPolicyID: str) -> str | None:  # F.7.9.30
    """Section: F.7.9.30 Return readResponse expression string."""
    val = getFieldAccessPolicyReadResponse(fieldAccessPolicyID)
    return None if val is None else str(val)


def getFieldAccessPolicyReadResponseID(fieldAccessPolicyID: str) -> str | None:  # F.7.9.31
    """Section: F.7.9.31 Return handle of readResponse element."""
    pol = _get_inline_field_policy(fieldAccessPolicyID)
    rr = getattr(pol, "read_response", None)
    return get_handle(rr) if rr is not None else None


def getFieldAccessPolicyReserved(fieldAccessPolicyID: str) -> Numeric | None:  # F.7.9.32
    """Section: F.7.9.32 Return reserved numeric value."""
    pol = _get_inline_field_policy(fieldAccessPolicyID)
    r = getattr(pol, "reserved", None)
    return getattr(r, "value", None) if r is not None else None


def getFieldAccessPolicyReservedExpression(fieldAccessPolicyID: str) -> str | None:  # F.7.9.33
    """Section: F.7.9.33 Return reserved expression string."""
    val = getFieldAccessPolicyReserved(fieldAccessPolicyID)
    return None if val is None else str(val)


def getFieldAccessPolicyReservedID(fieldAccessPolicyID: str) -> str | None:  # F.7.9.34
    """Section: F.7.9.34 Return handle of reserved element."""
    pol = _get_inline_field_policy(fieldAccessPolicyID)
    r = getattr(pol, "reserved", None)
    return get_handle(r) if r is not None else None


def getFieldAccessPolicyTestable(fieldAccessPolicyID: str) -> bool | None:  # F.7.9.35
    """Section: F.7.9.35 Return testable boolean value."""
    pol = _get_inline_field_policy(fieldAccessPolicyID)
    t = getattr(pol, "testable", None)
    return getattr(t, "value", None) if t is not None else None


def getFieldAccessPolicyTestableID(fieldAccessPolicyID: str) -> str | None:  # F.7.9.36
    """Section: F.7.9.36 Return handle of testable element."""
    pol = _get_inline_field_policy(fieldAccessPolicyID)
    t = getattr(pol, "testable", None)
    return get_handle(t) if t is not None else None


def getFieldAccessPolicyWriteValueConstraintID(fieldAccessPolicyID: str) -> str | None:  # F.7.9.37
    """Section: F.7.9.37 Return handle of writeValueConstraint element."""
    pol = _get_inline_field_policy(fieldAccessPolicyID)
    w = getattr(pol, "write_value_constraint", None)
    return get_handle(w) if w is not None else None


def getFieldAccesspolicyBroadcastToIDs(fieldAccessPolicyID: str) -> list[str]:  # F.7.9.38
    """Section: F.7.9.38 Return broadcastTo handles under broadcasts."""
    pol = _get_inline_field_policy(fieldAccessPolicyID)
    b = getattr(pol, "broadcasts", None)
    if b is None:
        return []
    return _ids(getattr(b, "broadcast_to", []))


def getRegisterAccessPolicyIDs(registerID: str) -> list[str]:  # F.7.9.39
    """Section: F.7.9.39 Return accessPolicy handles of a register."""
    return _ids(_collect_access_policies(registerID, "access_policies"))


def getRegisterFieldFieldAccessPoliciesID(registerFieldID: str) -> str | None:  # F.7.9.40
    """Section: F.7.9.40 Return handle of fieldAccessPolicies container on a field."""
    f = resolve_handle(registerFieldID)
    if f is None:
        raise TgiError("Invalid registerField handle", TgiFaultCode.INVALID_ID)
    cont = getattr(f, "field_access_policies", None)
    return get_handle(cont) if cont is not None else None


def getTypeDefinitionsFieldAccessPolicyDefinitionIDs(typeDefinitionsID: str) -> list[str]:  # F.7.9.41
    """Section: F.7.9.41 Return fieldAccessPolicyDefinition handles under typeDefinitions."""
    td = resolve_handle(typeDefinitionsID)
    if td is None or not hasattr(td, "field_access_policy_definitions"):
        raise TgiError("Invalid typeDefinitions handle", TgiFaultCode.INVALID_ID)
    defs = getattr(td, "field_access_policy_definitions", None)
    if defs is None:
        return []
    return _ids(getattr(defs, "field_access_policy_definition", []))


def getWriteValueConstraintMaximum(writeValueConstraintID: str) -> Numeric | None:  # F.7.9.42
    """Section: F.7.9.42 Return maximum numeric value."""
    w = _get_write_value_constraint_handle(writeValueConstraintID)
    m = getattr(w, "maximum", None)
    return getattr(m, "value", None) if m is not None else None


def getWriteValueConstraintMaximumExpression(writeValueConstraintID: str) -> str | None:  # F.7.9.43
    """Section: F.7.9.43 Return maximum expression string."""
    val = getWriteValueConstraintMaximum(writeValueConstraintID)
    return None if val is None else str(val)


def getWriteValueConstraintMaximumID(writeValueConstraintID: str) -> str | None:  # F.7.9.44
    """Section: F.7.9.44 Return handle of maximum element."""
    w = _get_write_value_constraint_handle(writeValueConstraintID)
    m = getattr(w, "maximum", None)
    return get_handle(m) if m is not None else None


def getWriteValueConstraintMinimum(writeValueConstraintID: str) -> Numeric | None:  # F.7.9.45
    """Section: F.7.9.45 Return minimum numeric value."""
    w = _get_write_value_constraint_handle(writeValueConstraintID)
    m = getattr(w, "minimum", None)
    return getattr(m, "value", None) if m is not None else None


def getWriteValueConstraintMinimumExpression(writeValueConstraintID: str) -> str | None:  # F.7.9.46
    """Section: F.7.9.46 Return minimum expression string."""
    val = getWriteValueConstraintMinimum(writeValueConstraintID)
    return None if val is None else str(val)


def getWriteValueConstraintMinimumID(writeValueConstraintID: str) -> str | None:  # F.7.9.47
    """Section: F.7.9.47 Return handle of minimum element."""
    w = _get_write_value_constraint_handle(writeValueConstraintID)
    m = getattr(w, "minimum", None)
    return get_handle(m) if m is not None else None


def getWriteValueConstraintUseEnumeratedValues(writeValueConstraintID: str) -> bool | None:  # F.7.9.48
    """Section: F.7.9.48 Return useEnumeratedValues flag."""
    w = _get_write_value_constraint_handle(writeValueConstraintID)
    return _scalar_bool(w, "use_enumerated_values")


def getWriteValueConstraintWriteAsRead(writeValueConstraintID: str) -> bool | None:  # F.7.9.49
    """Section: F.7.9.49 Return writeAsRead flag."""
    w = _get_write_value_constraint_handle(writeValueConstraintID)
    return _scalar_bool(w, "write_as_read")


# ---------------------------------------------------------------------------
# F.7.10 EXTENDED – add/remove/set operations
# ---------------------------------------------------------------------------
def _append_and_register(parent: Any, list_attr: str, child: Any, path: tuple[str, ...]):
    lst = getattr(parent, list_attr)
    lst.append(child)
    register_parent(child, parent, path, "list")
    return get_handle(child)


def addAccessRestrictionModeRef(accessRestrictionID: str, modeRef: str, priority: int | None = None) -> str:  # F.7.10.1
    """Section: F.7.10.1 Add a modeRef to an accessRestriction."""
    ar = _get_access_restriction_handle(accessRestrictionID)
    from org.accellera.ipxact.v1685_2022.mode_ref import ModeRef

    mr = ModeRef(value=modeRef, priority=priority)
    ar.mode_ref.append(mr)  # type: ignore[attr-defined]
    register_parent(mr, ar, ("mode_ref",), "list")
    return get_handle(mr)


def _ensure_access_policies(parent: Any):
    if getattr(parent, "access_policies", None) is None:
        from org.accellera.ipxact.v1685_2022.access_policies import AccessPolicies

        parent.access_policies = AccessPolicies()  # type: ignore[attr-defined]


def _new_access_policy() -> Any:
    from org.accellera.ipxact.v1685_2022.access_policies import AccessPolicies

    return AccessPolicies.AccessPolicy()


def addAddressBlockAccessPolicy(addressBlockID: str) -> str:  # F.7.10.2
    """Section: F.7.10.2 Add accessPolicy to addressBlock."""
    blk = resolve_handle(addressBlockID)
    if blk is None:
        raise TgiError("Invalid addressBlock handle", TgiFaultCode.INVALID_ID)
    _ensure_access_policies(blk)
    ap = _new_access_policy()
    return _append_and_register(blk.access_policies, "access_policy", ap, ("access_policies", "access_policy"))


def addAlternateRegisterAccessPolicy(registerID: str) -> str:  # F.7.10.3
    """Section: F.7.10.3 Add accessPolicy to alternateRegister."""
    reg = resolve_handle(registerID)
    if reg is None:
        raise TgiError("Invalid alternateRegister handle", TgiFaultCode.INVALID_ID)
    _ensure_access_policies(reg)
    ap = _new_access_policy()
    return _append_and_register(reg.access_policies, "access_policy", ap, ("access_policies", "access_policy"))


def addExternalTypeDefinitionsResetTypeLink(*_args, **_kwargs) -> str:  # F.7.10.4
    """Section: F.7.10.4 Not supported by generated schema (externalTypeDefinitions)."""
    raise TgiError("externalTypeDefinitions resetTypeLink unsupported", TgiFaultCode.INVALID_ARGUMENT)


def addFieldAccessPoliciesFieldAccessPolicy(fieldAccessPoliciesID: str) -> str:  # F.7.10.5
    """Section: F.7.10.5 Add fieldAccessPolicy to fieldAccessPolicies."""
    cont = resolve_handle(fieldAccessPoliciesID)
    if cont is None or not hasattr(cont, "field_access_policy"):
        raise TgiError("Invalid fieldAccessPolicies handle", TgiFaultCode.INVALID_ID)
    from org.accellera.ipxact.v1685_2022.field_definitions import FieldDefinitions

    pol = FieldDefinitions.FieldDefinition.FieldAccessPolicies.FieldAccessPolicy()
    cont.field_access_policy.append(pol)  # type: ignore[attr-defined]
    register_parent(pol, cont, ("field_access_policy",), "list")
    return get_handle(pol)


def addFieldAccessPolicyAccessRestriction(fieldAccessPolicyID: str) -> str:  # F.7.10.6
    """Section: F.7.10.6 Add accessRestriction to fieldAccessPolicy."""
    pol = _get_inline_field_policy(fieldAccessPolicyID)
    from org.accellera.ipxact.v1685_2022.access_restriction_type import AccessRestrictionType
    from org.accellera.ipxact.v1685_2022.access_restrictions import AccessRestrictions

    if pol.access_restrictions is None:  # type: ignore[attr-defined]
        pol.access_restrictions = AccessRestrictions()  # type: ignore[attr-defined]
    ar = AccessRestrictionType()
    pol.access_restrictions.access_restriction.append(ar)  # type: ignore[attr-defined]
    register_parent(ar, pol.access_restrictions, ("access_restrictions", "access_restriction"), "list")
    return get_handle(ar)


def addFieldAccessPolicyBroadcastTo(
    fieldAccessPolicyID: str,
    memoryMapRef: str | None = None,
    addressBlockRef: str | None = None,
    registerRef: str | None = None,
    fieldRef: str | None = None,
) -> str:  # F.7.10.7
    """Section: F.7.10.7 Add broadcastTo element to fieldAccessPolicy (subset of refs)."""
    pol = _get_inline_field_policy(fieldAccessPolicyID)
    from org.accellera.ipxact.v1685_2022.field_definitions import FieldDefinitions

    if pol.broadcasts is None:  # type: ignore[attr-defined]
        pol.broadcasts = FieldDefinitions.FieldDefinition.FieldAccessPolicies.FieldAccessPolicy.Broadcasts()  # type: ignore[attr-defined]
    bt = FieldDefinitions.FieldDefinition.FieldAccessPolicies.FieldAccessPolicy.Broadcasts.BroadcastTo()
    if memoryMapRef is not None:
        bt.memory_map_ref = (
            FieldDefinitions.FieldDefinition.FieldAccessPolicies.FieldAccessPolicy.Broadcasts
            .BroadcastTo.MemoryMapRef(memory_map_ref=memoryMapRef)  # type: ignore[attr-defined]
        )
    if addressBlockRef is not None:
        from org.accellera.ipxact.v1685_2022.address_block_ref import AddressBlockRef

        bt.address_block_ref = AddressBlockRef(address_block_ref=addressBlockRef)  # type: ignore[attr-defined]
    if registerRef is not None:
        from org.accellera.ipxact.v1685_2022.register_ref import RegisterRef

        bt.register_ref = RegisterRef(register_ref=registerRef)  # type: ignore[attr-defined]
    if fieldRef is not None:
        from org.accellera.ipxact.v1685_2022.field_ref import FieldRef

        bt.field_ref = FieldRef(field_ref=fieldRef)  # type: ignore[attr-defined]
    pol.broadcasts.broadcast_to.append(bt)  # type: ignore[attr-defined]
    register_parent(bt, pol.broadcasts, ("broadcasts", "broadcast_to"), "list")
    return get_handle(bt)


def addFieldAccessPolicyModeRef(fieldAccessPolicyID: str, modeRef: str, priority: int | None = None) -> str:  # F.7.10.8
    """Section: F.7.10.8 Add modeRef to fieldAccessPolicy."""
    pol = _get_inline_field_policy(fieldAccessPolicyID)
    from org.accellera.ipxact.v1685_2022.mode_ref import ModeRef

    mr = ModeRef(value=modeRef, priority=priority)
    pol.mode_ref.append(mr)  # type: ignore[attr-defined]
    register_parent(mr, pol, ("mode_ref",), "list")
    return get_handle(mr)


def addFieldDefinitionFieldAccessPolicy(fieldDefinitionID: str) -> str:  # F.7.10.9
    """Section: F.7.10.9 Add fieldAccessPolicy to a fieldDefinition (create container if absent)."""
    fd = resolve_handle(fieldDefinitionID)
    if fd is None:
        raise TgiError("Invalid fieldDefinition handle", TgiFaultCode.INVALID_ID)
    if getattr(fd, "field_access_policies", None) is None:
        from org.accellera.ipxact.v1685_2022.field_definitions import FieldDefinitions

        fd.field_access_policies = FieldDefinitions.FieldDefinition.FieldAccessPolicies()  # type: ignore[attr-defined]
    from org.accellera.ipxact.v1685_2022.field_definitions import FieldDefinitions

    pol = FieldDefinitions.FieldDefinition.FieldAccessPolicies.FieldAccessPolicy()
    fd.field_access_policies.field_access_policy.append(pol)  # type: ignore[attr-defined]
    register_parent(pol, fd.field_access_policies, ("field_access_policies", "field_access_policy"), "list")
    return get_handle(pol)


def addRegisterAccessPolicy(registerID: str) -> str:  # F.7.10.10
    """Section: F.7.10.10 Add accessPolicy to register."""
    reg = resolve_handle(registerID)
    if reg is None:
        raise TgiError("Invalid register handle", TgiFaultCode.INVALID_ID)
    _ensure_access_policies(reg)
    ap = _new_access_policy()
    return _append_and_register(reg.access_policies, "access_policy", ap, ("access_policies", "access_policy"))


def addRegisterFileAccessPolicy(registerFileID: str) -> str:  # F.7.10.11
    """Section: F.7.10.11 Add accessPolicy to registerFile."""
    rf = resolve_handle(registerFileID)
    if rf is None:
        raise TgiError("Invalid registerFile handle", TgiFaultCode.INVALID_ID)
    _ensure_access_policies(rf)
    ap = _new_access_policy()
    return _append_and_register(rf.access_policies, "access_policy", ap, ("access_policies", "access_policy"))


# Removals
def removeAccessPolicyAccess(accessPolicyID: str) -> bool:  # F.7.10.12
    """Section: F.7.10.12 Remove access element from accessPolicy."""
    ap = _get_access_policy(accessPolicyID)
    if getattr(ap, "access", None) is None:
        return False
    ap.access = None  # type: ignore[attr-defined]
    return True


def removeAccessRestrictionModeRef(modeRefID: str) -> bool:  # F.7.10.13
    """Section: F.7.10.13 Remove a modeRef from an accessRestriction."""
    return detach_child_by_handle(modeRefID)


def removeAccessRestrictionReadAccessMask(accessRestrictionID: str) -> bool:  # F.7.10.14
    """Section: F.7.10.14 Remove readAccessMask element."""
    ar = _get_access_restriction_handle(accessRestrictionID)
    if getattr(ar, "read_access_mask", None) is None:
        return False
    ar.read_access_mask = None  # type: ignore[attr-defined]
    return True


def removeAccessRestrictionWriteAccessMask(accessRestrictionID: str) -> bool:  # F.7.10.15
    """Section: F.7.10.15 Remove writeAccessMask element."""
    ar = _get_access_restriction_handle(accessRestrictionID)
    if getattr(ar, "write_access_mask", None) is None:
        return False
    ar.write_access_mask = None  # type: ignore[attr-defined]
    return True


def removeAddressBlockAccessPolicyID(accessPolicyID: str) -> bool:  # F.7.10.16
    """Section: F.7.10.16 Remove accessPolicy (addressBlock container)."""
    return detach_child_by_handle(accessPolicyID)


def removeAlternateRegisterAccessPolicy(accessPolicyID: str) -> bool:  # F.7.10.17
    """Section: F.7.10.17 Remove accessPolicy (alternateRegister container)."""
    return detach_child_by_handle(accessPolicyID)


def removeFieldAccessPoliciesFieldAccessPolicy(
    fieldAccessPoliciesID: str,
    fieldAccessPolicyID: str,
) -> bool:  # F.7.10.18
    """Section: F.7.10.18 Remove fieldAccessPolicy from fieldAccessPolicies."""
    return detach_child_by_handle(fieldAccessPolicyID)


def removeFieldAccessPolicyAccess(fieldAccessPolicyID: str) -> bool:  # F.7.10.19
    """Section: F.7.10.19 Remove access from fieldAccessPolicy."""
    pol = _get_inline_field_policy(fieldAccessPolicyID)
    if getattr(pol, "access", None) is None:
        return False
    pol.access = None  # type: ignore[attr-defined]
    return True


def removeFieldAccessPolicyAccessRestriction(accessRestrictionID: str) -> bool:  # F.7.10.20
    """Section: F.7.10.20 Remove accessRestriction."""
    return detach_child_by_handle(accessRestrictionID)


def removeFieldAccessPolicyBroadcastTo(broadcastToID: str) -> bool:  # F.7.10.21
    """Section: F.7.10.21 Remove broadcastTo element."""
    return detach_child_by_handle(broadcastToID)


def removeFieldAccessPolicyFieldAccessPolicyDefinitionRef(fieldAccessPolicyID: str) -> bool:  # F.7.10.22
    """Section: F.7.10.22 Remove fieldAccessPolicyDefinitionRef."""
    pol = _get_inline_field_policy(fieldAccessPolicyID)
    if getattr(pol, "field_access_policy_definition_ref", None) is None:
        return False
    pol.field_access_policy_definition_ref = None  # type: ignore[attr-defined]
    return True


def removeFieldAccessPolicyModeRef(modeRefID: str) -> bool:  # F.7.10.23
    """Section: F.7.10.23 Remove fieldAccessPolicy modeRef."""
    return detach_child_by_handle(modeRefID)


def removeFieldAccessPolicyModifiedWriteValue(fieldAccessPolicyID: str) -> bool:  # F.7.10.24
    """Section: F.7.10.24 Remove modifiedWriteValue."""
    pol = _get_inline_field_policy(fieldAccessPolicyID)
    if getattr(pol, "modified_write_value", None) is None:
        return False
    pol.modified_write_value = None  # type: ignore[attr-defined]
    return True


def removeFieldAccessPolicyReadAction(fieldAccessPolicyID: str) -> bool:  # F.7.10.25
    """Section: F.7.10.25 Remove readAction."""
    pol = _get_inline_field_policy(fieldAccessPolicyID)
    if getattr(pol, "read_action", None) is None:
        return False
    pol.read_action = None  # type: ignore[attr-defined]
    return True


def removeFieldAccessPolicyReadResponse(fieldAccessPolicyID: str) -> bool:  # F.7.10.26
    """Section: F.7.10.26 Remove readResponse."""
    pol = _get_inline_field_policy(fieldAccessPolicyID)
    if getattr(pol, "read_response", None) is None:
        return False
    pol.read_response = None  # type: ignore[attr-defined]
    return True


def removeFieldAccessPolicyReserved(fieldAccessPolicyID: str) -> bool:  # F.7.10.27
    """Section: F.7.10.27 Remove reserved."""
    pol = _get_inline_field_policy(fieldAccessPolicyID)
    if getattr(pol, "reserved", None) is None:
        return False
    pol.reserved = None  # type: ignore[attr-defined]
    return True


def removeFieldAccessPolicyTestable(fieldAccessPolicyID: str) -> bool:  # F.7.10.28
    """Section: F.7.10.28 Remove testable."""
    pol = _get_inline_field_policy(fieldAccessPolicyID)
    if getattr(pol, "testable", None) is None:
        return False
    pol.testable = None  # type: ignore[attr-defined]
    return True


def removeFieldAccessPolicyWriteValueConstraint(fieldAccessPolicyID: str) -> bool:  # F.7.10.29
    """Section: F.7.10.29 Remove writeValueConstraint."""
    pol = _get_inline_field_policy(fieldAccessPolicyID)
    if getattr(pol, "write_value_constraint", None) is None:
        return False
    pol.write_value_constraint = None  # type: ignore[attr-defined]
    return True


def removeFieldDefinitionFieldAccessPolicy(accessPolicyID: str) -> bool:  # F.7.10.30
    """Section: F.7.10.30 Remove fieldAccessPolicy from fieldDefinition."""
    return detach_child_by_handle(accessPolicyID)


def removeRegisterAccessPolicy(accessPolicyID: str) -> bool:  # F.7.10.31
    """Section: F.7.10.31 Remove accessPolicy from register."""
    return detach_child_by_handle(accessPolicyID)


def removeRegisterFileAccessPolicy(accessPolicyID: str) -> bool:  # F.7.10.32
    """Section: F.7.10.32 Remove accessPolicy from registerFile."""
    return detach_child_by_handle(accessPolicyID)


# Setters
def setAccessPolicyAccess(accessPolicyID: str, access: str) -> bool:  # F.7.10.33
    """Section: F.7.10.33 Set access value on accessPolicy."""
    ap = _get_access_policy(accessPolicyID)
    ap.access = access  # type: ignore[attr-defined]
    return True


def setAccessRestrictionReadAccessMask(accessRestrictionID: str, value: str) -> bool:  # F.7.10.34
    """Section: F.7.10.34 Set readAccessMask expression/value."""
    ar = _get_access_restriction_handle(accessRestrictionID)
    from org.accellera.ipxact.v1685_2022.unsigned_bit_vector_expression import UnsignedBitVectorExpression

    ar.read_access_mask = UnsignedBitVectorExpression(value=value)  # type: ignore[attr-defined]
    return True


def setAccessRestrictionWriteAccessMask(accessRestrictionID: str, value: str) -> bool:  # F.7.10.35
    """Section: F.7.10.35 Set writeAccessMask expression/value."""
    ar = _get_access_restriction_handle(accessRestrictionID)
    from org.accellera.ipxact.v1685_2022.unsigned_bit_vector_expression import UnsignedBitVectorExpression

    ar.write_access_mask = UnsignedBitVectorExpression(value=value)  # type: ignore[attr-defined]
    return True


def setFieldAccessPolicyAccess(fieldAccessPolicyID: str, access: str) -> bool:  # F.7.10.36
    """Section: F.7.10.36 Set access of fieldAccessPolicy."""
    pol = _get_inline_field_policy(fieldAccessPolicyID)
    pol.access = access  # type: ignore[attr-defined]
    return True


def setFieldAccessPolicyFieldAccessPolicyDefinitionRef(
    fieldAccessPolicyID: str,
    name: str,
    typeDefinitions: str | None = None,
) -> bool:  # F.7.10.37
    """Section: F.7.10.37 Set fieldAccessPolicyDefinitionRef values."""
    pol = _get_inline_field_policy(fieldAccessPolicyID)
    from org.accellera.ipxact.v1685_2022.field_access_policy_definition_ref import FieldAccessPolicyDefinitionRef

    pol.field_access_policy_definition_ref = FieldAccessPolicyDefinitionRef(
        value=name,
        type_definitions=typeDefinitions,
    )  # type: ignore[attr-defined]
    return True


def setFieldAccessPolicyModifiedWriteValue(
    fieldAccessPolicyID: str,
    value: str,
    modify: str | None = None,
) -> bool:  # F.7.10.38
    """Section: F.7.10.38 Set modifiedWriteValue element."""
    pol = _get_inline_field_policy(fieldAccessPolicyID)
    from org.accellera.ipxact.v1685_2022.modified_write_value import ModifiedWriteValue

    pol.modified_write_value = ModifiedWriteValue(value=value, modify=modify)  # type: ignore[attr-defined]
    return True


def setFieldAccessPolicyReadAction(fieldAccessPolicyID: str, value: str) -> bool:  # F.7.10.39
    """Section: F.7.10.39 Set readAction element."""
    pol = _get_inline_field_policy(fieldAccessPolicyID)
    from org.accellera.ipxact.v1685_2022.read_action import ReadAction

    pol.read_action = ReadAction(value=value)  # type: ignore[attr-defined]
    return True


def setFieldAccessPolicyReadResponse(fieldAccessPolicyID: str, value: str) -> bool:  # F.7.10.40
    """Section: F.7.10.40 Set readResponse element."""
    pol = _get_inline_field_policy(fieldAccessPolicyID)
    from org.accellera.ipxact.v1685_2022.unsigned_bit_vector_expression import UnsignedBitVectorExpression

    pol.read_response = UnsignedBitVectorExpression(value=value)  # type: ignore[attr-defined]
    return True


def setFieldAccessPolicyReserved(fieldAccessPolicyID: str, value: str) -> bool:  # F.7.10.41
    """Section: F.7.10.41 Set reserved element."""
    pol = _get_inline_field_policy(fieldAccessPolicyID)
    from org.accellera.ipxact.v1685_2022.unsigned_bit_expression import UnsignedBitExpression

    pol.reserved = UnsignedBitExpression(value=value)  # type: ignore[attr-defined]
    return True


def setFieldAccessPolicyTestable(
    fieldAccessPolicyID: str,
    value: bool,
    testConstraint: str | None = None,
) -> bool:  # F.7.10.42
    """Section: F.7.10.42 Set testable (boolean + optional constraint)."""
    pol = _get_inline_field_policy(fieldAccessPolicyID)
    from org.accellera.ipxact.v1685_2022.field_definitions import FieldDefinitions

    pol.testable = (
        FieldDefinitions.FieldDefinition.FieldAccessPolicies.FieldAccessPolicy.Testable(
            value=value,
            test_constraint=testConstraint,  # type: ignore[arg-type]
        )
    )  # type: ignore[attr-defined]
    return True


def setFieldAccessPolicyWriteValueConstraintMinMax(
    fieldAccessPolicyID: str,
    minimum: str | None,
    maximum: str | None,
) -> bool:  # F.7.10.43
    """Section: F.7.10.43 Set minimum/maximum on writeValueConstraint (create if absent)."""
    pol = _get_inline_field_policy(fieldAccessPolicyID)
    from org.accellera.ipxact.v1685_2022.unsigned_bit_vector_expression import UnsignedBitVectorExpression
    from org.accellera.ipxact.v1685_2022.write_value_constraint import WriteValueConstraint

    if pol.write_value_constraint is None:  # type: ignore[attr-defined]
        pol.write_value_constraint = WriteValueConstraint()  # type: ignore[attr-defined]
    if minimum is not None:
        pol.write_value_constraint.minimum = UnsignedBitVectorExpression(value=minimum)  # type: ignore[attr-defined]
    if maximum is not None:
        pol.write_value_constraint.maximum = UnsignedBitVectorExpression(value=maximum)  # type: ignore[attr-defined]
    return True


def setFieldAccessPolicyWriteValueConstraintUseEnumeratedValue(
    fieldAccessPolicyID: str,
    value: bool,
) -> bool:  # F.7.10.44
    """Section: F.7.10.44 Set useEnumeratedValues flag."""
    pol = _get_inline_field_policy(fieldAccessPolicyID)
    from org.accellera.ipxact.v1685_2022.write_value_constraint import WriteValueConstraint

    if pol.write_value_constraint is None:  # type: ignore[attr-defined]
        pol.write_value_constraint = WriteValueConstraint()  # type: ignore[attr-defined]
    pol.write_value_constraint.use_enumerated_values = value  # type: ignore[attr-defined]
    return True


def setFieldAccessPolicyWriteValueConstraintWriteAsRead(fieldAccessPolicyID: str, value: bool) -> bool:  # F.7.10.45
    """Section: F.7.10.45 Set writeAsRead flag."""
    pol = _get_inline_field_policy(fieldAccessPolicyID)
    from org.accellera.ipxact.v1685_2022.write_value_constraint import WriteValueConstraint

    if pol.write_value_constraint is None:  # type: ignore[attr-defined]
        pol.write_value_constraint = WriteValueConstraint()  # type: ignore[attr-defined]
    pol.write_value_constraint.write_as_read = value  # type: ignore[attr-defined]
    return True


def setWriteValueConstraintMaximum(writeValueConstraintID: str, maximum: str | None) -> bool:  # F.7.10.46
    """Section: F.7.10.46 Set maximum element (None clears)."""
    w = _get_write_value_constraint_handle(writeValueConstraintID)
    from org.accellera.ipxact.v1685_2022.unsigned_bit_vector_expression import UnsignedBitVectorExpression

    if maximum is None:
        w.maximum = None  # type: ignore[attr-defined]
    else:
        w.maximum = UnsignedBitVectorExpression(value=maximum)  # type: ignore[attr-defined]
    return True


def setWriteValueConstraintMinimum(writeValueConstraintID: str, minimum: str | None) -> bool:  # F.7.10.47
    """Section: F.7.10.47 Set minimum element (None clears)."""
    w = _get_write_value_constraint_handle(writeValueConstraintID)
    from org.accellera.ipxact.v1685_2022.unsigned_bit_vector_expression import UnsignedBitVectorExpression

    if minimum is None:
        w.minimum = None  # type: ignore[attr-defined]
    else:
        w.minimum = UnsignedBitVectorExpression(value=minimum)  # type: ignore[attr-defined]
    return True


def setWriteValueConstraintUseEnumeratedValues(writeValueConstraintID: str, value: bool | None) -> bool:  # F.7.10.48
    """Section: F.7.10.48 Set useEnumeratedValues flag (None clears)."""
    w = _get_write_value_constraint_handle(writeValueConstraintID)
    w.use_enumerated_values = value  # type: ignore[attr-defined]
    return True


def setWriteValueConstraintWriteAsRead(writeValueConstraintID: str, value: bool | None) -> bool:  # F.7.10.49
    """Section: F.7.10.49 Set writeAsRead flag (None clears)."""
    w = _get_write_value_constraint_handle(writeValueConstraintID)
    w.write_as_read = value  # type: ignore[attr-defined]
    return True


