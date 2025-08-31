# ruff: noqa: I001
"""Instantiation category TGI functions (IEEE 1685-2022).

Implements BASE (F.7.55) and EXTENDED (F.7.56) Instantiation functions. These
cover getter, add, remove and set operations for:

* ``componentInstantiation`` (attributes, nested refs and lists)
* ``designConfigurationInstantiation`` (language + designConfigurationRef)
* abstractionType / abstractorInstance / componentInstance reference helper
  getters used elsewhere in traversal APIs

Error handling matches the common TGI pattern: invalid handles raise
``TgiError`` with ``TgiFaultCode.INVALID_ID``; semantic violations (e.g. wrong
handle kind for an operation) raise ``INVALID_ARGUMENT``. Absent optional
elements simply return ``None`` or an empty list as appropriate per Annex F.
All functions implemented here are ONLY those enumerated in sections F.7.55 and
F.7.56 (no more, no less).
"""
from __future__ import annotations

from org.accellera.ipxact.v1685_2022 import (
    ComponentInstance,
    ComponentInstantiationType,
    DesignConfigurationInstantiationType,
)
from org.accellera.ipxact.v1685_2022.clearbox_element_ref_type import ClearboxElementRefType
from org.accellera.ipxact.v1685_2022.constraint_set_ref import ConstraintSetRef
from org.accellera.ipxact.v1685_2022.file_builder_type import FileBuilderType
from org.accellera.ipxact.v1685_2022.file_set_ref import FileSetRef
from org.accellera.ipxact.v1685_2022.language_type import LanguageType
from org.accellera.ipxact.v1685_2022.configurable_library_ref_type import ConfigurableLibraryRefType

from .core import (
    TgiError,
    TgiFaultCode,
    resolve_handle,
    get_handle,
    register_parent,
    detach_child_by_handle,
)

__all__ = [
    # BASE (F.7.55)
    "getAbstractionTypeAbstractionRefID",
    "getAbstractorInstanceAbstractorRefID",
    "getComponentInstanceComponentRefID",
    "getComponentInstantiationArchitectureName",
    "getComponentInstantiationClearboxElementRefIDs",
    "getComponentInstantiationConfigurationName",
    "getComponentInstantiationConstraintSetRefIDs",
    "getComponentInstantiationDefaultFileBuilderIDs",
    "getComponentInstantiationFileSetRefIDs",
    "getComponentInstantiationIsVirtual",
    "getComponentInstantiationLanguage",
    "getComponentInstantiationLanguageID",
    "getComponentInstantiationLibraryName",
    "getComponentInstantiationModuleName",
    "getComponentInstantiationPackageName",
    "getDesignConfigurationInstantiationDesignConfigurationRefByID",
    "getDesignConfigurationInstantiationDesignConfigurationRefByVLNV",
    "getDesignConfigurationInstantiationDesignConfigurationRefID",
    "getDesignConfigurationInstantiationLanguage",
    "getDesignConfigurationInstantiationLanguageID",
    # EXTENDED (F.7.56)
    "addComponentInstantiationClearboxElementRef",
    "addComponentInstantiationConstraintSetRef",
    "addComponentInstantiationDefaultFileBuilder",
    "addComponentInstantiationFileSetRef",
    "removeComponentInstantiationArchitectureName",
    "removeComponentInstantiationClearboxElementRef",
    "removeComponentInstantiationConfigurationName",
    "removeComponentInstantiationConstraintSetRef",
    "removeComponentInstantiationDefaultFileBuilder",
    "removeComponentInstantiationFileSetRef",
    "removeComponentInstantiationIsVirtual",
    "removeComponentInstantiationLanguage",
    "removeComponentInstantiationLibraryName",
    "removeComponentInstantiationModuleName",
    "removeComponentInstantiationPackageName",
    "removeDesignConfigurationInstantiationLanguage",
    "setComponentInstantiationArchitectureName",
    "setComponentInstantiationConfigurationName",
    "setComponentInstantiationIsVirtual",
    "setComponentInstantiationLanguage",
    "setComponentInstantiationLibraryName",
    "setComponentInstantiationModuleName",
    "setComponentInstantiationPackageName",
    "setDesignConfigurationInstantiationDesignConfigurationRef",
    "setDesignConfigurationInstantiationLanguage",
]


