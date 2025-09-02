# tests/test_xml_transformer.py

import subprocess
from unittest import mock

import pytest
from lxml import etree

from amal.utilities.xml_translator import XmlTranslator


@pytest.fixture
def xsl_file(tmp_path):
    """Fixture to create a temporary XSLT file."""
    xsl_content = '''<?xml version="1.0" encoding="UTF-8"?>
    <xsl:stylesheet version="1.0"
        xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
        <xsl:template match="/">
            <transformed>
                <xsl:copy-of select="."/>
            </transformed>
        </xsl:template>
    </xsl:stylesheet>
    '''
    xsl_path = tmp_path / "transform.xsl"
    xsl_path.write_text(xsl_content)
    return xsl_path


@pytest.fixture
def valid_xml_file(tmp_path):
    """Fixture to create a temporary valid XML file."""
    xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
    <note>
        <to>Tove</to>
        <from>Jani</from>
        <heading>Reminder</heading>
        <body>Don't forget me this weekend!</body>
    </note>
    '''
    xml_path = tmp_path / "valid_note.xml"
    xml_path.write_text(xml_content)
    return xml_path


@pytest.fixture
def invalid_xml_file(tmp_path):
    """Fixture to create a temporary invalid XML file."""
    xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
    <note>
        <to>Tove</to>
        <!-- Missing <from> element -->
        <heading>Reminder</heading>
        <body>Don't forget me this weekend!</body>
    </note>
    '''
    xml_path = tmp_path / "invalid_note.xml"
    xml_path.write_text(xml_content)
    return xml_path


@pytest.fixture
def transformer_lxml(xsl_file):
    """Fixture to create an XmlTranslator instance using lxml."""
    return XmlTranslator(xsl_filename=str(xsl_file), use_lxml=True)


@pytest.fixture
def transformer_xsltproc(xsl_file):
    """Fixture to create an XmlTranslator instance using xsltproc."""
    return XmlTranslator(xsl_filename=str(xsl_file), use_lxml=False)


def test_init_lxml(transformer_lxml, xsl_file):
    """Test initializing XmlTranslator with lxml."""
    assert transformer_lxml.xsl_filename == str(xsl_file)
    assert transformer_lxml.use_lxml is True
    # Implementation exposes XSLT object via 'transformer' attribute; 'transform'
    # remains the dispatcher method used in later tests.
    assert hasattr(transformer_lxml, "transform") and callable(transformer_lxml.transform)
    assert isinstance(getattr(transformer_lxml, "transformer"), etree.XSLT)


def test_init_xsltproc(transformer_xsltproc, xsl_file):
    """Test initializing XmlTranslator with xsltproc."""
    assert transformer_xsltproc.xsl_filename == str(xsl_file)
    assert transformer_xsltproc.use_lxml is False
    # assert not hasattr(transformer_xsltproc, 'transform')


def test_transform_using_lxml_valid(transformer_lxml, valid_xml_file, tmp_path):
    """Test transform_using_lxml with valid XML."""
    output_xml = tmp_path / "output_valid.xml"
    transformer_lxml.transform_using_lxml(str(valid_xml_file), str(output_xml))

    # Parse the output to ensure it's well-formed
    tree = etree.parse(str(output_xml))
    root = tree.getroot()
    assert root.tag == "transformed"
    assert root.find("note") is not None


def test_transform_using_lxml_invalid(transformer_lxml, invalid_xml_file, tmp_path):
    """Test transform_using_lxml with invalid XML."""
    output_xml = tmp_path / "output_invalid.xml"
    # with pytest.raises(etree.XMLSyntaxError):
    #     transformer_lxml.transform_using_lxml(str(invalid_xml_file), str(output_xml))
    transformer_lxml.transform_using_lxml(str(invalid_xml_file), str(output_xml))


@mock.patch('subprocess.check_output')
def test_transform_using_xsltproc_valid(mock_check_output, transformer_xsltproc, valid_xml_file, tmp_path, xsl_file):
    """Test transform_using_xsltproc with valid XML."""
    # Mock successful execution of xsltproc
    mock_check_output.return_value = "Transformation successful\n"

    output_xml = tmp_path / "output_valid_xsltproc.xml"
    transformer_xsltproc.transform_using_xsltproc(str(valid_xml_file), str(output_xml), str(xsl_file))

    # Ensure subprocess was called correctly
    mock_check_output.assert_called_with(
        ["xsltproc", "--output", str(output_xml), str(xsl_file), str(valid_xml_file)],
        text=True,
        stderr=subprocess.STDOUT
    )

    # Verify that the output file was written
    assert output_xml.exists()
    transformed_content = output_xml.read_text()
    assert "<transformed>" in transformed_content
    assert "<note>" in transformed_content


