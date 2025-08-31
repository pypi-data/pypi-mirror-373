from dataclasses import dataclass, field

from amal.eda.ipxact_de.xml_document import XmlDocument
from org.accellera.ipxact.v1685_2022 import (
    Catalog,
    Description,
    IpxactFilesType,
    IpxactFileType,
    IpxactUri,
    LibraryRefType,
    ShortDescription,
    VendorExtensions,
)
from org.accellera.standard import Standard

NS_MAP = Standard.namespace_map_for("ipxact", "1685-2022")
SCHEMA_LOCATION = Standard.schema_location_for("ipxact", "1685-2022")


def test_catalog_defaults():
    """Test the default values of the Catalog class."""

    catalog = Catalog()
    assert catalog.vendor is None
    assert catalog.name is None
    assert catalog.version is None
    assert catalog.library is None
    assert catalog.display_name is None
    assert catalog.short_description is None
    assert catalog.description is None
    assert catalog.catalogs is None
    assert catalog.bus_definitions is None
    assert catalog.abstraction_definitions is None
    assert catalog.components is None
    assert catalog.abstractors is None
    assert catalog.designs is None
    assert catalog.design_configurations is None
    assert catalog.generator_chains is None
    assert catalog.type_definitions is None
    assert catalog.vendor_extensions is None
    assert catalog.id is None


def test_catalog_simple():
    """Test the simple values of the Catalog class."""

    catalog = Catalog(
        vendor="accellera",
        library="library",
        name="catalog",
        version="1.0",
        display_name="display_name",
        short_description=ShortDescription("short_description"),
        description=Description("description"),
    )

    assert catalog.vendor == "accellera"
    assert catalog.library == "library"
    assert catalog.name == "catalog"
    assert catalog.version == "1.0"
    assert catalog.display_name == "display_name"
    assert catalog.short_description is not None and catalog.short_description.value == "short_description"
    assert catalog.description is not None and catalog.description.value == "description"


def test_catalog_catalogs():
    """Test the catalogs values of the Catalog class."""

    catalog = Catalog(
        vendor="accellera",
        library="library",
        name="catalog",
        version="1.0",
        display_name="display_name",
        short_description=ShortDescription("short_description"),
        description=Description("description"),
    )
    catalog0_ipxact_file = IpxactFileType(
        vlnv=LibraryRefType(vendor="vendor", library="library", name="catalog0", version="1.0"),
        name=IpxactUri("catalog0.xml"),
        description=Description("description"),
    )
    catalog1_ipxact_file = IpxactFileType(
        vlnv=LibraryRefType(vendor="vendor", library="library", name="catalog1", version="1.0"),
        name=IpxactUri("catalog1.xml"),
        description=Description("description"),
    )

    catalog.catalogs = IpxactFilesType(
        ipxact_file=[catalog0_ipxact_file, catalog1_ipxact_file],
    )

    assert catalog.vendor == "accellera"
    assert catalog.library == "library"
    assert catalog.name == "catalog"
    assert catalog.version == "1.0"
    assert catalog.display_name == "display_name"
    assert catalog.short_description is not None and catalog.short_description.value == "short_description"
    assert catalog.description is not None and catalog.description.value == "description"

    assert len(list(catalog.catalogs.ipxact_file)) == 2

    catalogs_files = list(catalog.catalogs.ipxact_file)
    vlnv0 = catalogs_files[0].vlnv
    assert vlnv0 is not None
    assert f"{vlnv0.vendor}:{vlnv0.library}:{vlnv0.name}:{vlnv0.version}" == "vendor:library:catalog0:1.0"
    assert catalogs_files[0].name is not None and catalogs_files[0].name.value == "catalog0.xml"
    cf0_desc = catalogs_files[0].description
    assert cf0_desc is not None and cf0_desc.value == "description"

    vlnv1 = catalogs_files[1].vlnv
    assert vlnv1 is not None
    assert f"{vlnv1.vendor}:{vlnv1.library}:{vlnv1.name}:{vlnv1.version}" == "vendor:library:catalog1:1.0"
    assert catalogs_files[1].name is not None and catalogs_files[1].name.value == "catalog1.xml"
    cf1_desc = catalogs_files[1].description
    assert cf1_desc is not None and cf1_desc.value == "description"


