# tests/test_xml_validator.py

import subprocess
from unittest import mock

import pytest
from lxml import etree

from amal.utilities.xml_validator import XmlValidator


@pytest.fixture
def xsd_file(tmp_path):
    """Fixture to create a temporary XSD schema file."""
    schema_content = '''<?xml version="1.0" encoding="UTF-8"?>
    <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
        <xs:element name="note">
            <xs:complexType>
                <xs:sequence>
                    <xs:element name="to" type="xs:string"/>
                    <xs:element name="from" type="xs:string"/>
                    <xs:element name="heading" type="xs:string"/>
                    <xs:element name="body" type="xs:string"/>
                </xs:sequence>
            </xs:complexType>
        </xs:element>
    </xs:schema>
    '''
    xsd_path = tmp_path / "note.xsd"
    xsd_path.write_text(schema_content)
    return xsd_path


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
def xml_validator(xsd_file):
    """Fixture to create an instance of XmlValidator using lxml."""
    return XmlValidator(xsd_filename=str(xsd_file), use_lxml=True)


def test_init_valid(xml_validator, xsd_file):
    """Test initializing XmlValidator with valid XSD file."""
    assert xml_validator.xsd_filename == str(xsd_file)
    assert xml_validator.use_lxml is True
    assert isinstance(xml_validator.xmlschema, etree.XMLSchema)


def test_init_invalid_xsd(tmp_path):
    """Test initializing XmlValidator with an invalid XSD file."""
    invalid_xsd_path = tmp_path / "invalid.xsd"
    invalid_xsd_path.write_text("<invalid></xsd>")  # Malformed XML

    # with pytest.raises(etree.XMLSchemaParseError):
    with pytest.raises(etree.XMLSyntaxError):
        XmlValidator(xsd_filename=str(invalid_xsd_path), use_lxml=True)


def test_validate_using_lxml_valid(xml_validator, valid_xml_file):
    """Test validate_using_lxml method with a valid XML file."""
    is_valid = xml_validator.validate_using_lxml(str(valid_xml_file))
    assert is_valid is True


def test_validate_using_lxml_invalid(xml_validator, invalid_xml_file):
    """Test validate_using_lxml method with an invalid XML file."""
    is_valid = xml_validator.validate_using_lxml(str(invalid_xml_file))
    assert is_valid is False


@mock.patch('subprocess.check_output')
def test_validate_using_xmllint_valid(mock_check_output, xml_validator, valid_xml_file):
    """Test validate_using_xmllint method with a valid XML file."""
    # Mock xmllint to return successful validation
    mock_check_output.return_value = "valid\n"

    # Initialize XmlValidator with use_lxml=False to use xmllint
    validator = XmlValidator(xsd_filename=xml_validator.xsd_filename, use_lxml=False)

    is_valid = validator.validate_using_xmllint(str(valid_xml_file))
    assert is_valid is True
    mock_check_output.assert_called_with(
        ("xmllint", "--schema", validator.xsd_filename, "--noout", str(valid_xml_file)),
        text=True,
        stderr=subprocess.STDOUT
    )


@mock.patch('subprocess.check_output')
def test_validate_using_xmllint_invalid(mock_check_output, xml_validator, invalid_xml_file):
    """Test validate_using_xmllint method with an invalid XML file."""
    # Mock xmllint to raise CalledProcessError for invalid XML
    mock_check_output.side_effect = subprocess.CalledProcessError(
        returncode=1,
        cmd=("xmllint", "--schema", xml_validator.xsd_filename, "--noout", str(invalid_xml_file)),
        output="invalid\nError: ..."
    )

    # Initialize XmlValidator with use_lxml=False to use xmllint
    validator = XmlValidator(xsd_filename=xml_validator.xsd_filename, use_lxml=False)

    is_valid = validator.validate_using_xmllint(str(invalid_xml_file))
    assert is_valid is False
    mock_check_output.assert_called_with(
        ("xmllint", "--schema", validator.xsd_filename, "--noout", str(invalid_xml_file)),
        text=True,
        stderr=subprocess.STDOUT
    )


def test_validate_using_xmllint_command_failure(xml_validator, valid_xml_file):
    """Test validate_using_xmllint method when xmllint command fails."""
    # This test assumes that xmllint is not installed or the command fails
    # It should return False without raising an exception
    # To simulate this, we'll mock subprocess.check_output to raise CalledProcessError

    with mock.patch('subprocess.check_output', side_effect=subprocess.CalledProcessError(
        returncode=1,
        cmd=("xmllint", "--schema", xml_validator.xsd_filename, "--noout", str(valid_xml_file)),
        output="error"
    )):
        validator = XmlValidator(xsd_filename=xml_validator.xsd_filename, use_lxml=False)
        is_valid = validator.validate_using_xmllint(str(valid_xml_file))
        assert is_valid is False


def test_validate_using_lxml_nonexistent_xml(xml_validator):
    """Test validate_using_lxml method with a nonexistent XML file."""
    nonexistent_file = "/path/to/nonexistent.xml"
    # with pytest.raises(etree.XMLSyntaxError):
    with pytest.raises(OSError):
        xml_validator.validate_using_lxml(nonexistent_file)


@mock.patch('subprocess.check_output')
def test_validate_using_xmllint_nonexistent_xml(mock_check_output, xml_validator):
    """Test validate_using_xmllint method with a nonexistent XML file."""
    # Mock subprocess to raise CalledProcessError for nonexistent file
    mock_check_output.side_effect = subprocess.CalledProcessError(
        returncode=1,
        cmd=("xmllint", "--schema", xml_validator.xsd_filename, "--noout", "/path/to/nonexistent.xml"),
        output="error: can't open '/path/to/nonexistent.xml'"
    )

    validator = XmlValidator(xsd_filename=xml_validator.xsd_filename, use_lxml=False)
    is_valid = validator.validate_using_xmllint("/path/to/nonexistent.xml")
    assert is_valid is False
    mock_check_output.assert_called_with(
        ("xmllint", "--schema", validator.xsd_filename, "--noout", "/path/to/nonexistent.xml"),
        text=True,
        stderr=subprocess.STDOUT
    )