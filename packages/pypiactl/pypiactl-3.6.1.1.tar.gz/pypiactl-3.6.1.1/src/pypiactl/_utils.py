import ipaddress
from typing import Optional

from ._types import (
    PIAConnectionState,
    PIAInformationType,
    PIAPortForwardStatus,
    PIAProtocol,
)


def string_to_bool(string: str) -> bool:
    return string == "true"


def to_integer(string: str) -> Optional[int]:
    try:
        return int(string)
    except Exception:
        return None


def to_ipv4(string: str) -> Optional[ipaddress.IPv4Address]:
    try:
        return ipaddress.IPv4Address(string)
    except Exception:
        return None


def parse(raw_data: str, info_type: PIAInformationType):
    if info_type in (
        PIAInformationType.ALLOW_LAN,
        PIAInformationType.DEBUG_LOGGING,
        PIAInformationType.REQUEST_PORT_FORWARD,
    ):
        return string_to_bool(raw_data)

    elif info_type == PIAInformationType.CONNECTION_STATE:
        return PIAConnectionState.from_value(raw_data)

    elif info_type == PIAInformationType.PORT_FORWARD:
        port = to_integer(raw_data)
        if port:
            return port
        else:
            return PIAPortForwardStatus.from_value(raw_data)

    elif info_type == PIAInformationType.PROTOCOL:
        return PIAProtocol.from_value(raw_data)

    elif info_type in (PIAInformationType.PUB_IP, PIAInformationType.VPN_IP):
        return to_ipv4(raw_data)

    elif info_type == PIAInformationType.REGION:
        return raw_data

    elif info_type == PIAInformationType.REGIONS:
        return set(raw_data.splitlines())

    else:
        return None