# ---------------------------------------------------------------------------
# Helpers (non-spec)
# ---------------------------------------------------------------------------

def _resolve_component_instantiation(handle: str) -> ComponentInstantiationType | None:
    obj = resolve_handle(handle)
    return obj if isinstance(obj, ComponentInstantiationType) else None


def _resolve_design_config_instantiation(handle: str) -> DesignConfigurationInstantiationType | None:
    obj = resolve_handle(handle)
    return obj if isinstance(obj, DesignConfigurationInstantiationType) else None


def _require(obj, fault=TgiFaultCode.INVALID_ID):  # pragma: no cover - trivial
    # Wrapper to standardize None checking.
    if obj is None:
        raise TgiError("Invalid ID", fault)
    return obj


# ---------------------------------------------------------------------------
# BASE (F.7.55)
# ---------------------------------------------------------------------------

def getAbstractionTypeAbstractionRefID(abstractionTypeID: str) -> str | None:
    """Return handle of ``abstractionRef`` inside an abstractionType.

    Section: F.7.55.1. Returns None if absent.
    """
    at = resolve_handle(abstractionTypeID)
    from org.accellera.ipxact.v1685_2022.abstraction_types import AbstractionTypes

    if not isinstance(at, AbstractionTypes.AbstractionType):  # type: ignore[attr-defined]
        raise TgiError("Invalid abstractionType handle", TgiFaultCode.INVALID_ID)
    ref = getattr(at, "abstraction_ref", None)
    return None if ref is None else get_handle(ref)


def getAbstractorInstanceAbstractorRefID(abstractorInstanceID: str) -> str | None:
    """Return handle of the ``abstractorRef`` of an abstractorInstance.

    Section: F.7.55.2.
    """
    ai = resolve_handle(abstractorInstanceID)
    # AbstractorInstance is a nested dataclass inside
    # DesignConfiguration.InterconnectionConfiguration.AbstractorInstances
    from org.accellera.ipxact.v1685_2022.design_configuration import DesignConfiguration

    AbstractorInstanceCls = (
        DesignConfiguration.InterconnectionConfiguration.AbstractorInstances.AbstractorInstance
    )
    if not isinstance(ai, AbstractorInstanceCls):
        raise TgiError("Invalid abstractorInstance handle", TgiFaultCode.INVALID_ID)
    ref = getattr(ai, "abstractor_ref", None)
    return None if ref is None else get_handle(ref)


def getComponentInstanceComponentRefID(componentInstanceID: str) -> str | None:
    """Return handle of the ``componentRef`` inside a componentInstance.

    Section: F.7.55.3.
    """
    ci = resolve_handle(componentInstanceID)
    if not isinstance(ci, ComponentInstance):
        raise TgiError("Invalid componentInstance handle", TgiFaultCode.INVALID_ID)
    ref = getattr(ci, "component_ref", None)
    return None if ref is None else get_handle(ref)


def getComponentInstantiationArchitectureName(componentInstantiationID: str) -> str | None:
    """Return ``architectureName`` value.

    Section: F.7.55.4.
    """
    inst = _require(_resolve_component_instantiation(componentInstantiationID))
    return getattr(inst, "architecture_name", None)


def getComponentInstantiationClearboxElementRefIDs(componentInstantiationID: str) -> list[str]:
    """Return handles of all ``clearboxElementRef`` elements.

    Section: F.7.55.5.
    """
    inst = _require(_resolve_component_instantiation(componentInstantiationID))
    refs_container = getattr(inst, "clearbox_element_refs", None)
    if refs_container is None:
        return []
    return [get_handle(r) for r in getattr(refs_container, "clearbox_element_ref", [])]


