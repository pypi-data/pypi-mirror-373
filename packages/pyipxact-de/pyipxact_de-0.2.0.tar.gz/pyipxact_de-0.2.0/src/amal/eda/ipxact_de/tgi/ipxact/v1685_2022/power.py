"""Power category TGI functions (IEEE 1685-2022).

Implements BASE (F.7.71) and EXTENDED (F.7.72) Power functions. Only the
functions defined in Annex F are exported – no additional helpers. BASE
getters return empty/None for invalid handles; EXTENDED mutators raise
``TgiError`` with appropriate ``TgiFaultCode``.
"""

# ruff: noqa: I001
from typing import Any

from org.accellera.ipxact.v1685_2022 import (
    ComponentType,
    Port,
    PortTransactionalType,
    PortWireType,
    TransactionalPowerConstraintType,
    WirePowerConstraintType,
)
from org.accellera.ipxact.v1685_2022.always_on import AlwaysOn
from org.accellera.ipxact.v1685_2022.left import Left
from org.accellera.ipxact.v1685_2022.range import Range
from org.accellera.ipxact.v1685_2022.right import Right
from org.accellera.ipxact.v1685_2022.power_domain_links import (
    PowerDomainLinks as SchemaPowerDomainLinks,
)
from org.accellera.ipxact.v1685_2022.power_domain_links import (
    PowerDomainLinks as PDL,
)

from .core import (
    TgiError,
    TgiFaultCode,
    get_handle,
    resolve_handle,
    register_parent,
    detach_child_by_handle,
)

__all__ = [
    # BASE (F.7.71)
    "getPortTransactionalPowerConstraintIDs",
    "getPortWirePowerConstraintIDs",
    "getPowerConstraintPowerDomainRefByID",
    "getPowerConstraintPowerDomainRefByName",
    "getPowerConstraintRange",
    "getPowerConstraintRangeLeftID",
    "getPowerConstraintRangeRightID",
    "getPowerDomainAlwaysOn",
    "getPowerDomainAlwaysOnExpression",
    "getPowerDomainAlwaysOnID",
    "getPowerDomainName",
    "getPowerDomainSubDomainOf",
    "getPowerDomainSubDomainOfRefByID",
    # EXTENDED (F.7.72)
    "addComponentInstancePowerDomainLink",
    "addComponentPowerDomain",
    "addPortTransactionalPowerConstraint",
    "addPortWirePowerConstraint",
    "addPowerDomainLinkInternalPowerDomainReference",
    "removeComponentInstancePowerDomainLink",
    "removeComponentPowerDomain",
    "removePowerConstraintRange",
    "removePowerDomainLinkInternalPowerDomainRef",
    "removePowerDomainSubDomainOf",
    "setPowerConstraintPowerDomainRef",
    "setPowerConstraintRange",
    "setPowerDomainAlwaysOn",
    "setPowerDomainSubDomainOf",
]


# ---------------------------------------------------------------------------
# Helpers (non-spec)
# ---------------------------------------------------------------------------

def _resolve_port(portID: str) -> Port | None:
    obj = resolve_handle(portID)
    return obj if isinstance(obj, Port) else None


def _resolve_wire_constraint(cID: str) -> WirePowerConstraintType | None:
    obj = resolve_handle(cID)
    return obj if isinstance(obj, WirePowerConstraintType) else None


def _resolve_tx_constraint(cID: str) -> TransactionalPowerConstraintType | None:
    obj = resolve_handle(cID)
    return obj if isinstance(obj, TransactionalPowerConstraintType) else None


def _resolve_power_domain(pdID: str) -> ComponentType.PowerDomains.PowerDomain | None:  # type: ignore[name-defined]
    obj = resolve_handle(pdID)
    if isinstance(obj, ComponentType.PowerDomains.PowerDomain):  # type: ignore[attr-defined]
        return obj
    return None


def _resolve_component(compID: str) -> ComponentType | None:
    obj = resolve_handle(compID)
    return obj if isinstance(obj, ComponentType) else None


def _expr(node: Any | None) -> str | None:
    if node is None:
        return None
    return getattr(node, "value", None)


# ---------------------------------------------------------------------------
# BASE (F.7.71)
# ---------------------------------------------------------------------------

def getPortTransactionalPowerConstraintIDs(portID: str) -> list[str]:
    """Return IDs of transactional powerConstraint elements (F.7.71.1)."""
    p = _resolve_port(portID)
    if p is None:
        return []
    tx = getattr(p, "transactional", None)
    if not isinstance(tx, PortTransactionalType):
        return []
    pc = getattr(tx, "power_constraints", None)
    if pc is None:
        return []
    return [
        get_handle(c)
        for c in getattr(pc, "power_constraint", [])
        if isinstance(c, TransactionalPowerConstraintType)
    ]


