"""Utilities to send Cisco Discovery Protocol (CDP) packets using Scapy."""

from .cdp_sender import send_cdp_packet, parse_args, main

__all__ = [
    "send_cdp_packet",
    "parse_args",
    "main",
]
