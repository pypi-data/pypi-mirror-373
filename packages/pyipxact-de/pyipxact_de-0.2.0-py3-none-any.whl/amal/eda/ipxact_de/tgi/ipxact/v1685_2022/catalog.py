"""Catalog category TGI functions (IEEE 1685-2022).

Implements BASE (F.7.23) and EXTENDED (F.7.24) Catalog functions.

Catalogs provide traversal and manipulation of ipxactFile entries for all major
schema categories (abstractionDef, abstractors, busDefinitions, catalogs,
components, designConfigurations, designs, generatorChains, typeDefinitions).
BASE functions enumerate ipxactFile handles for each category and retrieve
element metadata. EXTENDED functions add/remove ipxactFile entries and set
element properties (name, VLNV reference).
"""

from collections.abc import Sequence

from org.accellera.ipxact.v1685_2022 import (
    Catalog,
    IpxactFilesType,
    IpxactFileType,
    IpxactUri,
    LibraryRefType,
)

from .core import get_handle

__all__ = [
    # BASE (F.7.23)
    "getCatalogAbstractionDefIpxactFileIDs",
    "getCatalogAbstractorsIpxactFileIDs",
    "getCatalogBusDefinitionsIpxactFileIDs",
    "getCatalogCatalogsIpxactFileIDs",
    "getCatalogComponentsIpxactFileIDs",
    "getCatalogDesignConfigurationsIpxactFileIDs",
    "getCatalogDesignsIpxactFileIDs",
    "getCatalogGeneratorChainsIpxactFileIDs",
    "getCatalogTypeDefinitionsIpxactFileIDs",
    "getIpxactFileName",
    "getIpxactFileVlnvRefByVLNV",
    # EXTENDED (F.7.24)
    "addCatalogAbstractionDefIpxactFile",
    "addCatalogAbstractorsIpxactFile",
    "addCatalogBusDefinitionsIpxactFile",
    "addCatalogCatalogsIpxactFile",
    "addCatalogComponentsIpxactFile",
    "addCatalogDesignConfigurationsIpxactFile",
    "addCatalogDesignsIpxactFile",
    "addCatalogGeneratorChainsIpxactFile",
    "addCatalogTypeDefinitionsIpxactFile",
    "removeCatalogAbstractionDefIpxactFile",
    "removeCatalogAbstractorsIpxactFile",
    "removeCatalogBusDefinitionsIpxactFile",
    "removeCatalogCatalogsIpxactFile",
    "removeCatalogComponentsIpxactFile",
    "removeCatalogDesignConfigurationsIpxactFile",
    "removeCatalogDesignsIpxactFile",
    "removeCatalogGeneratorChainsIpxactFile",
    "removeCatalogTypeDefinitionsIpxactFile",
    "setIpxactFileName",
    "setIpxactFileVlnv",
]


# ---------------------------------------------------------------------------
# Helpers (non-spec)
# ---------------------------------------------------------------------------

def _ensure_ipxact_files(container: IpxactFilesType | None) -> IpxactFilesType:
    return container if container is not None else IpxactFilesType()

def _list_handles(files: IpxactFilesType | None) -> list[str]:
    if files is None:
        return []
    return [get_handle(f) for f in files.ipxact_file]

def _remove_file_by_handle(files: IpxactFilesType | None, file_id: str) -> bool:
    if files is None:
        return False
    new_list = []
    removed = False
    for f in list(files.ipxact_file):
        if get_handle(f) == file_id and not removed:
            removed = True
            continue
        new_list.append(f)
    if removed:
        files.ipxact_file = new_list  # type: ignore[attr-defined]
    return removed

def _add_ipxact_file(
    files: IpxactFilesType | None,
    vlnv: Sequence[str],
    file_name: str,
) -> tuple[IpxactFilesType, IpxactFileType]:
    if len(vlnv) != 4:
        raise ValueError("VLNV must be vendor, library, name, version")
    container = _ensure_ipxact_files(files)
    new_file = IpxactFileType(
        vlnv=LibraryRefType(vendor=vlnv[0], library=vlnv[1], name=vlnv[2], version=vlnv[3]),
        name=IpxactUri(file_name),
    )
    current = list(container.ipxact_file)
    current.append(new_file)
    container.ipxact_file = current  # type: ignore[attr-defined]
    return container, new_file


# ---------------------------------------------------------------------------
# BASE (F.7.23)
# ---------------------------------------------------------------------------

def getCatalogAbstractionDefIpxactFileIDs(catalog: Catalog) -> list[str]:
    """Return handles of abstractionDefinition ipxactFile entries."""
    return _list_handles(getattr(catalog, "abstraction_definitions", None))

