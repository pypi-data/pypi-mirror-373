from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum, IntFlag
from typing import List, Optional, Union, Literal


# ---------- Basic aliases ----------
MacAddress = str   # e.g. "01:00:0c:cc:cc:cc"
Hex8 = str         # e.g. "0xAA"
Hex16 = str        # e.g. "0x1234"


# ---------- Ethernet + LLC/SNAP ----------
@dataclass
class EthernetLLCSNAP:
    dsap: Hex8        # "0xAA"
    ssap: Hex8        # "0xAA"
    control: Hex8     # "0x03"
    oui: str          # "0x00000C" (Cisco)
    protocol_id: str  # "0x2000" (CDP)

@dataclass
class EthernetHeader:
    destination_mac: MacAddress  # 01:00:0c:cc:cc:cc for CDP
    source_mac: MacAddress
    llc_snap: EthernetLLCSNAP


# ---------- CDP header ----------
@dataclass
class CDPHeader:
    version: int    # 1 or 2
    ttl: int        # seconds (e.g. 180)
    checksum: Hex16 # 16-bit internet checksum (hex string)


# ---------- Enums ----------
class CDPTlvType(IntEnum):
    DeviceId           = 0x0001
    Address            = 0x0002
    PortId             = 0x0003
    Capabilities       = 0x0004
    SoftwareVersion    = 0x0005
    Platform           = 0x0006
    IpNetworkPrefix    = 0x0007
    ProtocolHello      = 0x0008
    VtpDomain          = 0x0009
    NativeVlan         = 0x000A
    Duplex             = 0x000B
    TrustBitmap        = 0x000C
    UntrustedPortCos   = 0x000D
    PowerAvailable     = 0x0010
    Mtu                = 0x0011
    ManagementAddress  = 0x0016
    Unknown            = 0xFFFF

class CDPCapability(IntFlag):
    Router             = 0x01
    TransparentBridge  = 0x02
    SourceRouteBridge  = 0x04
    Switch             = 0x08
    Host               = 0x10
    IGMP               = 0x20
    Repeater           = 0x40
    # keep as IntFlag for bitwise ops


# ---------- TLV base ----------
@dataclass
class BaseTlv:
    type: int         # usually CDPTlvType, but int to allow unknowns
    length: int       # total TLV length (incl. type+length+value)


# ---------- Specific TLVs ----------
@dataclass
class DeviceIdTlv(BaseTlv):
    type: CDPTlvType = field(default=CDPTlvType.DeviceId, init=False)
    value: str = ""

@dataclass
class PortIdTlv(BaseTlv):
    type: CDPTlvType = field(default=CDPTlvType.PortId, init=False)
    value: str = ""

@dataclass
class PlatformTlv(BaseTlv):
    type: CDPTlvType = field(default=CDPTlvType.Platform, init=False)
    value: str = ""

@dataclass
class SoftwareVersionTlv(BaseTlv):
    type: CDPTlvType = field(default=CDPTlvType.SoftwareVersion, init=False)
    value: str = ""

@dataclass
class NativeVlanTlv(BaseTlv):
    type: CDPTlvType = field(default=CDPTlvType.NativeVlan, init=False)
    value: int = 1

@dataclass
class DuplexTlv(BaseTlv):
    type: CDPTlvType = field(default=CDPTlvType.Duplex, init=False)
    # typically "half" or "full"; keep str to tolerate vendor quirks
    value: str = "full"

@dataclass
class CapabilitiesTlv(BaseTlv):
    type: CDPTlvType = field(default=CDPTlvType.Capabilities, init=False)
    # bitmask of CDPCapability
    value: int = 0

# Address TLV internals
@dataclass
class CDPAddressEntry:
    protocol_type: int        # e.g. 0xCC (NLPID), 0xAA (SNAP)
    protocol: bytes           # raw protocol bytes
    address: bytes            # raw address bytes
    decoded_ip: Optional[str] = None   # e.g. "192.168.1.1" or "2001:db8::1"
    family: Optional[Literal["IPv4", "IPv6"]] = None

@dataclass
class AddressTlvValue:
    number_of_addresses: int
    addresses: List[CDPAddressEntry]

@dataclass
class AddressTlv(BaseTlv):
    type: CDPTlvType = field(default=CDPTlvType.Address, init=False)
    value: AddressTlvValue = field(default_factory=lambda: AddressTlvValue(0, []))

# Unknown / passthrough
@dataclass
class UnknownTlv(BaseTlv):
    # keep raw bytes so you can parse later if needed
    value: bytes = b""


# ---------- TLV union for typing ----------
CDPTlv = Union[
    DeviceIdTlv,
    AddressTlv,
    PortIdTlv,
    CapabilitiesTlv,
    SoftwareVersionTlv,
    PlatformTlv,
    NativeVlanTlv,
    DuplexTlv,
    UnknownTlv,
]


# ---------- Full frame ----------
@dataclass
class CDPBody:
    header: CDPHeader
    tlvs: List[CDPTlv]

@dataclass
class CDPFrame:
    ethernet: EthernetHeader
    cdp: CDPBody


# ---------- Helpers ----------
def decode_capabilities(bits: int) -> List[CDPCapability]:
    """Return set bits as a list of CDPCapability flags."""
    flags: List[CDPCapability] = []
    for cap in CDPCapability:
        if bits & cap:
            flags.append(cap)
    return flags
