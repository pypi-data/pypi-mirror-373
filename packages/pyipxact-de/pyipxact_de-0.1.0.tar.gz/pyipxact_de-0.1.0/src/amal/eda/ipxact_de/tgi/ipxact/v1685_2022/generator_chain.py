"""Generator chain category TGI functions (IEEE 1685-2022).

Implements exactly BASE (F.7.51) and EXTENDED (F.7.52) Generator chain
functions. These cover traversal of chain groups, selectors, choices,
and mutation of chain group, selector, generator and choice elements.
Error handling: INVALID_ID for bad handles; INVALID_ARGUMENT for
semantic violations.
"""
# ruff: noqa: I001
# NOTE: Direct GeneratorChain / Generator class imports not required here;
# specific schema types imported below from their defining modules.
from org.accellera.ipxact.v1685_2022.generator_chain import GeneratorChain as SchemaGeneratorChain
from org.accellera.ipxact.v1685_2022.generator_selector_type import GeneratorSelectorType
from org.accellera.ipxact.v1685_2022.group_selector import GroupSelector
from org.accellera.ipxact.v1685_2022.configurable_library_ref_type import ConfigurableLibraryRefType
from org.accellera.ipxact.v1685_2022.choices import Choices
from org.accellera.ipxact.v1685_2022.generator_type import GeneratorType
from org.accellera.ipxact.v1685_2022.ipxact_uri import IpxactUri
from org.accellera.ipxact.v1685_2022.group_selector_multiple_group_selection_operator import (
    GroupSelectorMultipleGroupSelectionOperator,
)

from .core import (
    TgiError,
    TgiFaultCode,
    resolve_handle,
    get_handle,
    register_parent,
    detach_child_by_handle,
)

__all__ = [
    # BASE (F.7.51)
    "getComponentGeneratorSelectorGroupSelectorID",
    "getGeneratorChainChainGroupIDs",
    "getGeneratorChainChoiceIDs",
    "getGeneratorChainComponentGeneratorSelectorIDs",
    "getGeneratorChainGeneratorChainSelectorIDs",
    "getGeneratorChainGeneratorIDs",
    "getGeneratorChainSelectorGeneratorChainRefByID",
    "getGeneratorChainSelectorGeneratorChainRefByVLNV",
    "getGeneratorChainSelectorGroupSelectorID",
    "getGroupSelectorNameIDs",
    "getGroupSelectorSelectionNames",
    "getGroupSelectorSelectionOperator",
    # EXTENDED (F.7.52)
    "addGeneratorChainChainGroup",
    "addGeneratorChainChoice",
    "addGeneratorChainComponentGeneratorSelector",
    "addGeneratorChainGenerator",
    "addGeneratorChainGeneratorChainSelector",
    "addGroupSelectorName",
    "removeGeneratorChainChainGroup",
    "removeGeneratorChainChoice",
    "removeGeneratorChainComponentGeneratorSelector",
    "removeGeneratorChainGenerator",
    "removeGeneratorChainGeneratorChainSelector",
    "removeGroupSelectorName",
    "setComponentGeneratorSelectorGroupSelector",
    "setGeneratorChainSelectorGeneratorChainRef",
    "setGeneratorChainSelectorGroupSelector",
]


# ---------------------------------------------------------------------------
# Helpers (non-spec)
# ---------------------------------------------------------------------------

def _resolve_chain(chainID: str) -> SchemaGeneratorChain | None:
    obj = resolve_handle(chainID)
    return obj if isinstance(obj, SchemaGeneratorChain) else None


def _resolve_chain_selector(selectorID: str) -> SchemaGeneratorChain.GeneratorChainSelector | None:
    obj = resolve_handle(selectorID)
    return obj if isinstance(obj, SchemaGeneratorChain.GeneratorChainSelector) else None


def _resolve_component_generator_selector(selID: str) -> GeneratorSelectorType | None:
    obj = resolve_handle(selID)
    return obj if isinstance(obj, GeneratorSelectorType) else None


def _resolve_group_selector(gsID: str) -> GroupSelector | None:
    obj = resolve_handle(gsID)
    return obj if isinstance(obj, GroupSelector) else None


def _resolve_group_selector_name(nameID: str) -> GroupSelector.Name | None:
    obj = resolve_handle(nameID)
    return obj if isinstance(obj, GroupSelector.Name) else None


def _resolve_choice(choiceID: str) -> Choices.Choice | None:
    obj = resolve_handle(choiceID)
    return obj if isinstance(obj, Choices.Choice) else None


# ---------------------------------------------------------------------------
# BASE (F.7.51)
# ---------------------------------------------------------------------------

