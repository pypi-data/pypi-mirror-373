"""XML parsing utilities for IP-XACT / SPIRIT documents.
"""
from pathlib import Path
from typing import TypeVar

from lxml import etree
from rich import print
from xsdata.formats.dataclass.context import XmlContext
from xsdata.formats.dataclass.parsers import XmlParser
from xsdata.formats.dataclass.serializers.config import SerializerConfig
from xsdata.formats.dataclass.serializers.xml import XmlSerializer

from amal.utilities import ARROW, CHECK, CROSS

T = TypeVar("T")


class XmlDocument:
    """Represents a parsed IP-XACT/SPIRIT XML document.

    Attributes
    ----------
    path: Path
        Path to the original XML file.
    tree: etree._ElementTree | None
        Parsed XML tree (None until parsing succeeds).
    schema: str | None
        Resolved schema location (index.xsd path) if discovered.
    version: str | None
        Version string in the form 'IPXACT/1685-2022' or 'SPIRIT/1.5'.
    root_name: str | None
        Root element name.
    is_spirit: bool
        True if the file namespace matches SPIRIT.
    is_ipxact: bool
        True if the file namespace matches IP-XACT.
    """

    def __init__(self, path: Path, *, auto_parse: bool = True) -> None:
        """Create a new XML document representation.

        Parameters
        ----------
        path: Path
            Path to the XML file to be parsed.
        auto_parse: bool, default True
            If True (default) the file is parsed immediately; set to False to
            defer parsing and call parse() manually.
        """
        # Initialize slot attributes
        self.path: Path = path
        self.tree: etree._ElementTree | None = None
        self.schema: str = ""
        self.standard: str = ""
        self.version: str = ""
        self.root_name: str = ""
        self.is_spirit: bool = False
        self.is_ipxact: bool = False
        if auto_parse:
            self.parse()

    # ------------------------------------------------------------------
    # Shared serializer/parser singletons
    # ------------------------------------------------------------------
    _XML_CONTEXT: XmlContext = XmlContext()
    _SERIALIZER: XmlSerializer = XmlSerializer(
        context=_XML_CONTEXT,
        config=SerializerConfig(indent="  ")
    )
    _PARSER: XmlParser = XmlParser(context=_XML_CONTEXT)

    @classmethod
    def serializer(cls) -> XmlSerializer:
        """Return a shared ``XmlSerializer`` instance.

        Returns
        -------
        XmlSerializer
            The singleton serializer configured with two-space indentation.
        """
        return cls._SERIALIZER

    @classmethod
    def parser(cls) -> XmlParser:
        """Return a shared ``XmlParser`` instance.

        Returns
        -------
        XmlParser
            The singleton parser bound to the shared XML context.
        """
        return cls._PARSER

    # ------------------------------------------------------------------
    def parse(self) -> None:
        """Parse the XML document if not already parsed.

        This populates tree, schema, standard, version, root_name, and flags.
        Subsequent calls are no-ops.
        """
        if self.tree is not None:
            return  # already parsed

        print(f"{ARROW} Parsing ...")
        try:
            self.tree = etree.parse(str(self.path))
            print(f"  {ARROW} Success {CHECK}")
        except etree.XMLSyntaxError as err:  # pragma: no cover - defensive
            print(f"  {ARROW} Failed {CROSS}\n{err}")
            raise

        assert self.tree is not None  # for type checkers
        root = self.tree.getroot()
        self.root_name = self.tree.docinfo.root_name
        attrib = root.attrib
        nsmap = root.nsmap

        try:
            xsi = nsmap["xsi"]
            xsi_location = f"{{{xsi}}}schemaLocation"
            _schema_decl = attrib.get(xsi_location)
            if _schema_decl:
                _schema_decl = ' '.join(_schema_decl.split())
                print(f"{ARROW} Schema      : '{_schema_decl}'")
        except KeyError:
            print(f"{ARROW} xsi namespace is missing in xml file!")

        print(f"{ARROW} Found       : '{self.root_name}'")

        ipxact_ns = nsmap.get("ipxact")
        spirit_ns = nsmap.get("spirit")

        if spirit_ns:
            schema_root = "http://www.spiritconsortium.org/XMLSchema/"
            self.standard, self.version = spirit_ns.removeprefix(schema_root).split("/", 1)
            print(f"  {ARROW} Standard  : '{self.standard}'")
            print(f"  {ARROW} Version   : '{self.version}'")
            self.schema = f"{spirit_ns}/index.xsd"
            self.is_spirit = True
        elif ipxact_ns:
            schema_root = "http://www.accellera.org/XMLSchema/"
            self.standard, self.version = ipxact_ns.removeprefix(schema_root).split("/", 1)
            print(f"  {ARROW} Standard  : '{self.standard}'")
            print(f"  {ARROW} Version   : '{self.version}'")
            self.schema = f"{ipxact_ns}/index.xsd"
            self.is_ipxact = True
        else:  # pragma: no cover - defensive
            print("Namespace not found!")
            print("File is neither a well formed SPIRIT or IPXACT.")
            raise ValueError("Unsupported XML namespace for IP-XACT/SPIRIT")
        return None

    # Note: Legacy builder/to_xml helpers were removed (no backward compatibility required).

    # ------------------------------------------------------------------
    def serialize(self, obj: object) -> str:
        """Serialize ``obj`` using the shared serializer.

        Parameters
        ----------
        obj: object
            The dataclass instance to serialize.

        Returns
        -------
        str
            The serialized XML content.
        """
        return self.serializer().render(obj)

    # ------------------------------------------------------------------
    @classmethod
    def deserialize(cls, xml: str, cls_type: type[T]) -> T:
        """Deserialize ``xml`` string into an instance of ``cls_type``.

        Parameters
        ----------
        xml: str
            XML text to parse.
        cls_type: type[T]
            Target dataclass type.

        Returns
        -------
        T
            The deserialized object instance.
        """
        return cls.parser().from_string(xml, cls_type)
