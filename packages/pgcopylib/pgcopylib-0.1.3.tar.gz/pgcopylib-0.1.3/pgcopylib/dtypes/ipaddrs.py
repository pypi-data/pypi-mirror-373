from ipaddress import (
    IPv4Address,
    IPv4Network,
    IPv6Address,
    IPv6Network,
)
from struct import (
    pack,
    unpack,
)

from ..enums import PGOid
from ..errors import PGCopyRecordError
from .nullables import (
    read_nullable,
    write_nullable,
)


IpAddr = {
    2: IPv4Address,
    3: IPv6Address,
    IPv4Address: 2,
    IPv4Network: 2,
    IPv6Network: 3,
    IPv6Address: 3,
}
IpNet = {
    IPv4Address: IPv4Network,
    IPv6Address: IPv6Network,
}


@read_nullable
def to_network(
    binary_data: bytes,
) -> IPv4Address | IPv6Address | IPv4Network | IPv6Network:
    """Unpack inet or cidr value."""

    ip_family, ip_netmask, is_cidr, ip_length, ip_data = unpack(
        f"!4B{len(binary_data) - 4}s",
        binary_data,
    )

    if ip_length != len(ip_data):
        raise PGCopyRecordError("Invalid IP data")

    ip_addr: IPv4Address | IPv6Address = IpAddr[ip_family](ip_data)

    if is_cidr:
        return IpNet[ip_addr.__class__](
            f"{ip_addr}/{ip_netmask}",
            strict=False,
        )

    return ip_addr


@write_nullable
def from_network(
    dtype_value: IPv4Address | IPv6Address | IPv4Network | IPv6Network,
    pg_oid: PGOid,
) -> bytes:
    """Pack inet or cidr value."""

    if isinstance(dtype_value, IPv4Address | IPv6Address):
        ip_addr = dtype_value.packed
        ip_netmask = dtype_value.max_prefixlen
        is_cidr = 0
    elif isinstance(dtype_value, IPv4Network | IPv6Network):
        ip_addr = dtype_value.network_address.packed
        ip_netmask = dtype_value._prefixlen
        is_cidr = 1

    ip_family: int = IpAddr[dtype_value]

    return pack(
        f"!4B{len(ip_addr)}s",
        ip_family,
        ip_netmask,
        is_cidr,
        len(ip_addr),
        ip_addr,
    )
