import importlib
from pathlib import Path

import pytest
from xsdata.formats.dataclass.parsers import XmlParser

from amal.eda.ipxact_de.xml_document import XmlDocument

# from xsdata.formats.dataclass.context import XmlContext

# NOTE: Serialization/deserialization is performed via XmlDocument.serializer()/parser().
# If needed, namespace and schema location can be obtained from Standard:
# from org.accellera.standard import Standard
# NS_MAP = Standard.namespace_map_for("ipxact", "1685-2022")
# SCHEMA_LOCATION = Standard.schema_location_for("ipxact", "1685-2022")

FILE_PATH = Path(__file__).parent
XML_DIR = FILE_PATH / "xml"

# Collect all XML files under tests/xml and build (standard, version, path) tuples.
_xml_param_values = []
if XML_DIR.exists():
    for _p in sorted(XML_DIR.rglob("*.xml")):
        rel = _p.relative_to(XML_DIR)
        # Expect at least: standard/version/....xml
        if len(rel.parts) < 2:
            continue
        _standard = rel.parts[0]
        _version = rel.parts[1]
        _xml_param_values.append((_standard, _version, _p))

_xml_param_ids = [f"{s}-{v}-{p.relative_to(XML_DIR)}" for s, v, p in _xml_param_values]


@pytest.mark.parametrize("standard,version,xml_file", _xml_param_values, ids=_xml_param_ids)

def test_serialize_roundtrip(standard: str, version: str, xml_file: Path) -> None:
    """Parse, deserialize, re-serialize, and ensure no major failures.
    """
    rel = xml_file.relative_to(FILE_PATH)
    print(f"\n➤ Parsing XML file: '{rel}' using expected standard: '{standard}', version: '{version}' ...")

    try:
        doc = XmlDocument(xml_file)
    except Exception as e:  # pragma: no cover - defensive
        pytest.fail(f"Failed to parse XML file '{xml_file}': {e}")

    assert doc.tree is not None, "Document tree not parsed"
    name = doc.root_name or doc.tree.docinfo.root_name
    print(f"  • Root element: '{name}'")

    # Validate metadata
    assert doc.standard == standard.upper(), f"Expected standard '{standard.upper()}' got '{doc.standard}'"

    # Version normalization mirroring the original test
    v_dir = version
    v_work = v_dir.lstrip('v')
    parts = v_work.split('_')
    if parts and parts[0] == '1685' and len(parts) == 2:
        expected_version = parts[0] + '-' + parts[1]
    elif len(parts) == 2:
        expected_version = parts[0] + '.' + parts[1]
    else:
        expected_version = v_work.replace('_', '-')
    assert doc.version == expected_version, (
        f"Expected version '{expected_version}' (from dir '{version}') got '{doc.version}'"
    )

    # Import concrete module
    full_module_name = f"org.accellera.{standard}.{version}"
    try:
        module = importlib.import_module(full_module_name)
        print(f"  • Imported module '{full_module_name}' successfully.")
    except ImportError as e:
        pytest.fail(f"Failed to import module '{full_module_name}': {e}")

    class_map = {
        "catalog": getattr(module, "Catalog", None),
        "busDefinition": getattr(module, "BusDefinition", None),
        "abstractionDefinition": getattr(module, "AbstractionDefinition", None),
        "component": getattr(module, "Component", None),
        "abstractor": getattr(module, "Abstractor", None),
        "design": getattr(module, "Design", None),
        "designConfiguration": getattr(module, "DesignConfiguration", None),
        "generatorChain": getattr(module, "GeneratorChain", None),
        "typeDefinitions": getattr(module, "TypeDefinitions", None),
    }

    cls = class_map.get(name)
    if cls is None:
        pytest.fail(f"No class mapping found for tag '{name}' in module '{full_module_name}'.")

    # Use the shared parser to deserialize
    parser: XmlParser = XmlDocument.parser()
    try:
        obj = parser.from_string(xml_file.read_text(), cls)
    except Exception as e:  # pragma: no cover - defensive
        pytest.fail(f"Failed to deserialize XML file '{xml_file}' using class '{cls}': {e}")

    assert obj is not None

    # Re-serialize with the shared serializer and ensure a non-empty string
    xml_text = XmlDocument.serializer().render(obj)
    assert isinstance(xml_text, str) and xml_text.strip(), "Serialization produced empty output"