def getComponentGeneratorSelectorGroupSelectorID(componentGeneratorSelectorID: str) -> str | None:
    """Return handle of groupSelector of a componentGeneratorSelector.

    Section: F.7.51.1.
    """
    sel = _resolve_component_generator_selector(componentGeneratorSelectorID)
    if sel is None:
        raise TgiError("Invalid componentGeneratorSelector handle", TgiFaultCode.INVALID_ID)
    gs = sel.group_selector
    return None if gs is None else get_handle(gs)


def getGeneratorChainChainGroupIDs(generatorChainID: str) -> list[str]:
    """Return handles of all chainGroup elements.

    Section: F.7.51.2.
    """
    chain = _resolve_chain(generatorChainID)
    if chain is None:
        raise TgiError("Invalid generatorChain handle", TgiFaultCode.INVALID_ID)
    return [get_handle(g) for g in getattr(chain, "chain_group", [])]


def getGeneratorChainChoiceIDs(generatorChainID: str) -> list[str]:
    """Return handles of all choice elements.

    Section: F.7.51.3.
    """
    chain = _resolve_chain(generatorChainID)
    if chain is None:
        raise TgiError("Invalid generatorChain handle", TgiFaultCode.INVALID_ID)
    if chain.choices is None:
        return []
    return [get_handle(c) for c in getattr(chain.choices, "choice", [])]


def getGeneratorChainComponentGeneratorSelectorIDs(generatorChainID: str) -> list[str]:
    """Return handles of componentGeneratorSelector elements.

    Section: F.7.51.4.
    """
    chain = _resolve_chain(generatorChainID)
    if chain is None:
        raise TgiError("Invalid generatorChain handle", TgiFaultCode.INVALID_ID)
    return [get_handle(c) for c in getattr(chain, "component_generator_selector", [])]


def getGeneratorChainGeneratorChainSelectorIDs(generatorChainID: str) -> list[str]:
    """Return handles of generatorChainSelector elements.

    Section: F.7.51.5.
    """
    chain = _resolve_chain(generatorChainID)
    if chain is None:
        raise TgiError("Invalid generatorChain handle", TgiFaultCode.INVALID_ID)
    return [get_handle(c) for c in getattr(chain, "generator_chain_selector", [])]


def getGeneratorChainGeneratorIDs(generatorChainID: str) -> list[str]:
    """Return handles of generator child elements.

    Section: F.7.51.6.
    """
    chain = _resolve_chain(generatorChainID)
    if chain is None:
        raise TgiError("Invalid generatorChain handle", TgiFaultCode.INVALID_ID)
    return [get_handle(g) for g in getattr(chain, "generator", [])]


def getGeneratorChainSelectorGeneratorChainRefByID(generatorChainSelectorID: str) -> str | None:
    """Return handle of referenced generatorChain (generatorChainRef).

    Section: F.7.51.7.
    """
    sel = _resolve_chain_selector(generatorChainSelectorID)
    if sel is None:
        raise TgiError("Invalid generatorChainSelector handle", TgiFaultCode.INVALID_ID)
    ref = sel.generator_chain_ref
    return None if ref is None else get_handle(ref)


def getGeneratorChainSelectorGeneratorChainRefByVLNV(
    generatorChainSelectorID: str,
) -> tuple[str | None, str | None, str | None, str | None]:
    """Return VLNV tuple of referenced generatorChain.

    Section: F.7.51.8.
    """
    sel = _resolve_chain_selector(generatorChainSelectorID)
    if sel is None:
        raise TgiError("Invalid generatorChainSelector handle", TgiFaultCode.INVALID_ID)
    ref = sel.generator_chain_ref
    if ref is None:
        return (None, None, None, None)
    return (ref.vendor, ref.library, ref.name, ref.version)


def getGeneratorChainSelectorGroupSelectorID(generatorChainSelectorID: str) -> str | None:
    """Return handle of groupSelector element on a generatorChainSelector.

    Section: F.7.51.9.
    """
    sel = _resolve_chain_selector(generatorChainSelectorID)
    if sel is None:
        raise TgiError("Invalid generatorChainSelector handle", TgiFaultCode.INVALID_ID)
    gs = sel.group_selector
    return None if gs is None else get_handle(gs)


def getGroupSelectorNameIDs(groupSelectorID: str) -> list[str]:
    """Return handles of all Name elements within a groupSelector.

    Section: F.7.51.10.
    """
    gs = _resolve_group_selector(groupSelectorID)
    if gs is None:
        raise TgiError("Invalid groupSelector handle", TgiFaultCode.INVALID_ID)
    return [get_handle(n) for n in getattr(gs, "name", [])]