def getComponentInstantiationConfigurationName(componentInstantiationID: str) -> str | None:
    """Return ``configurationName`` value.

    Section: F.7.55.6.
    """
    inst = _require(_resolve_component_instantiation(componentInstantiationID))
    return getattr(inst, "configuration_name", None)


def getComponentInstantiationConstraintSetRefIDs(componentInstantiationID: str) -> list[str]:
    """Return handles of ``constraintSetRef`` elements.

    Section: F.7.55.7.
    """
    inst = _require(_resolve_component_instantiation(componentInstantiationID))
    return [get_handle(r) for r in getattr(inst, "constraint_set_ref", [])]


def getComponentInstantiationDefaultFileBuilderIDs(componentInstantiationID: str) -> list[str]:
    """Return handles of ``defaultFileBuilder`` elements.

    Section: F.7.55.8.
    """
    inst = _require(_resolve_component_instantiation(componentInstantiationID))
    return [get_handle(fb) for fb in getattr(inst, "default_file_builder", [])]


def getComponentInstantiationFileSetRefIDs(componentInstantiationID: str) -> list[str]:
    """Return handles of ``fileSetRef`` elements.

    Section: F.7.55.9.
    """
    inst = _require(_resolve_component_instantiation(componentInstantiationID))
    return [get_handle(r) for r in getattr(inst, "file_set_ref", [])]


def getComponentInstantiationIsVirtual(componentInstantiationID: str) -> bool | None:
    """Return value of ``isVirtual``.

    Section: F.7.55.10.
    """
    inst = _require(_resolve_component_instantiation(componentInstantiationID))
    return getattr(inst, "is_virtual", None)


def getComponentInstantiationLanguage(componentInstantiationID: str) -> str | None:
    """Return language value (string) if present.

    Section: F.7.55.11.
    """
    inst = _require(_resolve_component_instantiation(componentInstantiationID))
    lang = getattr(inst, "language", None)
    if lang is None:
        return None
    return getattr(getattr(lang, "value", None), "value", None)  # LanguageType holds a ValueType


def getComponentInstantiationLanguageID(componentInstantiationID: str) -> str | None:
    """Return handle of the ``language`` element.

    Section: F.7.55.12.
    """
    inst = _require(_resolve_component_instantiation(componentInstantiationID))
    lang = getattr(inst, "language", None)
    return None if lang is None else get_handle(lang)


def getComponentInstantiationLibraryName(componentInstantiationID: str) -> str | None:
    """Return libraryName value.

    Section: F.7.55.13.
    """
    inst = _require(_resolve_component_instantiation(componentInstantiationID))
    return getattr(inst, "library_name", None)


def getComponentInstantiationModuleName(componentInstantiationID: str) -> str | None:
    """Return moduleName value.

    Section: F.7.55.14.
    """
    inst = _require(_resolve_component_instantiation(componentInstantiationID))
    return getattr(inst, "module_name", None)


def getComponentInstantiationPackageName(componentInstantiationID: str) -> str | None:
    """Return packageName value.

    Section: F.7.55.15.
    """
    inst = _require(_resolve_component_instantiation(componentInstantiationID))
    return getattr(inst, "package_name", None)


def getDesignConfigurationInstantiationDesignConfigurationRefByID(
    designConfigurationInstantiationID: str,
) -> str | None:
    """Return designConfigurationRef handle for a designConfigurationInstantiation.

    Section: F.7.55.16.
    """
    dci = _require(_resolve_design_config_instantiation(designConfigurationInstantiationID))
    ref = getattr(dci, "design_configuration_ref", None)
    return None if ref is None else get_handle(ref)


def getDesignConfigurationInstantiationDesignConfigurationRefByVLNV(
    designConfigurationInstantiationID: str,
) -> tuple[str | None, str | None, str | None, str | None]:
    """Return VLNV tuple of the designConfigurationRef.

    Section: F.7.55.17. Returns (None, None, None, None) if absent.
    """
    dci = _require(_resolve_design_config_instantiation(designConfigurationInstantiationID))
    ref = getattr(dci, "design_configuration_ref", None)
    if ref is None:
        return (None, None, None, None)
    return (ref.vendor, ref.library, ref.name, ref.version)