def test_catalog_bus_definitions():
    """Test the bus_definitions values of the Catalog class."""

    catalog = Catalog(
        vendor="accellera",
        library="library",
        name="catalog",
        version="1.0",
        display_name="display_name",
        short_description=ShortDescription("short_description"),
        description=Description("description"),
    )
    bus_definition0_ipxact_file = IpxactFileType(
        vlnv=LibraryRefType(vendor="vendor", library="library", name="bus_definition0", version="1.0"),
        name=IpxactUri("bus_definition0.xml"),
        description=Description("description"),
    )
    bus_definition1_ipxact_file = IpxactFileType(
        vlnv=LibraryRefType(vendor="vendor", library="library", name="bus_definition1", version="1.0"),
        name=IpxactUri("bus_definition1.xml"),
        description=Description("description"),
    )

    catalog.bus_definitions = IpxactFilesType(
        ipxact_file=[bus_definition0_ipxact_file, bus_definition1_ipxact_file],
    )

    assert catalog.vendor == "accellera"
    assert catalog.library == "library"
    assert catalog.name == "catalog"
    assert catalog.version == "1.0"
    assert catalog.display_name == "display_name"
    assert catalog.short_description is not None and catalog.short_description.value == "short_description"
    assert catalog.description is not None and catalog.description.value == "description"

    bus_files = list(catalog.bus_definitions.ipxact_file)
    assert len(bus_files) == 2
    b0_vlnv = bus_files[0].vlnv
    assert b0_vlnv is not None
    assert (
        f"{b0_vlnv.vendor}:{b0_vlnv.library}:{b0_vlnv.name}:{b0_vlnv.version}"
        == "vendor:library:bus_definition0:1.0"
    )
    assert bus_files[0].name is not None and bus_files[0].name.value == "bus_definition0.xml"
    b0_desc = bus_files[0].description
    assert b0_desc is not None and b0_desc.value == "description"
    b1_vlnv = bus_files[1].vlnv
    assert b1_vlnv is not None
    assert (
        f"{b1_vlnv.vendor}:{b1_vlnv.library}:{b1_vlnv.name}:{b1_vlnv.version}"
        == "vendor:library:bus_definition1:1.0"
    )
    assert bus_files[1].name is not None and bus_files[1].name.value == "bus_definition1.xml"
    b1_desc = bus_files[1].description
    assert b1_desc is not None and b1_desc.value == "description"


def test_catalog_abstraction_definitions():
    """Test the abstraction_definitions values of the Catalog class."""

    catalog = Catalog(
        vendor="accellera",
        library="library",
        name="catalog",
        version="1.0",
        display_name="display_name",
        short_description=ShortDescription("short_description"),
        description=Description("description"),
    )
    abstraction_definition0_ipxact_file = IpxactFileType(
        vlnv=LibraryRefType(vendor="vendor", library="library", name="abstraction_definition0", version="1.0"),
        name=IpxactUri("abstraction_definition0.xml"),
        description=Description("description"),
    )
    abstraction_definition1_ipxact_file = IpxactFileType(
        vlnv=LibraryRefType(vendor="vendor", library="library", name="abstraction_definition1", version="1.0"),
        name=IpxactUri("abstraction_definition1.xml"),
        description=Description("description"),
    )

    catalog.abstraction_definitions = IpxactFilesType(
        ipxact_file=[abstraction_definition0_ipxact_file, abstraction_definition1_ipxact_file],
    )

    assert catalog.vendor == "accellera"
    assert catalog.library == "library"
    assert catalog.name == "catalog"
    assert catalog.version == "1.0"
    assert catalog.display_name == "display_name"
    assert catalog.short_description is not None and catalog.short_description.value == "short_description"
    assert catalog.description is not None and catalog.description.value == "description"

    abs_files = list(catalog.abstraction_definitions.ipxact_file)
    assert len(abs_files) == 2
    a0_vlnv = abs_files[0].vlnv
    assert a0_vlnv is not None
    assert (
        f"{a0_vlnv.vendor}:{a0_vlnv.library}:{a0_vlnv.name}:{a0_vlnv.version}"
        == "vendor:library:abstraction_definition0:1.0"
    )
    assert abs_files[0].name is not None and abs_files[0].name.value == "abstraction_definition0.xml"
    a0_desc = abs_files[0].description
    assert a0_desc is not None and a0_desc.value == "description"
    a1_vlnv = abs_files[1].vlnv
    assert a1_vlnv is not None
    assert (
        f"{a1_vlnv.vendor}:{a1_vlnv.library}:{a1_vlnv.name}:{a1_vlnv.version}"
        == "vendor:library:abstraction_definition1:1.0"
    )
    assert abs_files[1].name is not None and abs_files[1].name.value == "abstraction_definition1.xml"
    a1_desc = abs_files[1].description
    assert a1_desc is not None and a1_desc.value == "description"


