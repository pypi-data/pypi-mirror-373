from scapy.all import *
from scapy.layers.l2 import Ether, SNAP, LLC
from scapy.contrib.cdp import (
    CDPv2_HDR,
    CDPMsgDeviceID,
    CDPMsgPortID,
    CDPMsgSoftwareVersion,
    CDPMsgPlatform,
    CDPMsgAddr,
    CDPAddrRecordIPv4,
    CDPMsgCapabilities,
)
import argparse
import json
import time


def send_cdp_packet(interface, device_id, software_version, platform, ttl, capabilities):
    """Send a CDP packet with customizable fields."""
    # Get the MAC address and IP of the interface
    src_mac = get_if_hwaddr(interface)
    src_ip = get_if_addr(interface)
    print(f"Using source MAC address: {src_mac}")
    print(f"Using source IP address: {src_ip}")

    # Create base packet with CDP multicast address and correct source MAC
    eth = Ether(dst="01:00:0c:cc:cc:cc", src=src_mac)
    llc = LLC(dsap=0xAA, ssap=0xAA, ctrl=3)
    snap = SNAP(OUI=0x00000C, code=0x2000)

    # Create the address record
    addr_record = CDPAddrRecordIPv4(addr=src_ip)

    cdp = CDPv2_HDR(
        ttl=ttl,
        msg=[
            CDPMsgDeviceID(val=device_id),
            CDPMsgAddr(naddr=1, addr=[addr_record]),
            CDPMsgPortID(iface=interface),
            CDPMsgCapabilities(cap=capabilities),
            CDPMsgSoftwareVersion(val=software_version),
            CDPMsgPlatform(val=platform),
        ],
    )

    packet = eth / llc / snap / cdp

    try:
        while True:
            sendp(packet, iface=interface, verbose=False)
            print(
                f"CDP packet sent on interface {interface} at {time.strftime('%H:%M:%S')}"
            )
            time.sleep(60)  # Wait 60 seconds before next packet
    except KeyboardInterrupt:
        print("\nStopping CDP sender...")
    except Exception as e:  # pragma: no cover - runtime safeguard
        print(f"Error sending packet: {e}")


def parse_args():
    parser = argparse.ArgumentParser(description="Send customizable CDP packets.")
    parser.add_argument("--interface", default="eth0", help="Interface to send CDP packets on.")
    parser.add_argument("--device-id", dest="device_id", default="Cisco_AP_01", help="Device ID to advertise.")
    parser.add_argument("--software-version", dest="software_version", default="AP Software 8.5.1", help="Software version string.")
    parser.add_argument("--platform", default="Cisco Aironet 2800", help="Platform string.")
    parser.add_argument("--ttl", type=int, default=180, help="TTL in seconds.")
    parser.add_argument(
        "--capabilities",
        type=lambda x: int(x, 0),
        default=0x0038,
        help="Capabilities bitmap (e.g., 0x0038).",
    )
    parser.add_argument("--config", help="Path to JSON file with default argument values.")
    args = parser.parse_args()
    if args.config:
        with open(args.config) as f:
            cfg = json.load(f)
        for field in ["interface", "device_id", "software_version", "platform", "ttl", "capabilities"]:
            if field in cfg and getattr(args, field) == parser.get_default(field):
                value = cfg[field]
                if field in {"ttl", "capabilities"} and isinstance(value, str):
                    value = int(value, 0)
                setattr(args, field, value)
    return args


def main() -> None:
    """Entry point for the ``cdp-sender`` console script."""
    args = parse_args()

    # List available interfaces
    print("Available interfaces:")
    print(get_if_list())

    print(f"Starting CDP sender on {args.interface}")
    print("Press Ctrl+C to stop")
    send_cdp_packet(
        interface=args.interface,
        device_id=args.device_id,
        software_version=args.software_version,
        platform=args.platform,
        ttl=args.ttl,
        capabilities=args.capabilities,
    )


if __name__ == "__main__":  # pragma: no cover - manual execution
    main()
