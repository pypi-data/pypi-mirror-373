import importlib
from pathlib import Path

# import tempfile
# from tempfile import TemporaryDirectory
# import ssl
# import urllib.request
# import zipfile
import pytest

from amal.eda.ipxact_de.xml_document import XmlDocument
from org.accellera.standard import Standard

# from org.accellera.ipxact.v1685_2022 import (
#     Catalog,
#     BusDefinition,
#     AbstractionDefinition,
#     Component,
#     Abstractor,
#     Design,
#     DesignConfiguration,
#     GeneratorChain,
#     TypeDefinitions,
# )


NS_MAP = Standard.namespace_map_for("ipxact", "1685-2022")
SCHEMA_LOCATION = Standard.schema_location_for("ipxact", "1685-2022")

# from shutil import copytree

# @pytest.fixture
# def zip_dir(tmp_path, request):
#     session = request.session
#     # copy the data from our cache to the temp location for the test
#     copytree(session.__CACHE, tmp_path)
#     yield tmp_path


# # @pytest.fixture
# def xml_files():
#     return Path("Leon2").rglob("*.xml")



# @pytest.fixture(scope="session")
# def xml_files():
#     leon2_example_url = "https://www.accellera.org/images/activities/committees/ip-xact/Leon2_1685-2022.zip"
#     td = TemporaryDirectory()
#     tmp_path = Path(td.name)

#     print("➤ Downloading and extracting 'Leon2_1685-2022.zip' ...")
#     print(tmp_path)
#     # Download Leon2_1685-2022.zip in the temporary directory
#     ssl._create_default_https_context = ssl._create_unverified_context
#     urllib.request.urlretrieve(leon2_example_url, tmp_path / "Leon2_1685-2022.zip")

#     # Unzip Leon2_1685-2022.zip in the temporary directory
#     with zipfile.ZipFile(tmp_path / "Leon2_1685-2022.zip", "r") as zip_ref:
#         zip_ref.extractall(tmp_path)

#     return tmp_path.rglob("*.xml")

# def pytest_generate_tests(metafunc):
#     if "xml_file" in metafunc.fixturenames:
#         xml_files = metafunc.config._xml_files
#         # xml_files = metafunc.config.pluginmanager.getplugin("session").xml_files
#         metafunc.parametrize("xml_file", xml_files)


# @pytest.fixture(scope="session", autouse=True)
# def load_xml_files(request):
#     xml_files = request.getfixturevalue("xml_files")
#     request.config._xml_files = xml_files
#     # request.config.pluginmanager.getplugin("session").xml_files = xml_files

# def get_xml_files(xml_dir):
#     """Get list of XML files in directory"""
#     return Path(xml_dir).rglob("*.xml")


# @pytest.fixture(scope="session", name="download_dir", autouse=True)
# def xml_dir():
#     """Download and extract Leon2 example files, return path to XML files"""
#     leon2_example_url = "https://www.accellera.org/images/activities/committees/ip-xact/Leon2_1685-2022.zip"
#     with TemporaryDirectory() as td:
#         tmp_path = Path(td)
#         print(f"➤ Downloading and extracting 'Leon2_1685-2022.zip' to {tmp_path}...")
#         print(tmp_path)

#         ssl._create_default_https_context = ssl._create_unverified_context
#         urllib.request.urlretrieve(leon2_example_url, tmp_path / "Leon2_1685-2022.zip")

#         with zipfile.ZipFile(tmp_path / "Leon2_1685-2022.zip", "r") as zip_ref:
#             zip_ref.extractall(tmp_path)

#         yield tmp_path


# def pytest_generate_tests(metafunc):
#     """Generate test cases for each XML file"""
#     if "xml_file" in metafunc.fixturenames:
#         xml_dir = metafunc.getfixturevalue("xml_dir")
#         xml_files = Path(xml_dir).rglob("*.xml")
#         metafunc.parametrize("xml_file", xml_files)


# @pytest.fixture(scope="session")
# def xml_files(download_dir):
#     """Get list of all XML files from downloaded directory"""
#     return list(Path(download_dir).rglob("*.xml"))

# def pytest_generate_tests(metafunc):
#     """Generate test cases for each XML file"""
#     if "xml_file" in metafunc.fixturenames:
#         metafunc.parametrize("xml_file", metafunc.getfixturevalue("xml_files"))

# # Global variables to hold temporary directory and XML files
# _download_temp_dir = None
# _download_xml_files = []

# def pytest_generate_tests(metafunc):
#     global _download_temp_dir, _download_xml_files
#     if "xml_file" in metafunc.fixturenames and not _download_xml_files:
#         leon2_example_url = "https://www.accellera.org/images/activities/committees/ip-xact/Leon2_1685-2022.zip"
#         # _download_temp_dir = TemporaryDirectory()
#         _download_temp_dir = tempfile.mkdtemp(prefix="leon2_test_")
#         download_path = Path(_download_temp_dir)
#         # download_path = Path(_download_temp_dir.name)
#         print(f"➤ Downloading and extracting 'Leon2_1685-2022.zip' to {download_path}...")

#         # Disable SSL verification for the download
#         ssl._create_default_https_context = ssl._create_unverified_context

#         # Download the ZIP file
#         zip_path = download_path / "Leon2_1685-2022.zip"
#         urllib.request.urlretrieve(leon2_example_url, zip_path)
#         print(f"Downloaded ZIP to {zip_path}")

