# Base on: https://stackoverflow.com/a/37972081/1877238

import subprocess

from lxml import etree
from rich import print

from .globals import ARROW, CHECK, CROSS


class XmlValidator:
    """Validate XML instance documents against an XSD schema.

    Supports either in‑process validation via lxml or an external ``xmllint``
    invocation (useful for parity with existing tool flows and for test
    mocking). The selected backend is controlled via the ``use_lxml`` flag.

    Args:
        xsd_filename (str): Path to the XSD schema file.
        use_lxml (bool, optional): If True, use lxml for validation; if False
            call out to ``xmllint``. Defaults to True.

    Attributes:
        xsd_filename (str): Stored schema file location.
        use_lxml (bool): Active backend selector.
        xmlschema (etree.XMLSchema): Compiled schema (only when ``use_lxml``).
    """

    def __init__(self, xsd_filename: str, use_lxml: bool = True):
        self.use_lxml = use_lxml
        self.xsd_filename: str = xsd_filename

        if use_lxml:
            tree: etree.ElementTree = etree.parse(xsd_filename)
            self.xmlschema: etree.XMLSchema = etree.XMLSchema(tree)

    def validate_using_lxml(self, xml_filename: str) -> bool:
        """Validate an XML document using lxml's compiled schema.

        Args:
            xml_filename (str): Path to the XML instance document.

        Returns:
            bool: True if the document validates; False otherwise.
        """
        tree: etree.ElementTree = etree.parse(xml_filename)
        valid = self.xmlschema.validate(tree)  # type: ignore[attr-defined]
        return valid

    def validate_using_xmllint(self, xml_filename: str) -> bool:
        """Validate an XML document using the external xmllint tool.

        Args:
            xml_filename (str): Path to the XML instance document.

        Returns:
            bool: True if exit status indicates success; False otherwise.
        """
        command = ("xmllint", "--schema", self.xsd_filename, "--noout", xml_filename)

        print("  " + "-" * 80)
        valid: bool = True
        output: str = ""
        try:
            output = subprocess.check_output(command, text=True, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as exc:
            valid = False
            # Combined stdout/stderr from failed xmllint invocation.
            output = (exc.output or "")
            # + f"\n[exit status {exc.returncode}]"

        output = f"{output.strip()} {CHECK if valid else CROSS}"
        print(f"  {ARROW} {output}")

        return valid

    def validate(self, xml_filename: str) -> bool:
        """Validate an XML document dispatching to the configured backend.

        Args:
            xml_filename (str): Path to the XML instance document.

        Returns:
            bool: Validation result from the selected backend.
        """
        if self.use_lxml:
            return self.validate_using_lxml(xml_filename)
        else:
            return self.validate_using_xmllint(xml_filename)