def test_catalog_components():
    """Test the components values of the Catalog class."""

    catalog = Catalog(
        vendor="accellera",
        library="library",
        name="catalog",
        version="1.0",
        display_name="display_name",
        short_description=ShortDescription("short_description"),
        description=Description("description"),
    )
    component0_ipxact_file = IpxactFileType(
        vlnv=LibraryRefType(vendor="vendor", library="library", name="component0", version="1.0"),
        name=IpxactUri("component0.xml"),
        description=Description("description"),
    )
    component1_ipxact_file = IpxactFileType(
        vlnv=LibraryRefType(vendor="vendor", library="library", name="component1", version="1.0"),
        name=IpxactUri("component1.xml"),
        description=Description("description"),
    )

    catalog.components = IpxactFilesType(
        ipxact_file=[component0_ipxact_file, component1_ipxact_file],
    )

    assert catalog.vendor == "accellera"
    assert catalog.library == "library"
    assert catalog.name == "catalog"
    assert catalog.version == "1.0"
    assert catalog.display_name == "display_name"
    assert catalog.short_description is not None and catalog.short_description.value == "short_description"
    assert catalog.description is not None and catalog.description.value == "description"

    comp_files = list(catalog.components.ipxact_file)
    assert len(comp_files) == 2
    c0_vlnv = comp_files[0].vlnv
    assert c0_vlnv is not None
    assert f"{c0_vlnv.vendor}:{c0_vlnv.library}:{c0_vlnv.name}:{c0_vlnv.version}" == "vendor:library:component0:1.0"
    assert comp_files[0].name is not None and comp_files[0].name.value == "component0.xml"
    c0_desc = comp_files[0].description
    assert c0_desc is not None and c0_desc.value == "description"
    c1_vlnv = comp_files[1].vlnv
    assert c1_vlnv is not None
    assert f"{c1_vlnv.vendor}:{c1_vlnv.library}:{c1_vlnv.name}:{c1_vlnv.version}" == "vendor:library:component1:1.0"
    assert comp_files[1].name is not None and comp_files[1].name.value == "component1.xml"
    c1_desc = comp_files[1].description
    assert c1_desc is not None and c1_desc.value == "description"