#         # Extract the ZIP file
#         with zipfile.ZipFile(zip_path, "r") as zip_ref:
#             zip_ref.extractall(download_path)
#         print(f"Extracted ZIP to {download_path}")

#         # Collect all XML files
#         _download_xml_files = list(download_path.rglob("*.xml"))
#         print(f"Found {len(_download_xml_files)} XML files.")

#     if "xml_file" in metafunc.fixturenames:
#         # metafunc.parametrize(
#         #     "xml_file",
#         #     _download_xml_files,
#         #     ids=[str(p.relative_to(tmp_path)) for p in _download_xml_files])
#         metafunc.parametrize(
#             "xml_file",
#             _download_xml_files,
#             ids=[str(p.relative_to(_download_temp_dir)) for p in _download_xml_files]
#         )

# def pytest_sessionfinish(session, exitstatus):
#     """Cleanup the temporary directory after all tests are done."""
#     global _download_temp_dir
#     if _download_temp_dir:
#         _download_temp_dir.cleanup()
#         print("➤ Cleaned up temporary directory.")


# @pytest.mark.parametrize("xml_file", xml_files())
# def test_parse_leon(xml_file: str):
# @pytest.mark.parametrize("xml_file", get_xml_files("Leon2"))
# @pytest.mark.parametrize("xml_file", [])  # Placeholder, actual params come from pytest_generate_tests
# def test_parse_leon(xml_file: Path):

def test_parse_leon(xml_file: Path, module_name: str):
    parser = XmlDocument.parser()

    # for xml_file in xml_files:
    # print(f"➤ Parsing XML file: '{xml_file.resolve()}' ...")
    # print(f"➤ Parsing XML file: '{xml_file.resolve()}' using module: '{module_name}' ...")

    print("=" * 120)
    print()
    try:
        doc = XmlDocument(xml_file)
        tree = doc.tree  # lxml ElementTree
        assert tree is not None
        version_xml = f"{doc.standard}/{doc.version}"  # e.g. IPXACT/1685-2022
    except Exception as e:
        pytest.fail(f"Failed to parse XML file '{xml_file}': {e}")

    # Skip faulty XML files
    if version_xml == "IPXACT/2.0":
        return

    # xml_text = xml_file.read_text()
    # print(xml_text)
    # print("=" * 120)

    name = tree.docinfo.root_name
    print(f"  • Root element: '{name}'")

    # Expected root elements
    expected_tags = [
        "catalog",
        "busDefinition",
        "abstractionDefinition",
        "component",
        "abstractor",
        "design",
        "designConfiguration",
        "generatorChain",
        "typeDefinition",
    ]
    assert name in expected_tags, f"Unknown root tag: '{name}'"

    # Dynamically import the appropriate module based on module_name
    full_module_name = f"org.accellera.ipxact.{module_name}"
    try:
        module = importlib.import_module(full_module_name)
        print(f"  • Imported module '{full_module_name}' successfully.")
    except ImportError as e:
        pytest.fail(f"Failed to import module '{full_module_name}': {e}")

    # Map of tag names to classes in the respective module
    class_map = {
        "catalog": getattr(module, "Catalog", None),
        "busDefinition": getattr(module, "BusDefinition", None),
        "abstractionDefinition": getattr(module, "AbstractionDefinition", None),
        "component": getattr(module, "Component", None),
        "abstractor": getattr(module, "Abstractor", None),
        "design": getattr(module, "Design", None),
        "designConfiguration": getattr(module, "DesignConfiguration", None),
        "generatorChain": getattr(module, "GeneratorChain", None),
        "typeDefinition": getattr(module, "TypeDefinitions", None),
    }

    # Get the appropriate class for the root tag
    cls = class_map.get(name)
    if cls is None:
        pytest.fail(f"No class mapping found for tag '{name}' in module '{full_module_name}'.")

    try:
        # Deserialize the XML into the dataclass
        # deserialized_object
        _ = parser.from_string(xml_file.read_text(), cls)
        # print(f"  • Deserialized object: {deserialized_object}")
    except Exception as e:
        pytest.fail(f"Failed to deserialize XML file '{xml_file}' using class '{cls}': {e}")

    # try:
    #     if name == "catalog":
    #         catalog = parser.from_string(xml_text, Catalog)
    #         print(catalog)
    #     elif name == "busDefinition":
    #         bus_definition = parser.from_string(xml_text, BusDefinition)
    #         print(bus_definition)
    #     elif name == "abstractionDefinition":
    #         abstraction_definition = parser.from_string(xml_text, AbstractionDefinition)
    #         print(abstraction_definition)
    #     # elif name == "component":
    #     #     component = parser.from_string(xml_text, Component)
    #     #     print(component)
    #     # elif name == "abstractor":
    #     #     abstractor = parser.from_string(xml_text, Abstractor)
    #     #     print(abstractor)
    #     elif name == "design":
    #         design = parser.from_string(xml_text, Design)
    #         print(design)
    #     elif name == "designConfiguration":
    #         design_configuration = parser.from_string(xml_text, DesignConfiguration)
    #         print(design_configuration)
    #     elif name == "generatorChain":
    #         generator_chain = parser.from_string(xml_text, GeneratorChain)
    #         print(generator_chain)
    #     elif name == "typeDefinition":
    #         type_definitions = parser.from_string(xml_text, TypeDefinitions)
    #         print(type_definitions)
    #     # else:
    #     #     print(f"Unknown root tag: '{name}'")
    #     #     # continue
    # except Exception as e:
    #         pytest.fail(f"Failed to deserialize XML file '{xml_file}': {e}")