def getGroupSelectorSelectionNames(groupSelectorID: str) -> list[str]:
    """Return list of name values in a groupSelector.

    Section: F.7.51.11.
    """
    gs = _resolve_group_selector(groupSelectorID)
    if gs is None:
        raise TgiError("Invalid groupSelector handle", TgiFaultCode.INVALID_ID)
    return [getattr(n, "value", "") for n in getattr(gs, "name", [])]


def getGroupSelectorSelectionOperator(groupSelectorID: str) -> str | None:
    """Return multipleGroupSelectionOperator value.

    Section: F.7.51.12.
    """
    gs = _resolve_group_selector(groupSelectorID)
    if gs is None:
        raise TgiError("Invalid groupSelector handle", TgiFaultCode.INVALID_ID)
    op = getattr(gs, "multiple_group_selection_operator", None)
    return None if op is None else op.value


# ---------------------------------------------------------------------------
# EXTENDED (F.7.52)
# ---------------------------------------------------------------------------

def addGeneratorChainChainGroup(generatorChainID: str, group: str) -> bool:
    """Add a chainGroup value to a generatorChain.

    Section: F.7.52.1.
    """
    chain = _resolve_chain(generatorChainID)
    if chain is None:
        raise TgiError("Invalid generatorChain handle", TgiFaultCode.INVALID_ID)
    grp = SchemaGeneratorChain.ChainGroup(value=group)
    chain.chain_group.append(grp)  # type: ignore[attr-defined]
    register_parent(grp, chain, ("chain_group",), "list")
    return True


def addGeneratorChainChoice(generatorChainID: str, name: str, enumerations: list[str]) -> str:
    """Add a choice with enumerations to a generatorChain.

    Section: F.7.52.2.
    """
    chain = _resolve_chain(generatorChainID)
    if chain is None:
        raise TgiError("Invalid generatorChain handle", TgiFaultCode.INVALID_ID)
    if chain.choices is None:
        chain.choices = Choices()  # type: ignore[arg-type]
    choice = Choices.Choice(name=name)
    for e in enumerations:
        choice.enumeration.append(Choices.Choice.Enumeration(value=e))  # type: ignore[attr-defined]
    chain.choices.choice.append(choice)  # type: ignore[attr-defined]
    register_parent(choice, chain, ("choices",), "list")
    return get_handle(choice)


def addGeneratorChainComponentGeneratorSelector(generatorChainID: str, name: str) -> str:
    """Add a componentGeneratorSelector (with groupSelector names) to chain.

    Section: F.7.52.3.
    """
    chain = _resolve_chain(generatorChainID)
    if chain is None:
        raise TgiError("Invalid generatorChain handle", TgiFaultCode.INVALID_ID)
    gs = GroupSelector(name=[GroupSelector.Name(value=name)])  # type: ignore[arg-type]
    sel = GeneratorSelectorType(group_selector=gs)
    chain.component_generator_selector.append(sel)  # type: ignore[attr-defined]
    register_parent(sel, chain, ("component_generator_selector",), "list")
    register_parent(gs, sel, ("group_selector",), "single")
    return get_handle(sel)


def addGeneratorChainGenerator(generatorChainID: str, name: str, generatorExecutable: str) -> str:
    """Add a generator (name + executable path) to chain.

    Section: F.7.52.4.
    """
    chain = _resolve_chain(generatorChainID)
    if chain is None:
        raise TgiError("Invalid generatorChain handle", TgiFaultCode.INVALID_ID)
    gen = GeneratorType(name=name, generator_exe=IpxactUri(value=generatorExecutable))  # type: ignore[arg-type]
    # Wrap into Generator (alias class) if schema uses subclass, else use GeneratorType directly
    gen_obj = GeneratorType(name=gen.name, generator_exe=gen.generator_exe)  # type: ignore[arg-type]
    chain.generator.append(gen_obj)  # type: ignore[attr-defined]
    register_parent(gen_obj, chain, ("generator",), "list")
    return get_handle(gen_obj)


def addGeneratorChainGeneratorChainSelector(generatorChainID: str, name: str) -> str:
    """Add a generatorChainSelector with groupSelector name placeholder.

    Section: F.7.52.5.
    """
    chain = _resolve_chain(generatorChainID)
    if chain is None:
        raise TgiError("Invalid generatorChain handle", TgiFaultCode.INVALID_ID)
    sel = SchemaGeneratorChain.GeneratorChainSelector()
    # Add group selector with provided name
    gs = GroupSelector(name=[GroupSelector.Name(value=name)])  # type: ignore[arg-type]
    sel.group_selector = gs  # type: ignore[assignment]
    chain.generator_chain_selector.append(sel)  # type: ignore[attr-defined]
    register_parent(sel, chain, ("generator_chain_selector",), "list")
    register_parent(gs, sel, ("group_selector",), "single")
    return get_handle(sel)