def test_catalog_abstractors():
    """Test the abstractors values of the Catalog class."""

    catalog = Catalog(
        vendor="accellera",
        library="library",
        name="catalog",
        version="1.0",
        display_name="display_name",
        short_description=ShortDescription("short_description"),
        description=Description("description"),
    )
    abstractor0_ipxact_file = IpxactFileType(
        vlnv=LibraryRefType(vendor="vendor", library="library", name="abstractor0", version="1.0"),
        name=IpxactUri("abstractor0.xml"),
        description=Description("description"),
    )
    abstractor1_ipxact_file = IpxactFileType(
        vlnv=LibraryRefType(vendor="vendor", library="library", name="abstractor1", version="1.0"),
        name=IpxactUri("abstractor1.xml"),
        description=Description("description"),
    )

    catalog.abstractors = IpxactFilesType(
        ipxact_file=[abstractor0_ipxact_file, abstractor1_ipxact_file],
    )

    assert catalog.vendor == "accellera"
    assert catalog.library == "library"
    assert catalog.name == "catalog"
    assert catalog.version == "1.0"
    assert catalog.display_name == "display_name"
    assert catalog.short_description is not None and catalog.short_description.value == "short_description"
    assert catalog.description is not None and catalog.description.value == "description"

    abstractor_files = list(catalog.abstractors.ipxact_file)
    assert len(abstractor_files) == 2
    ab0_vlnv = abstractor_files[0].vlnv
    assert ab0_vlnv is not None
    assert (
        f"{ab0_vlnv.vendor}:{ab0_vlnv.library}:{ab0_vlnv.name}:{ab0_vlnv.version}"
        == "vendor:library:abstractor0:1.0"
    )
    assert abstractor_files[0].name is not None and abstractor_files[0].name.value == "abstractor0.xml"
    ab0_desc = abstractor_files[0].description
    assert ab0_desc is not None and ab0_desc.value == "description"
    ab1_vlnv = abstractor_files[1].vlnv
    assert ab1_vlnv is not None
    assert (
        f"{ab1_vlnv.vendor}:{ab1_vlnv.library}:{ab1_vlnv.name}:{ab1_vlnv.version}"
        == "vendor:library:abstractor1:1.0"
    )
    assert abstractor_files[1].name is not None and abstractor_files[1].name.value == "abstractor1.xml"
    ab1_desc = abstractor_files[1].description
    assert ab1_desc is not None and ab1_desc.value == "description"



def test_catalog_designs():
    """Test the designs values of the Catalog class."""

    catalog = Catalog(
        vendor="accellera",
        library="library",
        name="catalog",
        version="1.0",
        display_name="display_name",
        short_description=ShortDescription("short_description"),
        description=Description("description"),
    )
    design0_ipxact_file = IpxactFileType(
        vlnv=LibraryRefType(vendor="vendor", library="library", name="design0", version="1.0"),
        name=IpxactUri("design0.xml"),
        description=Description("description"),
    )
    design1_ipxact_file = IpxactFileType(
        vlnv=LibraryRefType(vendor="vendor", library="library", name="design1", version="1.0"),
        name=IpxactUri("design1.xml"),
        description=Description("description"),
    )

    catalog.designs = IpxactFilesType(
        ipxact_file=[design0_ipxact_file, design1_ipxact_file],
    )

    assert catalog.vendor == "accellera"
    assert catalog.library == "library"
    assert catalog.name == "catalog"
    assert catalog.version == "1.0"
    assert catalog.display_name == "display_name"
    assert catalog.short_description is not None and catalog.short_description.value == "short_description"
    assert catalog.description is not None and catalog.description.value == "description"

    design_files = list(catalog.designs.ipxact_file)
    assert len(design_files) == 2
    d0_vlnv = design_files[0].vlnv
    assert d0_vlnv is not None
    assert f"{d0_vlnv.vendor}:{d0_vlnv.library}:{d0_vlnv.name}:{d0_vlnv.version}" == "vendor:library:design0:1.0"
    assert design_files[0].name is not None and design_files[0].name.value == "design0.xml"
    d0_desc = design_files[0].description
    assert d0_desc is not None and d0_desc.value == "description"
    d1_vlnv = design_files[1].vlnv
    assert d1_vlnv is not None
    assert f"{d1_vlnv.vendor}:{d1_vlnv.library}:{d1_vlnv.name}:{d1_vlnv.version}" == "vendor:library:design1:1.0"
    assert design_files[1].name is not None and design_files[1].name.value == "design1.xml"
    d1_desc = design_files[1].description
    assert d1_desc is not None and d1_desc.value == "description"


