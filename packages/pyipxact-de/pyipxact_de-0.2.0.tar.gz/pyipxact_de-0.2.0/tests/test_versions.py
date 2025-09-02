# test_versions.py

import pytest

from org.accellera import Standard

    # "get_ns_url",


# Test Initialization with Valid Standards and Versions
@pytest.mark.parametrize(
    "standard, version",
    [
        ("spirit", "1.0"),
        ("spirit", "1.1"),
        ("spirit", "1.2"),
        ("spirit", "1.4"),
        ("spirit", "1.5"),
        ("spirit", "1685-2009"),
        ("ipxact", "1685-2014"),
        ("ipxact", "1685-2022"),
    ],
)
def test_init_valid(standard, version) -> None:
    # Should not raise
    Standard.validate(standard, version)
    expected_schema_root = (
        "http://www.spiritconsortium.org/XMLSchema"
        if standard.lower() == "spirit"
        else "http://www.accellera.org/XMLSchema"
    )
    assert Standard.get(standard).schema_root == expected_schema_root


# Test Initialization with Invalid Standard
def test_init_invalid_standard() -> None:
    with pytest.raises(ValueError) as excinfo:
        Standard.validate("unknown_standard", "1.0")
    assert "Unknown standard" in str(excinfo.value)


# Test Initialization with Invalid Version for Spirit
@pytest.mark.parametrize("version", ["2.0", "1.3", "invalid-version"])
def test_init_invalid_spirit_version(version) -> None:
    with pytest.raises(ValueError) as excinfo:
        Standard.validate("spirit", version)
    assert "Unknown version" in str(excinfo.value)


# Test Initialization with Invalid Version for Ipxact
@pytest.mark.parametrize("version", ["1685-2010", "2020", "invalid-version"])
def test_init_invalid_ipxact_version(version) -> None:
    with pytest.raises(ValueError) as excinfo:
        Standard.validate("ipxact", version)
    assert "Unknown version" in str(excinfo.value)


# Test get_ns_map for various standards and versions
@pytest.mark.parametrize(
    "standard, version, expected_ns_map",
    [
        (
            "spirit",
            "1.0",
            {
                "xsi": "http://www.w3.org/2001/XMLSchema-instance",
                "spirit": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1.0",
            },
        ),
        (
            "spirit",
            "1.1",
            {
                "xsi": "http://www.w3.org/2001/XMLSchema-instance",
                "spirit": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1.1",
            },
        ),
        (
            "spirit",
            "1.2",
            {
                "xsi": "http://www.w3.org/2001/XMLSchema-instance",
                "spirit": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1.2",
            },
        ),
        (
            "spirit",
            "1.4",
            {
                "xsi": "http://www.w3.org/2001/XMLSchema-instance",
                "spirit": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1.4",
            },
        ),
        (
            "spirit",
            "1.5",
            {
                "xsi": "http://www.w3.org/2001/XMLSchema-instance",
                "spirit": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1.5",
            },
        ),
        (
            "spirit",
            "1685-2009",
            {
                "xsi": "http://www.w3.org/2001/XMLSchema-instance",
                "spirit": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009",
            },
        ),
        (
            "ipxact",
            "1685-2014",
            {
                "xsi": "http://www.w3.org/2001/XMLSchema-instance",
                "ipxact": "http://www.accellera.org/XMLSchema/IPXACT/1685-2014",
            },
        ),
        (
            "ipxact",
            "1685-2022",
            {
                "xsi": "http://www.w3.org/2001/XMLSchema-instance",
                "ipxact": "http://www.accellera.org/XMLSchema/IPXACT/1685-2022",
            },
        ),
    ]
)
def test_get_ns_map(standard, version, expected_ns_map) -> None:
    Standard.validate(standard, version)
    ns_map = Standard.namespace_map_for(standard, version)
    assert ns_map == expected_ns_map


# Test get_get_schema_location for various standards and versions
@pytest.mark.parametrize(
    "standard, version, expected_location",
    [
        (
            "spirit",
            "1.0",
            "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1.0 http://www.spiritconsortium.org/XMLSchema/SPIRIT/1.0/index.xsd",
        ),
        (
            "spirit",
            "1.1",
            "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1.1 http://www.spiritconsortium.org/XMLSchema/SPIRIT/1.1/index.xsd",
        ),
        (
            "spirit",
            "1.2",
            "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1.2 http://www.spiritconsortium.org/XMLSchema/SPIRIT/1.2/index.xsd",
        ),
        (
            "spirit",
            "1.4",
            "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1.4 http://www.spiritconsortium.org/XMLSchema/SPIRIT/1.4/index.xsd",
        ),
        (
            "spirit",
            "1.5",
            "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1.5 http://www.spiritconsortium.org/XMLSchema/SPIRIT/1.5/index.xsd",
        ),
        (
            "spirit",
            "1685-2009",
            "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009 http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009/index.xsd",
        ),
        (
            "ipxact",
            "1685-2014",
            "http://www.accellera.org/XMLSchema/IPXACT/1685-2014 http://www.accellera.org/XMLSchema/IPXACT/1685-2014/index.xsd",
        ),
        (
            "ipxact",
            "1685-2022",
            "http://www.accellera.org/XMLSchema/IPXACT/1685-2022 http://www.accellera.org/XMLSchema/IPXACT/1685-2022/index.xsd",
        ),
    ],
)
def test_get_get_schema_location(standard, version, expected_location) -> None:
    Standard.validate(standard, version)
    loc = Standard.schema_location_for(standard, version)
    assert loc == expected_location