def getDesignConfigurationInstantiationDesignConfigurationRefID(designConfigurationInstantiationID: str) -> str | None:
    """Alias of F.7.55.16 (explicit naming per spec)."""
    return getDesignConfigurationInstantiationDesignConfigurationRefByID(designConfigurationInstantiationID)


def getDesignConfigurationInstantiationLanguage(designConfigurationInstantiationID: str) -> str | None:
    """Return language value of a designConfigurationInstantiation.

    Section: F.7.55.19.
    """
    dci = _require(_resolve_design_config_instantiation(designConfigurationInstantiationID))
    lang = getattr(dci, "language", None)
    if lang is None:
        return None
    return getattr(getattr(lang, "value", None), "value", None)


def getDesignConfigurationInstantiationLanguageID(designConfigurationInstantiationID: str) -> str | None:
    """Return handle of the language element.

    Section: F.7.55.20.
    """
    dci = _require(_resolve_design_config_instantiation(designConfigurationInstantiationID))
    lang = getattr(dci, "language", None)
    return None if lang is None else get_handle(lang)


# ---------------------------------------------------------------------------
# EXTENDED (F.7.56)
# ---------------------------------------------------------------------------

def addComponentInstantiationClearboxElementRef(componentInstantiationID: str, name: str, pathSegmentValue: str) -> str:
    """Add a ``clearboxElementRef`` element.

    Section: F.7.56.1.
    """
    inst = _require(_resolve_component_instantiation(componentInstantiationID))
    if inst.clearbox_element_refs is None:
        inst.clearbox_element_refs = ComponentInstantiationType.ClearboxElementRefs()  # type: ignore[attr-defined]
    # clearboxElementRefType has no path segment attribute in schema; ignore
    ref = ClearboxElementRefType(name=name)
    inst.clearbox_element_refs.clearbox_element_ref.append(ref)  # type: ignore[attr-defined]
    register_parent(ref, inst, ("clearbox_element_refs",), "list")
    return get_handle(ref)


def addComponentInstantiationConstraintSetRef(componentInstantiationID: str, localName: str) -> str:
    """Add a ``constraintSetRef``.

    Section: F.7.56.2.
    """
    inst = _require(_resolve_component_instantiation(componentInstantiationID))
    csr = ConstraintSetRef(local_name=localName)
    inst.constraint_set_ref.append(csr)  # type: ignore[attr-defined]
    register_parent(csr, inst, ("constraint_set_ref",), "list")
    return get_handle(csr)


def addComponentInstantiationDefaultFileBuilder(componentInstantiationID: str, fileType: str) -> str:
    """Add a ``defaultFileBuilder`` element.

    Section: F.7.56.3.
    """
    inst = _require(_resolve_component_instantiation(componentInstantiationID))
    # FileBuilderType requires FileType instance; minimal create
    from org.accellera.ipxact.v1685_2022.file_type import FileType
    from org.accellera.ipxact.v1685_2022.simple_file_type import SimpleFileType

    enum_val = None
    try:
        enum_val = SimpleFileType(fileType)
    except Exception:
        # Allow arbitrary user types via USER attribute if not matching enum
        if fileType:
            enum_val = SimpleFileType.USER
    fb = FileBuilderType(file_type=FileType(value=enum_val))
    inst.default_file_builder.append(fb)  # type: ignore[attr-defined]
    register_parent(fb, inst, ("default_file_builder",), "list")
    return get_handle(fb)


def addComponentInstantiationFileSetRef(componentInstantiationID: str, localName: str) -> str:
    """Add a ``fileSetRef`` element.

    Section: F.7.56.4.
    """
    inst = _require(_resolve_component_instantiation(componentInstantiationID))
    fsr = FileSetRef(local_name=localName)
    inst.file_set_ref.append(fsr)  # type: ignore[attr-defined]
    register_parent(fsr, inst, ("file_set_ref",), "list")
    return get_handle(fsr)