def test_catalog_design_configurations():
    """Test the design_configurations values of the Catalog class."""

    catalog = Catalog(
        vendor="accellera",
        library="library",
        name="catalog",
        version="1.0",
        display_name="display_name",
        short_description=ShortDescription("short_description"),
        description=Description("description"),
    )
    design_configuration0_ipxact_file = IpxactFileType(
        vlnv=LibraryRefType(vendor="vendor", library="library", name="design_configuration0", version="1.0"),
        name=IpxactUri("design_configuration0.xml"),
        description=Description("description"),
    )
    design_configuration1_ipxact_file = IpxactFileType(
        vlnv=LibraryRefType(vendor="vendor", library="library", name="design_configuration1", version="1.0"),
        name=IpxactUri("design_configuration1.xml"),
        description=Description("description"),
    )

    catalog.design_configurations = IpxactFilesType(
        ipxact_file=[design_configuration0_ipxact_file, design_configuration1_ipxact_file],
    )

    assert catalog.vendor == "accellera"
    assert catalog.library == "library"
    assert catalog.name == "catalog"
    assert catalog.version == "1.0"
    assert catalog.display_name == "display_name"
    assert catalog.short_description is not None and catalog.short_description.value == "short_description"
    assert catalog.description is not None and catalog.description.value == "description"

    design_cfg_files = list(catalog.design_configurations.ipxact_file)
    assert len(design_cfg_files) == 2
    dc0_vlnv = design_cfg_files[0].vlnv
    assert dc0_vlnv is not None
    assert (
        f"{dc0_vlnv.vendor}:{dc0_vlnv.library}:{dc0_vlnv.name}:{dc0_vlnv.version}"
        == "vendor:library:design_configuration0:1.0"
    )
    assert design_cfg_files[0].name is not None and design_cfg_files[0].name.value == "design_configuration0.xml"
    dc0_desc = design_cfg_files[0].description
    assert dc0_desc is not None and dc0_desc.value == "description"
    dc1_vlnv = design_cfg_files[1].vlnv
    assert dc1_vlnv is not None
    assert (
        f"{dc1_vlnv.vendor}:{dc1_vlnv.library}:{dc1_vlnv.name}:{dc1_vlnv.version}"
        == "vendor:library:design_configuration1:1.0"
    )
    assert design_cfg_files[1].name is not None and design_cfg_files[1].name.value == "design_configuration1.xml"
    dc1_desc = design_cfg_files[1].description
    assert dc1_desc is not None and dc1_desc.value == "description"


def test_catalog_generator_chains():
    """Test the generator_chains values of the Catalog class."""

    catalog = Catalog(
        vendor="accellera",
        library="library",
        name="catalog",
        version="1.0",
        display_name="display_name",
        short_description=ShortDescription("short_description"),
        description=Description("description"),
    )
    generator_chain0_ipxact_file = IpxactFileType(
        vlnv=LibraryRefType(vendor="vendor", library="library", name="generator_chain0", version="1.0"),
        name=IpxactUri("generator_chain0.xml"),
        description=Description("description"),
    )
    generator_chain1_ipxact_file = IpxactFileType(
        vlnv=LibraryRefType(vendor="vendor", library="library", name="generator_chain1", version="1.0"),
        name=IpxactUri("generator_chain1.xml"),
        description=Description("description"),
    )

    catalog.generator_chains = IpxactFilesType(
        ipxact_file=[generator_chain0_ipxact_file, generator_chain1_ipxact_file],
    )

    assert catalog.vendor == "accellera"
    assert catalog.library == "library"
    assert catalog.name == "catalog"
    assert catalog.version == "1.0"
    assert catalog.display_name == "display_name"
    assert catalog.short_description is not None and catalog.short_description.value == "short_description"
    assert catalog.description is not None and catalog.description.value == "description"

    gen_chain_files = list(catalog.generator_chains.ipxact_file)
    assert len(gen_chain_files) == 2
    g0_vlnv = gen_chain_files[0].vlnv
    assert g0_vlnv is not None
    assert (
        f"{g0_vlnv.vendor}:{g0_vlnv.library}:{g0_vlnv.name}:{g0_vlnv.version}"
        == "vendor:library:generator_chain0:1.0"
    )
    assert gen_chain_files[0].name is not None and gen_chain_files[0].name.value == "generator_chain0.xml"
    g0_desc = gen_chain_files[0].description
    assert g0_desc is not None and g0_desc.value == "description"
    g1_vlnv = gen_chain_files[1].vlnv
    assert g1_vlnv is not None
    assert (
        f"{g1_vlnv.vendor}:{g1_vlnv.library}:{g1_vlnv.name}:{g1_vlnv.version}"
        == "vendor:library:generator_chain1:1.0"
    )
    assert gen_chain_files[1].name is not None and gen_chain_files[1].name.value == "generator_chain1.xml"
    g1_desc = gen_chain_files[1].description
    assert g1_desc is not None and g1_desc.value == "description"


