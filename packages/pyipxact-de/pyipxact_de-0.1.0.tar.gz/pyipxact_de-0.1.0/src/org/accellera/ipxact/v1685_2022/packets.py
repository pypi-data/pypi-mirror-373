from dataclasses import dataclass

from org.accellera.ipxact.v1685_2022.port_packets_type import PortPacketsType

__NAMESPACE__ = "http://www.accellera.org/XMLSchema/IPXACT/1685-2022"


@dataclass(slots=True)
class Packets(PortPacketsType):
    class Meta:
        name = "packets"
        namespace = "http://www.accellera.org/XMLSchema/IPXACT/1685-2022"