def removeComponentInstantiationArchitectureName(componentInstantiationID: str) -> bool:
    """Remove (clear) ``architectureName``.

    Section: F.7.56.5.
    """
    inst = _require(_resolve_component_instantiation(componentInstantiationID))
    inst.architecture_name = None
    return True


def removeComponentInstantiationClearboxElementRef(clearboxElementRefID: str) -> bool:
    """Remove a specific ``clearboxElementRef`` by handle.

    Section: F.7.56.6.
    """
    ref = resolve_handle(clearboxElementRefID)
    if not isinstance(ref, ClearboxElementRefType):
        raise TgiError("Invalid clearboxElementRef handle", TgiFaultCode.INVALID_ID)
    detach_child_by_handle(clearboxElementRefID)
    return True


def removeComponentInstantiationConfigurationName(componentInstantiationID: str) -> bool:
    """Clear ``configurationName``.

    Section: F.7.56.7.
    """
    inst = _require(_resolve_component_instantiation(componentInstantiationID))
    inst.configuration_name = None
    return True


def removeComponentInstantiationConstraintSetRef(constraintSetRefID: str) -> bool:
    """Remove a ``constraintSetRef`` by handle.

    Section: F.7.56.8.
    """
    csr = resolve_handle(constraintSetRefID)
    if not isinstance(csr, ConstraintSetRef):
        raise TgiError("Invalid constraintSetRef handle", TgiFaultCode.INVALID_ID)
    detach_child_by_handle(constraintSetRefID)
    return True


def removeComponentInstantiationDefaultFileBuilder(fileBuilderID: str) -> bool:
    """Remove a ``defaultFileBuilder`` by handle.

    Section: F.7.56.9.
    """
    fb = resolve_handle(fileBuilderID)
    if not isinstance(fb, FileBuilderType):
        raise TgiError("Invalid fileBuilder handle", TgiFaultCode.INVALID_ID)
    detach_child_by_handle(fileBuilderID)
    return True


def removeComponentInstantiationFileSetRef(fileSetRefID: str) -> bool:
    """Remove a ``fileSetRef``.

    Section: F.7.56.10.
    """
    fsr = resolve_handle(fileSetRefID)
    if not isinstance(fsr, FileSetRef):
        raise TgiError("Invalid fileSetRef handle", TgiFaultCode.INVALID_ID)
    detach_child_by_handle(fileSetRefID)
    return True


def removeComponentInstantiationIsVirtual(componentInstantiationID: str) -> bool:
    """Clear ``isVirtual`` element.

    Section: F.7.56.11.
    """
    inst = _require(_resolve_component_instantiation(componentInstantiationID))
    inst.is_virtual = None
    return True


def removeComponentInstantiationLanguage(componentInstantiationID: str) -> bool:
    """Remove ``language`` element.

    Section: F.7.56.12.
    """
    inst = _require(_resolve_component_instantiation(componentInstantiationID))
    inst.language = None
    return True


def removeComponentInstantiationLibraryName(componentInstantiationID: str) -> bool:
    """Clear ``libraryName``.

    Section: F.7.56.13.
    """
    inst = _require(_resolve_component_instantiation(componentInstantiationID))
    inst.library_name = None
    return True


def removeComponentInstantiationModuleName(componentInstantiationID: str) -> bool:
    """Clear ``moduleName``.

    Section: F.7.56.14.
    """
    inst = _require(_resolve_component_instantiation(componentInstantiationID))
    inst.module_name = None
    return True


def removeComponentInstantiationPackageName(componentInstantiationID: str) -> bool:
    """Clear ``packageName``.

    Section: F.7.56.15.
    """
    inst = _require(_resolve_component_instantiation(componentInstantiationID))
    inst.package_name = None
    return True


def removeDesignConfigurationInstantiationLanguage(designConfigurationInstantiationID: str) -> bool:
    """Remove language element from designConfigurationInstantiation.

    Section: F.7.56.16.
    """
    dci = _require(_resolve_design_config_instantiation(designConfigurationInstantiationID))
    dci.language = None
    return True