def test_catalog_type_definitions():
    """Test the type_definitions values of the Catalog class."""

    catalog = Catalog(
        vendor="accellera",
        library="library",
        name="catalog",
        version="1.0",
        display_name="display_name",
        short_description=ShortDescription("short_description"),
        description=Description("description"),
    )
    type_definition0_ipxact_file = IpxactFileType(
        vlnv=LibraryRefType(vendor="vendor", library="library", name="type_definition0", version="1.0"),
        name=IpxactUri("type_definition0.xml"),
        description=Description("description"),
    )
    type_definition1_ipxact_file = IpxactFileType(
        vlnv=LibraryRefType(vendor="vendor", library="library", name="type_definition1", version="1.0"),
        name=IpxactUri("type_definition1.xml"),
        description=Description("description"),
    )

    catalog.type_definitions = IpxactFilesType(
        ipxact_file=[type_definition0_ipxact_file, type_definition1_ipxact_file],
    )

    assert catalog.vendor == "accellera"
    assert catalog.library == "library"
    assert catalog.name == "catalog"
    assert catalog.version == "1.0"
    assert catalog.display_name == "display_name"
    assert catalog.short_description is not None and catalog.short_description.value == "short_description"
    assert catalog.description is not None and catalog.description.value == "description"

    type_def_files = list(catalog.type_definitions.ipxact_file)
    assert len(type_def_files) == 2
    t0_vlnv = type_def_files[0].vlnv
    assert t0_vlnv is not None
    assert (
        f"{t0_vlnv.vendor}:{t0_vlnv.library}:{t0_vlnv.name}:{t0_vlnv.version}"
        == "vendor:library:type_definition0:1.0"
    )
    assert type_def_files[0].name is not None and type_def_files[0].name.value == "type_definition0.xml"
    t0_desc = type_def_files[0].description
    assert t0_desc is not None and t0_desc.value == "description"
    t1_vlnv = type_def_files[1].vlnv
    assert t1_vlnv is not None
    assert (
        f"{t1_vlnv.vendor}:{t1_vlnv.library}:{t1_vlnv.name}:{t1_vlnv.version}"
        == "vendor:library:type_definition1:1.0"
    )
    assert type_def_files[1].name is not None and type_def_files[1].name.value == "type_definition1.xml"
    t1_desc = type_def_files[1].description
    assert t1_desc is not None and t1_desc.value == "description"


# Define a vendor extension for the Catalog class
@dataclass
class CatalogExtension:
    class Meta:
        name = "catalog"
        namespace = "http://www.vendor.org/XMLSchema/"

    version: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )


def test_catalog_vendor_extensions():
    """Test the vendor_extensions values of the Catalog class."""

    catalog = Catalog(
        vendor="accellera",
        library="library",
        name="catalog",
        version="1.0",
        display_name="display_name",
        short_description=ShortDescription("short_description"),
        description=Description("description"),
    )

    catalog.vendor_extensions = VendorExtensions(
        [
            CatalogExtension(version="1.1.0"),
        ]
    )

    assert catalog.vendor == "accellera"
    assert catalog.library == "library"
    assert catalog.name == "catalog"
    assert catalog.version == "1.0"
    assert catalog.display_name == "display_name"
    assert catalog.short_description is not None and catalog.short_description.value == "short_description"
    assert catalog.description is not None and catalog.description.value == "description"

    assert catalog.vendor_extensions is not None
    ve_any = list(catalog.vendor_extensions.any_element)
    assert getattr(ve_any[0], "version", None) == "1.1.0"

    # Add new vendor extension to namespace
    NS_MAP["vendor"] = "http://www.vendor.org/XMLSchema/"

    xml = XmlDocument.serializer().render(catalog, ns_map=NS_MAP)

    # Add -s to view this
    # Visual separator for optional debug viewing
    print("\n" + ("=" * 120))
    print(xml)
    print("=" * 120)

    parser = XmlDocument.parser()
    catalog_new = parser.from_string(xml, Catalog)

    assert catalog_new == catalog