def getPortWirePowerConstraintIDs(portID: str) -> list[str]:
    """Return IDs of wire powerConstraint elements (F.7.71.2)."""
    p = _resolve_port(portID)
    if p is None:
        return []
    wire = getattr(p, "wire", None)
    if not isinstance(wire, PortWireType):
        return []
    pc = getattr(wire, "power_constraints", None)
    if pc is None:
        return []
    return [
        get_handle(c)
        for c in getattr(pc, "power_constraint", [])
        if isinstance(c, WirePowerConstraintType)
    ]


def getPowerConstraintPowerDomainRefByID(powerConstraintID: str) -> str | None:
    """Return powerDomainRef value for constraint (F.7.71.3)."""
    c = _resolve_wire_constraint(powerConstraintID) or _resolve_tx_constraint(powerConstraintID)
    pref = getattr(c, "power_domain_ref", None) if c else None
    return getattr(pref, "value", pref) if pref is not None else None


def getPowerConstraintPowerDomainRefByName(powerConstraintID: str) -> str | None:
    """Alias of getPowerConstraintPowerDomainRefByID (F.7.71.4)."""
    return getPowerConstraintPowerDomainRefByID(powerConstraintID)


def getPowerConstraintRange(powerConstraintID: str) -> str | None:
    """Return range handle if present (wire only) (F.7.71.5)."""
    c = _resolve_wire_constraint(powerConstraintID) or _resolve_tx_constraint(powerConstraintID)
    rng = getattr(c, "range", None) if c else None
    return get_handle(rng) if rng is not None else None


def getPowerConstraintRangeLeftID(powerConstraintID: str) -> str | None:
    """Return left bound handle of range (F.7.71.6)."""
    c = _resolve_wire_constraint(powerConstraintID) or _resolve_tx_constraint(powerConstraintID)
    rng = getattr(c, "range", None) if c else None
    left = getattr(rng, "left", None) if rng else None
    return get_handle(left) if left is not None else None


def getPowerConstraintRangeRightID(powerConstraintID: str) -> str | None:
    """Return right bound handle of range (F.7.71.7)."""
    c = _resolve_wire_constraint(powerConstraintID) or _resolve_tx_constraint(powerConstraintID)
    rng = getattr(c, "range", None) if c else None
    right = getattr(rng, "right", None) if rng else None
    return get_handle(right) if right is not None else None


def getPowerDomainAlwaysOn(powerDomainID: str) -> bool | None:
    """Return boolean alwaysOn value (F.7.71.8)."""
    pd = _resolve_power_domain(powerDomainID)
    ao = getattr(pd, "always_on", None) if pd else None
    val = getattr(ao, "value", ao) if ao is not None else None
    return val if isinstance(val, bool) else None


def getPowerDomainAlwaysOnExpression(powerDomainID: str) -> str | None:
    """Return expression string for alwaysOn (F.7.71.9)."""
    pd = _resolve_power_domain(powerDomainID)
    ao = getattr(pd, "always_on", None) if pd else None
    val = _expr(ao)
    return val if isinstance(val, str) else None


def getPowerDomainAlwaysOnID(powerDomainID: str) -> str | None:
    """Return handle of alwaysOn element (F.7.71.10)."""
    pd = _resolve_power_domain(powerDomainID)
    ao = getattr(pd, "always_on", None) if pd else None
    return get_handle(ao) if ao is not None else None


def getPowerDomainName(powerDomainID: str) -> str | None:
    """Return power domain name (F.7.71.11)."""
    pd = _resolve_power_domain(powerDomainID)
    return getattr(pd, "name", None) if pd else None


def getPowerDomainSubDomainOf(powerDomainID: str) -> str | None:
    """Return subDomainOf value (F.7.71.12)."""
    pd = _resolve_power_domain(powerDomainID)
    return getattr(pd, "sub_domain_of", None) if pd else None


def getPowerDomainSubDomainOfRefByID(powerDomainID: str) -> str | None:
    """Alias of getPowerDomainSubDomainOf (F.7.71.13)."""
    return getPowerDomainSubDomainOf(powerDomainID)


# ---------------------------------------------------------------------------
# EXTENDED (F.7.72)
# ---------------------------------------------------------------------------