def setComponentInstantiationArchitectureName(componentInstantiationID: str, architectureName: str) -> bool:
    """Set ``architectureName``.

    Section: F.7.56.17.
    """
    inst = _require(_resolve_component_instantiation(componentInstantiationID))
    inst.architecture_name = architectureName
    return True


def setComponentInstantiationConfigurationName(componentInstantiationID: str, configurationName: str) -> bool:
    """Set ``configurationName``.

    Section: F.7.56.18.
    """
    inst = _require(_resolve_component_instantiation(componentInstantiationID))
    inst.configuration_name = configurationName
    return True


def setComponentInstantiationIsVirtual(componentInstantiationID: str, value: bool) -> bool:
    """Set ``isVirtual`` element value.

    Section: F.7.56.19.
    """
    inst = _require(_resolve_component_instantiation(componentInstantiationID))
    inst.is_virtual = value
    return True


def setComponentInstantiationLanguage(componentInstantiationID: str, language: str) -> bool:
    """Set language element (creates if absent).

    Section: F.7.56.20.
    """
    inst = _require(_resolve_component_instantiation(componentInstantiationID))
    lang = getattr(inst, "language", None)
    if lang is None:
        lang = LanguageType()
        inst.language = lang
        register_parent(lang, inst, tuple(), "single")
    if getattr(lang, "value", None) is None:
        # LanguageType.value is a nested simpleContent wrapper; emulate pattern used elsewhere
        class _V:  # minimal wrapper
            def __init__(self, value):
                self.value = value

        lang.value = _V(language)  # type: ignore[attr-defined]
    else:
        lang.value.value = language  # type: ignore[attr-defined]
    return True


def setComponentInstantiationLibraryName(componentInstantiationID: str, libraryName: str) -> bool:
    """Set ``libraryName``.

    Section: F.7.56.21.
    """
    inst = _require(_resolve_component_instantiation(componentInstantiationID))
    inst.library_name = libraryName
    return True


def setComponentInstantiationModuleName(componentInstantiationID: str, moduleName: str) -> bool:
    """Set ``moduleName``.

    Section: F.7.56.22.
    """
    inst = _require(_resolve_component_instantiation(componentInstantiationID))
    inst.module_name = moduleName
    return True


def setComponentInstantiationPackageName(componentInstantiationID: str, packageName: str) -> bool:
    """Set ``packageName``.

    Section: F.7.56.23.
    """
    inst = _require(_resolve_component_instantiation(componentInstantiationID))
    inst.package_name = packageName
    return True


def setDesignConfigurationInstantiationDesignConfigurationRef(
    designConfigurationInstantiationID: str, designConfigurationVLNV: tuple[str, str, str, str]
) -> bool:
    """Set the ``designConfigurationRef`` (creates if absent).

    Section: F.7.56.24.
    """
    dci = _require(_resolve_design_config_instantiation(designConfigurationInstantiationID))
    ref = getattr(dci, "design_configuration_ref", None)
    if ref is None:
        ref = ConfigurableLibraryRefType(
            vendor=designConfigurationVLNV[0],
            library=designConfigurationVLNV[1],
            name=designConfigurationVLNV[2],
            version=designConfigurationVLNV[3],
        )
        dci.design_configuration_ref = ref
        register_parent(ref, dci, tuple(), "single")
    else:
        ref.vendor, ref.library, ref.name, ref.version = designConfigurationVLNV
    return True


def setDesignConfigurationInstantiationLanguage(designConfigurationInstantiationID: str, language: str) -> bool:
    """Set language element for designConfigurationInstantiation.

    Section: F.7.56.25.
    """
    dci = _require(_resolve_design_config_instantiation(designConfigurationInstantiationID))
    lang = getattr(dci, "language", None)
    if lang is None:
        lang = LanguageType()
        dci.language = lang
        register_parent(lang, dci, tuple(), "single")
    if getattr(lang, "value", None) is None:
        class _V:  # simple wrapper as above
            def __init__(self, value):
                self.value = value

        lang.value = _V(language)  # type: ignore[attr-defined]
    else:
        lang.value.value = language  # type: ignore[attr-defined]
    return True