def getCatalogAbstractorsIpxactFileIDs(catalog: Catalog) -> list[str]:
    """Return handles of abstractors ipxactFile entries."""
    return _list_handles(getattr(catalog, "abstractors", None))

def getCatalogBusDefinitionsIpxactFileIDs(catalog: Catalog) -> list[str]:
    """Return handles of busDefinitions ipxactFile entries."""
    return _list_handles(getattr(catalog, "bus_definitions", None))

def getCatalogCatalogsIpxactFileIDs(catalog: Catalog) -> list[str]:
    """Return handles of catalogs ipxactFile entries."""
    return _list_handles(getattr(catalog, "catalogs", None))

def getCatalogComponentsIpxactFileIDs(catalog: Catalog) -> list[str]:
    """Return handles of components ipxactFile entries."""
    return _list_handles(getattr(catalog, "components", None))

def getCatalogDesignConfigurationsIpxactFileIDs(catalog: Catalog) -> list[str]:
    """Return handles of designConfigurations ipxactFile entries."""
    return _list_handles(getattr(catalog, "design_configurations", None))

def getCatalogDesignsIpxactFileIDs(catalog: Catalog) -> list[str]:
    """Return handles of designs ipxactFile entries."""
    return _list_handles(getattr(catalog, "designs", None))

def getCatalogGeneratorChainsIpxactFileIDs(catalog: Catalog) -> list[str]:
    """Return handles of generatorChains ipxactFile entries."""
    return _list_handles(getattr(catalog, "generator_chains", None))

def getCatalogTypeDefinitionsIpxactFileIDs(catalog: Catalog) -> list[str]:
    """Return handles of typeDefinitions ipxactFile entries."""
    return _list_handles(getattr(catalog, "type_definitions", None))

def getIpxactFileName(ipxact_file: IpxactFileType) -> str | None:
    """Return the file name of an ipxactFile entry."""
    return ipxact_file.name.value if ipxact_file.name is not None else None

def getIpxactFileVlnvRefByVLNV(ipxact_file: IpxactFileType) -> str | None:
    """Return the VLNV string (vendor:library:name:version) for an ipxactFile."""
    if ipxact_file.vlnv is None:
        return None
    v = ipxact_file.vlnv
    return f"{v.vendor}:{v.library}:{v.name}:{v.version}"


# ---------------------------------------------------------------------------
# EXTENDED (F.7.24)
# ---------------------------------------------------------------------------

def addCatalogAbstractionDefIpxactFile(
    catalog: Catalog,
    abstractionDefVLNV: Sequence[str],
    fileName: str,
) -> str:
    """Add an abstractionDefinition ipxactFile entry to the catalog.

    Args:
        catalog: Catalog handle object.
        abstractionDefVLNV: Sequence [vendor, library, name, version].
        fileName: Relative or absolute XML file name.

    Returns:
        Handle string of the created ipxactFile element.
    """
    catalog.abstraction_definitions, nf = _add_ipxact_file(
        getattr(catalog, "abstraction_definitions", None),
        abstractionDefVLNV,
        fileName,
    )
    return get_handle(nf)

def addCatalogAbstractorsIpxactFile(
    catalog: Catalog,
    abstractorVLNV: Sequence[str],
    fileName: str,
) -> str:
    """Add an abstractors ipxactFile entry to the catalog."""
    catalog.abstractors, nf = _add_ipxact_file(getattr(catalog, "abstractors", None), abstractorVLNV, fileName)
    return get_handle(nf)

def addCatalogBusDefinitionsIpxactFile(
    catalog: Catalog,
    busDefVLNV: Sequence[str],
    fileName: str,
) -> str:
    """Add a busDefinitions ipxactFile entry to the catalog."""
    catalog.bus_definitions, nf = _add_ipxact_file(getattr(catalog, "bus_definitions", None), busDefVLNV, fileName)
    return get_handle(nf)

def addCatalogCatalogsIpxactFile(
    catalog: Catalog,
    catalogVLNV: Sequence[str],
    fileName: str,
) -> str:
    """Add a catalogs ipxactFile entry to the catalog."""
    catalog.catalogs, nf = _add_ipxact_file(getattr(catalog, "catalogs", None), catalogVLNV, fileName)
    return get_handle(nf)

def addCatalogComponentsIpxactFile(
    catalog: Catalog,
    componentVLNV: Sequence[str],
    fileName: str,
) -> str:
    """Add a components ipxactFile entry to the catalog."""
    catalog.components, nf = _add_ipxact_file(getattr(catalog, "components", None), componentVLNV, fileName)
    return get_handle(nf)