def addComponentInstancePowerDomainLink(componentInstanceID: str, externalRefExpression: str | None = None) -> str:
    """Append powerDomainLink to component instance (F.7.72.1)."""
    inst = resolve_handle(componentInstanceID)
    if inst is None:
        raise TgiError("Invalid component instance handle", TgiFaultCode.INVALID_ID)
    links = getattr(inst, "power_domain_links", None)
    if links is None:
        links = SchemaPowerDomainLinks()
        inst.power_domain_links = links  # type: ignore[attr-defined]
    link = PDL.PowerDomainLink()  # type: ignore[attr-defined]
    if externalRefExpression is not None:
        link.external_power_domain_reference = externalRefExpression  # type: ignore[attr-defined]
    links.power_domain_link.append(link)  # type: ignore[attr-defined]
    register_parent(link, inst, ("power_domain_links",), "list")
    return get_handle(link)


def addComponentPowerDomain(componentID: str, name: str) -> str:
    """Create powerDomain under component (F.7.72.2)."""
    comp = _resolve_component(componentID)
    if comp is None:
        raise TgiError("Invalid component handle", TgiFaultCode.INVALID_ID)
    if comp.power_domains is None:
        comp.power_domains = ComponentType.PowerDomains()  # type: ignore[attr-defined]
    for existing in getattr(comp.power_domains, "power_domain", []):  # type: ignore[attr-defined]
        if getattr(existing, "name", None) == name:
            raise TgiError("Power domain name already exists", TgiFaultCode.ALREADY_EXISTS)
    pd = ComponentType.PowerDomains.PowerDomain(name=name)  # type: ignore[attr-defined]
    comp.power_domains.power_domain.append(pd)  # type: ignore[attr-defined]
    register_parent(pd, comp, ("power_domains",), "list")
    return get_handle(pd)


def addPortTransactionalPowerConstraint(portID: str, powerDomainRef: str | None = None) -> str:
    """Add transactional powerConstraint (F.7.72.3)."""
    p = _resolve_port(portID)
    if p is None or not isinstance(getattr(p, "transactional", None), PortTransactionalType):
        raise TgiError("Invalid transactional port handle", TgiFaultCode.INVALID_ID)
    tx = p.transactional  # type: ignore[attr-defined]
    if getattr(tx, "power_constraints", None) is None:
        tx.power_constraints = PortTransactionalType.PowerConstraints()  # type: ignore[attr-defined]
    pc = TransactionalPowerConstraintType()
    if powerDomainRef is not None:
        pc.power_domain_ref = powerDomainRef  # type: ignore[attr-defined]
    tx.power_constraints.power_constraint.append(pc)  # type: ignore[attr-defined]
    register_parent(pc, p, ("transactional", "power_constraints"), "list")
    return get_handle(pc)


def addPortWirePowerConstraint(portID: str, powerDomainRef: str | None = None) -> str:
    """Add wire powerConstraint (F.7.72.4)."""
    p = _resolve_port(portID)
    if p is None or not isinstance(getattr(p, "wire", None), PortWireType):
        raise TgiError("Invalid wire port handle", TgiFaultCode.INVALID_ID)
    wire = p.wire  # type: ignore[attr-defined]
    if getattr(wire, "power_constraints", None) is None:
        wire.power_constraints = PortWireType.PowerConstraints()  # type: ignore[attr-defined]
    pc = WirePowerConstraintType()
    if powerDomainRef is not None:
        pc.power_domain_ref = powerDomainRef  # type: ignore[attr-defined]
    wire.power_constraints.power_constraint.append(pc)  # type: ignore[attr-defined]
    register_parent(pc, p, ("wire", "power_constraints"), "list")
    return get_handle(pc)


def addPowerDomainLinkInternalPowerDomainReference(powerDomainLinkID: str, internalRefExpression: str) -> str:
    """Add internalPowerDomainReference (F.7.72.5)."""
    link = resolve_handle(powerDomainLinkID)
    if not isinstance(link, PDL.PowerDomainLink):  # type: ignore[attr-defined]
        raise TgiError("Invalid powerDomainLink handle", TgiFaultCode.INVALID_ID)
    ref_obj = PDL.PowerDomainLink.InternalPowerDomainReference(value=internalRefExpression)  # type: ignore[attr-defined]
    link.internal_power_domain_reference.append(ref_obj)  # type: ignore[attr-defined]
    register_parent(ref_obj, link, ("internal_power_domain_reference",), "list")
    return get_handle(ref_obj)


def removeComponentInstancePowerDomainLink(powerDomainLinkID: str) -> bool:
    """Remove powerDomainLink (F.7.72.6)."""
    link = resolve_handle(powerDomainLinkID)
    if not isinstance(link, PDL.PowerDomainLink):  # type: ignore[attr-defined]
        raise TgiError("Invalid powerDomainLink handle", TgiFaultCode.INVALID_ID)
    return detach_child_by_handle(powerDomainLinkID)


