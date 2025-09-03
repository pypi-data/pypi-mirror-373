from enum import Enum
from typing import Generic, TypeVar

# Generic Declarations

S = TypeVar("S")
D = TypeVar("D", covariant=True)

T = TypeVar("T")

# Types


class PIACommandResult(Generic[S, D]):
    def __init__(self, status: S | None, data: D | None, logs: str | None):
        super().__init__()
        self.status = status
        self.data = data
        self.logs = logs

    def __str__(self):
        return f"{{status={self.status}, data={self.data}}}"


class PIACommandStatus(Enum):
    # PIA CliExitCode Enum
    SUCCESS = "Success"
    INVALID_ARGS = "InvalidArgs"
    TIMEOUT = "Timeout"
    CONNECTION_LOST = "ConnectionLost"
    REQUIRES_CLIENT = "RequiresClient"
    NOT_LOGGED_IN = "NotLoggedIn"
    UNKNOWN_SETTING = "UnknownSetting"
    DEDICATED_IP_TOKEN_EXPIRED = "DedicatedIPTokenExpired"
    DEDICATED_IP_TOKEN_INVALID = "DedicatedIPTokenInvalid"
    OTHER_ERROR = "OtherError"

    # Custom Values
    TEMP_FILE_ERROR = "TempFileError"

    @classmethod
    def from_cli_exit_code(cls, code: int) -> "PIACommandStatus":
        return {
            0: cls.SUCCESS,
            1: cls.INVALID_ARGS,
            2: cls.TIMEOUT,
            3: cls.CONNECTION_LOST,
            4: cls.REQUIRES_CLIENT,
            5: cls.NOT_LOGGED_IN,
            6: cls.UNKNOWN_SETTING,
            7: cls.DEDICATED_IP_TOKEN_EXPIRED,
            8: cls.DEDICATED_IP_TOKEN_INVALID,
        }.get(code, cls.OTHER_ERROR)


class PIAConnectionState(Enum):
    DISCONNECTED = "Disconnected"
    CONNECTING = "Connecting"
    CONNECTED = "Connected"
    INTERRUPTED = "Interrupted"
    RECONNECTING = "Reconnecting"
    DISCONNECTING_TO_RECONNECT = "DisconnectingToReconnect"
    DISCONNECTING = "Disconnecting"
    UNKNOWN = "Unknown"

    @classmethod
    def from_value(cls, value: str) -> "PIAConnectionState":
        return cls._value2member_map_.get(
            value, PIAConnectionState.UNKNOWN
        )  # type: ignore


class PIACredentials:
    def __init__(self, username: str, password: str) -> None:
        self.username: str = username
        self.password: str = password


class PIAInformationType(Enum):
    ALLOW_LAN = "allowlan"
    CONNECTION_STATE = "connectionstate"
    DEBUG_LOGGING = "debuglogging"
    PORT_FORWARD = "portforward"
    PROTOCOL = "protocol"
    PUB_IP = "pubip"
    REGION = "region"
    REGIONS = "regions"
    REQUEST_PORT_FORWARD = "requestportforward"
    VPN_IP = "vpnip"


class PIAPortForwardStatus(Enum):
    INACTIVE = "Inactive"
    ATTEMPTING = "Attempting"
    FAILED = "Failed"
    UNAVAILABLE = "Unavailable"
    UNKNOWN = "Unknown"

    @classmethod
    def from_value(cls, value: str) -> "PIAPortForwardStatus":
        return cls._value2member_map_.get(
            value, PIAPortForwardStatus.UNKNOWN
        )  # type: ignore


class PIAProtocol(Enum):
    OPENVPN = "openvpn"
    WIREGUARD = "wireguard"
    UNKNOWN = "unknown"

    @classmethod
    def from_value(cls, value: str) -> "PIAProtocol":
        return cls._value2member_map_.get(value, PIAProtocol.UNKNOWN)  # type: ignore
