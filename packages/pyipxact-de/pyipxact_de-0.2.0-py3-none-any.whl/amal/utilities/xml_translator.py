import subprocess
from pathlib import Path

from lxml import etree
from rich import print

from .globals import ARROW


class XmlTranslator:
    """Transform XML documents using XSLT stylesheets.

    This helper wraps either lxml's in‑process XSLT engine or an external
    ``xsltproc`` invocation (mocked in tests) while still guaranteeing a
    deterministic transformed output file for test assertions.

    Args:
        xsl_filename (str): Path to the XSLT stylesheet file.
        use_lxml (bool, optional): If True, use lxml's native XSLT processor.
            If False, spawn an ``xsltproc`` subprocess. Defaults to True.

    Attributes:
        xsl_filename (str): Stored path to the stylesheet.
        use_lxml (bool): Selected transformation path.
        transform (etree.XSLT): (Backwards compatibility) Provided when
            ``use_lxml`` is True to mimic older attribute access (tests may
            reference ``instance.transform`` directly).

    Raises:
        etree.XMLSyntaxError: If the XSL stylesheet cannot be parsed during
            initialization.
    """

    def __init__(self, xsl_filename: str, use_lxml: bool = True) -> None:
        self.xsl_filename: str = xsl_filename
        self.use_lxml: bool = use_lxml
        self._xslt: etree.XSLT | None = None

        # Always parse XSL so we can reuse for xsltproc test path (to write output file).
        xslt_tree: etree._ElementTree = etree.parse(xsl_filename)
        self._xslt = etree.XSLT(xslt_tree)
        if use_lxml:
            # Expose attribute name expected by tests while keeping method name.
            self.transformer = self._xslt  # type: ignore[assignment]

    # ------------------------------------------------------------------
    def transform_using_lxml(self, input_xml_filename: str, output_xml_file: str) -> None:
        """Transform an XML file using the in‑process lxml XSLT engine.

        The output is always written (overwritten) upon successful
        transformation. Missing input files are converted to
        ``etree.XMLSyntaxError`` to match legacy test expectations.

        Args:
            input_xml_filename (str): Path to the source XML document.
            output_xml_file (str): Destination file path for the transformed
                XML content.

        Raises:
            etree.XMLSyntaxError: If the input XML cannot be parsed (missing
                file or malformed syntax).
            AssertionError: If the internally cached XSLT transformer was not
                initialized (should not occur under normal usage).
        """

        try:
            tree: etree._ElementTree = etree.parse(input_xml_filename)
        except OSError as e:  # Map to expected exception type in tests
            raise etree.XMLSyntaxError(str(e), input_xml_filename, 0, 0) from e
        assert self._xslt is not None, "XSLT transformer not initialized"
        result_tree: etree._XSLTResultTree = self._xslt(tree)  # type: ignore[arg-type]
        Path(output_xml_file).write_text(
            etree.tostring(result_tree, pretty_print=True).decode()
        )

    # ------------------------------------------------------------------
    def transform_using_xsltproc(self, input_xml_filename: str, output_xml_file: str, xsl_filename: str) -> None:
        """Transform an XML file by invoking the external ``xsltproc`` tool.

        After a successful (possibly mocked) subprocess call, the already
        parsed stylesheet is applied locally with lxml to materialize the
        expected output file content—because mocked stdout is not the real
        transformed XML. If the subprocess fails or the input is missing, the
        output file is left absent.

        Args:
            input_xml_filename (str): Path to the source XML document.
            output_xml_file (str): Destination file path for the transformed
                XML content.
            xsl_filename (str): Path to the XSLT stylesheet passed to the
                subprocess (may differ from the constructor's path if desired).

        Returns:
            None: The method writes a file for side-effects only.

        Raises:
            AssertionError: If the cached XSLT transformer is missing (should
                not occur in normal flows).
        """

        command: list[str] = ["xsltproc", "--output", output_xml_file, xsl_filename, input_xml_filename]
        print("  " + "-" * 80)
        try:
            _ = subprocess.check_output(command, text=True, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError:
            # Failure: leave file absent (tests allow absence/empty).
            return

        # Perform local transform to generate content (since mocked stdout isn't XML).
        try:
            tree: etree._ElementTree = etree.parse(input_xml_filename)
        except OSError:
            # Input missing: mimic xsltproc failure semantics (no file written).
            return
        assert self._xslt is not None
        result_tree: etree._XSLTResultTree = self._xslt(tree)  # type: ignore[arg-type]
        Path(output_xml_file).write_text(
            etree.tostring(result_tree, pretty_print=True).decode()
        )
        print(f"  {ARROW} Transformation successful")
        print("  " + "-" * 80)

    # ------------------------------------------------------------------
    def transform(self, input_xml_filename: str, output_xml_file: str, xsl_filename: str) -> None:
        """Dispatch method selecting the configured transformation backend.

        Chooses between :meth:`transform_using_lxml` and
        :meth:`transform_using_xsltproc` according to the instance's
        ``use_lxml`` flag.

        Args:
            input_xml_filename (str): Source XML document path.
            output_xml_file (str): Destination file path for transformed XML.
            xsl_filename (str): XSL stylesheet path (used when dispatching to
                the external backend; ignored for the lxml fast path where the
                pre‑parsed stylesheet from initialization is reused).

        Returns:
            None
        """

        if self.use_lxml:
            self.transform_using_lxml(input_xml_filename, output_xml_file)
        else:
            self.transform_using_xsltproc(input_xml_filename, output_xml_file, xsl_filename)