def removeComponentPowerDomain(powerDomainID: str) -> bool:
    """Remove component powerDomain (F.7.72.7)."""
    pd = _resolve_power_domain(powerDomainID)
    if pd is None:
        raise TgiError("Invalid power domain handle", TgiFaultCode.INVALID_ID)
    return detach_child_by_handle(powerDomainID)


def removePowerConstraintRange(powerConstraintID: str) -> bool:
    """Remove range from powerConstraint (F.7.72.8)."""
    c = _resolve_wire_constraint(powerConstraintID)
    if c is None:
        # Transactional constraints never have range; treat as invalid ID
        if _resolve_tx_constraint(powerConstraintID) is not None:
            return False
        raise TgiError("Invalid powerConstraint handle", TgiFaultCode.INVALID_ID)
    if getattr(c, "range", None) is None:
        return False
    c.range = None  # type: ignore[attr-defined]
    return True


def removePowerDomainLinkInternalPowerDomainRef(powerDomainLinkID: str, internalRefExpression: str) -> bool:
    """Remove an internalPowerDomainReference by expression or ID (F.7.72.9)."""
    link = resolve_handle(powerDomainLinkID)
    if not isinstance(link, PDL.PowerDomainLink):  # type: ignore[attr-defined]
        raise TgiError("Invalid powerDomainLink handle", TgiFaultCode.INVALID_ID)
    # Allow handle
    ref_obj = resolve_handle(internalRefExpression)
    if ref_obj and isinstance(ref_obj, PDL.PowerDomainLink.InternalPowerDomainReference):  # type: ignore[attr-defined]
        # remove by handle
        return detach_child_by_handle(internalRefExpression)
    # Fall back to expression match
    refs = list(getattr(link, "internal_power_domain_reference", []))
    for r in refs:
        if getattr(r, "value", None) == internalRefExpression:
            refs.remove(r)
            link.internal_power_domain_reference = refs  # type: ignore[attr-defined]
            return True
    return False


def removePowerDomainSubDomainOf(powerDomainID: str) -> bool:
    """Clear subDomainOf (F.7.72.10)."""
    pd = _resolve_power_domain(powerDomainID)
    if pd is None:
        raise TgiError("Invalid power domain handle", TgiFaultCode.INVALID_ID)
    if getattr(pd, "sub_domain_of", None) is None:
        return False
    pd.sub_domain_of = None  # type: ignore[attr-defined]
    return True


def setPowerConstraintPowerDomainRef(powerConstraintID: str, powerDomainName: str) -> bool:
    """Set powerDomainRef (F.7.72.11)."""
    c = _resolve_wire_constraint(powerConstraintID) or _resolve_tx_constraint(powerConstraintID)
    if c is None:
        raise TgiError("Invalid powerConstraint handle", TgiFaultCode.INVALID_ID)
    c.power_domain_ref = powerDomainName  # type: ignore[attr-defined]
    return True


def setPowerConstraintRange(powerConstraintID: str, left_expr: str, right_expr: str) -> bool:
    """Create or update range (wire only) (F.7.72.12)."""
    c = _resolve_wire_constraint(powerConstraintID)
    if c is None:
        if _resolve_tx_constraint(powerConstraintID) is not None:
            raise TgiError("Transactional powerConstraint has no range", TgiFaultCode.INVALID_ARGUMENT)
        raise TgiError("Invalid powerConstraint handle", TgiFaultCode.INVALID_ID)
    if c.range is None:  # type: ignore[attr-defined]
        c.range = Range(left=Left(value=left_expr), right=Right(value=right_expr))  # type: ignore[attr-defined]
    else:
        if c.range.left is None:
            c.range.left = Left(value=left_expr)
        else:
            c.range.left.value = left_expr
        if c.range.right is None:
            c.range.right = Right(value=right_expr)
        else:
            c.range.right.value = right_expr
    return True


def setPowerDomainAlwaysOn(powerDomainID: str, expression: str | bool) -> bool:
    """Set alwaysOn (boolean or expression) (F.7.72.13)."""
    pd = _resolve_power_domain(powerDomainID)
    if pd is None:
        raise TgiError("Invalid power domain handle", TgiFaultCode.INVALID_ID)
    if isinstance(expression, AlwaysOn):
        pd.always_on = expression  # type: ignore[attr-defined]
    else:
        pd.always_on = AlwaysOn(value=expression)  # type: ignore[attr-defined]
    return True


def setPowerDomainSubDomainOf(powerDomainID: str, parentName: str) -> bool:
    """Set subDomainOf (F.7.72.14)."""
    pd = _resolve_power_domain(powerDomainID)
    if pd is None:
        raise TgiError("Invalid power domain handle", TgiFaultCode.INVALID_ID)
    pd.sub_domain_of = parentName  # type: ignore[attr-defined]
    return True