def addCatalogDesignConfigurationsIpxactFile(
    catalog: Catalog,
    designConfigurationVLNV: Sequence[str],
    fileName: str,
) -> str:
    """Add a designConfigurations ipxactFile entry to the catalog."""
    catalog.design_configurations, nf = _add_ipxact_file(
        getattr(catalog, "design_configurations", None),
        designConfigurationVLNV,
        fileName,
    )
    return get_handle(nf)

def addCatalogDesignsIpxactFile(
    catalog: Catalog,
    designVLNV: Sequence[str],
    fileName: str,
) -> str:
    """Add a designs ipxactFile entry to the catalog."""
    catalog.designs, nf = _add_ipxact_file(getattr(catalog, "designs", None), designVLNV, fileName)
    return get_handle(nf)

def addCatalogGeneratorChainsIpxactFile(
    catalog: Catalog,
    generatorChainVLNV: Sequence[str],
    fileName: str,
) -> str:
    """Add a generatorChains ipxactFile entry to the catalog."""
    catalog.generator_chains, nf = _add_ipxact_file(
        getattr(catalog, "generator_chains", None),
        generatorChainVLNV,
        fileName,
    )
    return get_handle(nf)

def addCatalogTypeDefinitionsIpxactFile(
    catalog: Catalog,
    typeDefinitionVLNV: Sequence[str],
    fileName: str,
) -> str:
    """Add a typeDefinitions ipxactFile entry to the catalog."""
    catalog.type_definitions, nf = _add_ipxact_file(
        getattr(catalog, "type_definitions", None),
        typeDefinitionVLNV,
        fileName,
    )
    return get_handle(nf)

def removeCatalogAbstractionDefIpxactFile(catalog: Catalog, ipxactFileID: str) -> bool:
    """Remove an abstractionDefinition ipxactFile entry by handle."""
    return _remove_file_by_handle(getattr(catalog, "abstraction_definitions", None), ipxactFileID)

def removeCatalogAbstractorsIpxactFile(catalog: Catalog, ipxactFileID: str) -> bool:
    """Remove an abstractors ipxactFile entry by handle."""
    return _remove_file_by_handle(getattr(catalog, "abstractors", None), ipxactFileID)

def removeCatalogBusDefinitionsIpxactFile(catalog: Catalog, ipxactFileID: str) -> bool:
    """Remove a busDefinitions ipxactFile entry by handle."""
    return _remove_file_by_handle(getattr(catalog, "bus_definitions", None), ipxactFileID)

def removeCatalogCatalogsIpxactFile(catalog: Catalog, ipxactFileID: str) -> bool:
    """Remove a catalogs ipxactFile entry by handle."""
    return _remove_file_by_handle(getattr(catalog, "catalogs", None), ipxactFileID)

def removeCatalogComponentsIpxactFile(catalog: Catalog, ipxactFileID: str) -> bool:
    """Remove a components ipxactFile entry by handle."""
    return _remove_file_by_handle(getattr(catalog, "components", None), ipxactFileID)

def removeCatalogDesignConfigurationsIpxactFile(catalog: Catalog, ipxactFileID: str) -> bool:
    """Remove a designConfigurations ipxactFile entry by handle."""
    return _remove_file_by_handle(getattr(catalog, "design_configurations", None), ipxactFileID)

def removeCatalogDesignsIpxactFile(catalog: Catalog, ipxactFileID: str) -> bool:
    """Remove a designs ipxactFile entry by handle."""
    return _remove_file_by_handle(getattr(catalog, "designs", None), ipxactFileID)

def removeCatalogGeneratorChainsIpxactFile(catalog: Catalog, ipxactFileID: str) -> bool:
    """Remove a generatorChains ipxactFile entry by handle."""
    return _remove_file_by_handle(getattr(catalog, "generator_chains", None), ipxactFileID)

def removeCatalogTypeDefinitionsIpxactFile(catalog: Catalog, ipxactFileID: str) -> bool:
    """Remove a typeDefinitions ipxactFile entry by handle."""
    return _remove_file_by_handle(getattr(catalog, "type_definitions", None), ipxactFileID)

def setIpxactFileName(ipxact_file: IpxactFileType, name: str) -> bool:
    """Set the file name of an ipxactFile entry."""
    ipxact_file.name = IpxactUri(name)
    return True

def setIpxactFileVlnv(ipxact_file: IpxactFileType, vlnv: Sequence[str]) -> bool:
    """Set the VLNV reference of an ipxactFile entry."""
    if len(vlnv) != 4:
        raise ValueError("VLNV must be sequence of 4 strings")
    ipxact_file.vlnv = LibraryRefType(vendor=vlnv[0], library=vlnv[1], name=vlnv[2], version=vlnv[3])
    return True
