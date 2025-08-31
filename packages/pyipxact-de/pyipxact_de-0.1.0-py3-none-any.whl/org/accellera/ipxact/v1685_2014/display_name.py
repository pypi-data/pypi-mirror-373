from dataclasses import dataclass, field

__NAMESPACE__ = "http://www.accellera.org/XMLSchema/IPXACT/1685-2014"


@dataclass(slots=True)
class DisplayName:
    """Element name for display purposes.

    Typically a few words providing a more detailed and/or user-friendly
    name than the ipxact:name.
    """

    class Meta:
        name = "displayName"
        namespace = "http://www.accellera.org/XMLSchema/IPXACT/1685-2014"

    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