def addGroupSelectorName(groupSelectorID: str, name: str) -> str:
    """Append a Name to groupSelector.

    Section: F.7.52.6.
    """
    gs = _resolve_group_selector(groupSelectorID)
    if gs is None:
        raise TgiError("Invalid groupSelector handle", TgiFaultCode.INVALID_ID)
    nm = GroupSelector.Name(value=name)
    gs.name.append(nm)  # type: ignore[attr-defined]
    register_parent(nm, gs, ("name",), "list")
    return get_handle(nm)


def removeGeneratorChainChainGroup(chainGroupID: str) -> bool:
    """Remove a chainGroup element.

    Section: F.7.52.7.
    """
    return detach_child_by_handle(chainGroupID)


def removeGeneratorChainChoice(choiceID: str) -> bool:
    """Remove a choice element.

    Section: F.7.52.8.
    """
    return detach_child_by_handle(choiceID)


def removeGeneratorChainComponentGeneratorSelector(componentGeneratorSelectorID: str) -> bool:
    """Remove a componentGeneratorSelector element.

    Section: F.7.52.9.
    """
    return detach_child_by_handle(componentGeneratorSelectorID)


def removeGeneratorChainGenerator(generatorID: str) -> bool:
    """Remove a generator element.

    Section: F.7.52.10.
    """
    return detach_child_by_handle(generatorID)


def removeGeneratorChainGeneratorChainSelector(generatorChainSelectorID: str) -> bool:
    """Remove a generatorChainSelector element.

    Section: F.7.52.11.
    """
    return detach_child_by_handle(generatorChainSelectorID)


def removeGroupSelectorName(groupSelectorNameID: str) -> bool:
    """Remove a Name element from a groupSelector.

    Section: F.7.52.12.
    """
    return detach_child_by_handle(groupSelectorNameID)


def setComponentGeneratorSelectorGroupSelector(componentGeneratorSelectorID: str, names: list[str]) -> bool:
    """Set groupSelector (names list) on componentGeneratorSelector.

    Section: F.7.52.13. Replaces any existing groupSelector.
    """
    sel = _resolve_component_generator_selector(componentGeneratorSelectorID)
    if sel is None:
        raise TgiError("Invalid componentGeneratorSelector handle", TgiFaultCode.INVALID_ID)
    gs = GroupSelector(name=[GroupSelector.Name(value=n) for n in names])  # type: ignore[arg-type]
    sel.group_selector = gs  # type: ignore[assignment]
    register_parent(gs, sel, ("group_selector",), "single")
    return True


def setGeneratorChainSelectorGeneratorChainRef(
    generatorChainSelectorID: str,
    generatorChainVLNV: tuple[str, str, str, str],
) -> bool:
    """Set generatorChainRef VLNV on a generatorChainSelector.

    Section: F.7.52.14.
    """
    sel = _resolve_chain_selector(generatorChainSelectorID)
    if sel is None:
        raise TgiError("Invalid generatorChainSelector handle", TgiFaultCode.INVALID_ID)
    sel.generator_chain_ref = ConfigurableLibraryRefType(
        vendor=generatorChainVLNV[0],
        library=generatorChainVLNV[1],
        name=generatorChainVLNV[2],
        version=generatorChainVLNV[3],
    )
    return True


def setGeneratorChainSelectorGroupSelector(
    generatorChainSelectorID: str,
    names: list[str],
    operator: str | None = None,
) -> bool:
    """Set groupSelector (names + optional operator) on generatorChainSelector.

    Section: F.7.52.15.
    """
    sel = _resolve_chain_selector(generatorChainSelectorID)
    if sel is None:
        raise TgiError("Invalid generatorChainSelector handle", TgiFaultCode.INVALID_ID)
    gs = GroupSelector(name=[GroupSelector.Name(value=n) for n in names])  # type: ignore[arg-type]
    if operator is not None:
        try:
            gs.multiple_group_selection_operator = GroupSelectorMultipleGroupSelectionOperator(operator)  # type: ignore[assignment]
        except ValueError as exc:
            raise TgiError("Unknown selection operator", TgiFaultCode.INVALID_ARGUMENT) from exc
    sel.group_selector = gs  # type: ignore[assignment]
    register_parent(gs, sel, ("group_selector",), "single")
    return True