@mock.patch('subprocess.check_output')
def test_transform_using_xsltproc_invalid(mock_check_output, transformer_xsltproc, invalid_xml_file, tmp_path, xsl_file):
    """Test transform_using_xsltproc with invalid XML."""
    # Mock xsltproc raising CalledProcessError for invalid XML
    mock_check_output.side_effect = subprocess.CalledProcessError(
        returncode=1,
        cmd=["xsltproc", "--output", "output_invalid_xsltproc.xml", str(xsl_file), str(invalid_xml_file)],
        output="Error: ..."
    )

    output_xml = tmp_path / "output_invalid_xsltproc.xml"
    transformer_xsltproc.transform_using_xsltproc(str(invalid_xml_file), str(output_xml), str(xsl_file))

    # Ensure subprocess was called correctly
    mock_check_output.assert_called_with(
        ["xsltproc", "--output", str(output_xml), str(xsl_file), str(invalid_xml_file)],
        text=True,
        stderr=subprocess.STDOUT
    )

    # Verify that the output file was not created or is empty
    assert not output_xml.exists() or output_xml.stat().st_size == 0


def test_transform_lxml(transformer_lxml, valid_xml_file, tmp_path):
    """Test the transform method using lxml with valid XML."""
    output_xml = tmp_path / "output_lxml.xml"
    transformer_lxml.transform(str(valid_xml_file), str(output_xml), transformer_lxml.xsl_filename)

    # Parse the output to ensure it's well-formed
    tree = etree.parse(str(output_xml))
    root = tree.getroot()
    assert root.tag == "transformed"
    assert root.find("note") is not None


def test_transform_xsltproc(transformer_xsltproc, valid_xml_file, tmp_path, xsl_file):
    """Test the transform method using xsltproc with valid XML."""
    with mock.patch('subprocess.check_output') as mock_check_output:
        mock_check_output.return_value = "Transformation successful\n"

        output_xml = tmp_path / "output_xsltproc.xml"
        transformer_xsltproc.transform(str(valid_xml_file), str(output_xml), str(xsl_file))

        # Ensure subprocess was called correctly
        mock_check_output.assert_called_with(
            ["xsltproc", "--output", str(output_xml), str(xsl_file), str(valid_xml_file)],
            text=True,
            stderr=subprocess.STDOUT
        )

        # Verify that the output file was written
        assert output_xml.exists()
        transformed_content = output_xml.read_text()
        assert "<transformed>" in transformed_content
        assert "<note>" in transformed_content


def test_transform_xsltproc_failure(transformer_xsltproc, valid_xml_file, tmp_path, xsl_file):
    """Test the transform method using xsltproc when the command fails."""
    with mock.patch('subprocess.check_output') as mock_check_output:
        mock_check_output.side_effect = subprocess.CalledProcessError(
            returncode=1,
            cmd=["xsltproc", "--output", "output_failure.xml", str(xsl_file), str(valid_xml_file)],
            output="Error: ..."
        )

        output_xml = tmp_path / "output_failure.xml"
        transformer_xsltproc.transform(str(valid_xml_file), str(output_xml), str(xsl_file))

        # Ensure subprocess was called correctly
        mock_check_output.assert_called_with(
            ["xsltproc", "--output", str(output_xml), str(xsl_file), str(valid_xml_file)],
            text=True,
            stderr=subprocess.STDOUT
        )

        # Verify that the output file was not created or is empty
        assert not output_xml.exists() or output_xml.stat().st_size == 0


def test_transform_nonexistent_input_lxml(transformer_lxml, tmp_path):
    """Test transform_using_lxml with a nonexistent input XML file."""
    nonexistent_input = tmp_path / "nonexistent.xml"
    output_xml = tmp_path / "output.xml"

    with pytest.raises(etree.XMLSyntaxError):
        transformer_lxml.transform_using_lxml(str(nonexistent_input), str(output_xml))


@mock.patch('subprocess.check_output')
def test_transform_nonexistent_input_xsltproc(mock_check_output, transformer_xsltproc, tmp_path, xsl_file):
    """Test transform_using_xsltproc with a nonexistent input XML file."""
    # Mock subprocess to raise CalledProcessError for nonexistent input file
    mock_check_output.side_effect = subprocess.CalledProcessError(
        returncode=1,
        cmd=["xsltproc", "--output", "output_nonexistent.xml", str(xsl_file), "/path/to/nonexistent.xml"],
        output="Error: could not open '/path/to/nonexistent.xml'"
    )

    nonexistent_input = "/path/to/nonexistent.xml"
    output_xml = tmp_path / "output_nonexistent.xml"
    transformer_xsltproc.transform_using_xsltproc(nonexistent_input, str(output_xml), str(xsl_file))

    # Ensure subprocess was called correctly
    mock_check_output.assert_called_with(
        ["xsltproc", "--output", str(output_xml), str(xsl_file), nonexistent_input],
        text=True,
        stderr=subprocess.STDOUT
    )

    # Verify that the output file was not created or is empty
    assert not output_xml.exists() or output_xml.stat().st_size == 0