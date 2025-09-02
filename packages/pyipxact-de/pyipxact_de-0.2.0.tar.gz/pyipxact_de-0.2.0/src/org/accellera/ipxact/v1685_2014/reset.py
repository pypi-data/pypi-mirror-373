from dataclasses import dataclass, field
from typing import Optional

from org.accellera.ipxact.v1685_2014.unsigned_bit_vector_expression import (
    UnsignedBitVectorExpression,
)

__NAMESPACE__ = "http://www.accellera.org/XMLSchema/IPXACT/1685-2014"


@dataclass(slots=True)
class Reset:
    """
    Register value at reset.

    :ivar value: The value itself.
    :ivar mask: Mask to be anded with the value before comparing to the
        reset value.
    :ivar reset_type_ref: Reference to a user defined resetType. Assumed
        to be HARD if not present.
    :ivar id:
    """

    class Meta:
        name = "reset"
        namespace = "http://www.accellera.org/XMLSchema/IPXACT/1685-2014"

    value: Optional[UnsignedBitVectorExpression] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    mask: Optional[UnsignedBitVectorExpression] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    reset_type_ref: Optional[str] = field(
        default=None,
        metadata={
            "name": "resetTypeRef",
            "type": "Attribute",
        },
    )
    id: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "namespace": "http://www.w3.org/XML/1998/namespace",
        },
    )
