"""
WebTransport Constants and Defaults.
"""

from __future__ import annotations

from enum import IntEnum
from typing import TypedDict

from pywebtransport.version import __version__

__all__ = [
    "ClientConfigDefaults",
    "DEFAULT_LOG_FORMAT",
    "DEFAULT_LOG_LEVEL",
    "DEFAULT_WEBTRANSPORT_PATH",
    "Defaults",
    "ErrorCodes",
    "ORIGIN_HEADER",
    "RECOMMENDED_BUFFER_SIZES",
    "SECURE_SCHEMES",
    "SEC_WEBTRANSPORT_HTTP3_DRAFT13",
    "ServerConfigDefaults",
    "USER_AGENT_HEADER",
    "WEBTRANSPORT_HEADER",
    "WEBTRANSPORT_MIME_TYPE",
    "WEBTRANSPORT_SCHEMES",
    "WebTransportConstants",
]

DEFAULT_LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DEFAULT_LOG_LEVEL: str = "INFO"
DEFAULT_WEBTRANSPORT_PATH: str = "/webtransport"
ORIGIN_HEADER: str = "origin"
RECOMMENDED_BUFFER_SIZES: dict[str, int] = {"small": 8192, "medium": 65536, "large": 262144}
SECURE_SCHEMES: tuple[str, str] = ("https", "wss")
SEC_WEBTRANSPORT_HTTP3_DRAFT13: str = "webtransport"
USER_AGENT_HEADER: str = "user-agent"
WEBTRANSPORT_HEADER: str = "webtransport"
WEBTRANSPORT_MIME_TYPE: str = "application/webtransport"
WEBTRANSPORT_SCHEMES: tuple[str, str] = ("https", "wss")


class ErrorCodes(IntEnum):
    """A collection of standard WebTransport and QUIC error codes."""

    NO_ERROR = 0x0
    INTERNAL_ERROR = 0x1
    CONNECTION_REFUSED = 0x2
    FLOW_CONTROL_ERROR = 0x3
    STREAM_LIMIT_ERROR = 0x4
    STREAM_STATE_ERROR = 0x5
    FINAL_SIZE_ERROR = 0x6
    FRAME_ENCODING_ERROR = 0x7
    TRANSPORT_PARAMETER_ERROR = 0x8
    CONNECTION_ID_LIMIT_ERROR = 0x9
    PROTOCOL_VIOLATION = 0xA
    INVALID_TOKEN = 0xB
    APPLICATION_ERROR = 0xC
    CRYPTO_BUFFER_EXCEEDED = 0xD
    KEY_UPDATE_ERROR = 0xE
    AEAD_LIMIT_REACHED = 0xF
    NO_VIABLE_PATH = 0x10
    H3_DATAGRAM_ERROR = 0x33
    H3_NO_ERROR = 0x100
    H3_GENERAL_PROTOCOL_ERROR = 0x101
    H3_INTERNAL_ERROR = 0x102
    H3_STREAM_CREATION_ERROR = 0x103
    H3_CLOSED_CRITICAL_STREAM = 0x104
    H3_FRAME_UNEXPECTED = 0x105
    H3_FRAME_ERROR = 0x106
    H3_EXCESSIVE_LOAD = 0x107
    H3_ID_ERROR = 0x108
    H3_SETTINGS_ERROR = 0x109
    H3_MISSING_SETTINGS = 0x10A
    H3_REQUEST_REJECTED = 0x10B
    H3_REQUEST_CANCELLED = 0x10C
    H3_REQUEST_INCOMPLETE = 0x10D
    H3_MESSAGE_ERROR = 0x10E
    H3_CONNECT_ERROR = 0x10F
    H3_VERSION_FALLBACK = 0x110
    QPACK_DECOMPRESSION_FAILED = 0x200
    QPACK_ENCODER_STREAM_ERROR = 0x201
    QPACK_DECODER_STREAM_ERROR = 0x202
    APP_CONNECTION_TIMEOUT = 0x1000
    APP_AUTHENTICATION_FAILED = 0x1001
    APP_PERMISSION_DENIED = 0x1002
    APP_RESOURCE_EXHAUSTED = 0x1003
    APP_INVALID_REQUEST = 0x1004
    APP_SERVICE_UNAVAILABLE = 0x1005


class WebTransportConstants:
    """A collection of fundamental WebTransport protocol constants."""

    DEFAULT_PORT: int = 80
    DEFAULT_SECURE_PORT: int = 443
    DEFAULT_DEV_PORT: int = 4433

    DRAFT_VERSION: int = 13
    SUPPORTED_VERSIONS: tuple[str, ...] = ("draft-ietf-webtrans-http3-13", "h3")
    DEFAULT_VERSION: str = "h3"

    BIDIRECTIONAL_STREAM: int = 0x0
    UNIDIRECTIONAL_STREAM: int = 0x2
    WEBTRANSPORT_H3_BIDI_STREAM_TYPE: int = 0x41
    WEBTRANSPORT_H3_UNI_STREAM_TYPE: int = 0x54
    CLOSE_WEBTRANSPORT_SESSION_TYPE: int = 0x2843
    DRAIN_WEBTRANSPORT_SESSION_TYPE: int = 0x78AE

    H3_DATA_FRAME_TYPE: int = 0x0
    H3_FRAME_TYPE_HEADERS = 0x01
    H3_FRAME_TYPE_SETTINGS = 0x04
    H3_STREAM_TYPE_CONTROL = 0x00
    H3_STREAM_TYPE_QPACK_ENCODER = 0x02
    H3_STREAM_TYPE_QPACK_DECODER = 0x03

    SETTINGS_QPACK_MAX_TABLE_CAPACITY = 0x1
    SETTINGS_QPACK_BLOCKED_STREAMS = 0x7
    SETTINGS_ENABLE_CONNECT_PROTOCOL = 0x8
    SETTINGS_H3_DATAGRAM = 0x33
    SETTINGS_ENABLE_WEBTRANSPORT = 0x2B603742

    MAX_STREAM_ID: int = 2**62 - 1
    MAX_DATAGRAM_SIZE: int = 65535
    DEFAULT_BUFFER_SIZE: int = 65536
    MAX_BUFFER_SIZE: int = 1024 * 1024
    DEFAULT_MAX_STREAMS: int = 100
    DEFAULT_MAX_INCOMING_STREAMS: int = 100
    DEFAULT_CLIENT_MAX_CONNECTIONS: int = 100
    DEFAULT_SERVER_MAX_CONNECTIONS: int = 3000
    DEFAULT_MAX_STREAMS_PER_CONNECTION: int = 100
    DEFAULT_MAX_SESSIONS: int = 10000

    DEFAULT_CONNECT_TIMEOUT: float = 30.0
    DEFAULT_READ_TIMEOUT: float = 60.0
    DEFAULT_WRITE_TIMEOUT: float = 30.0
    DEFAULT_CLOSE_TIMEOUT: float = 5.0
    DEFAULT_STREAM_CREATION_TIMEOUT: float = 10.0
    DEFAULT_CONNECTION_KEEPALIVE_TIMEOUT: float = 30.0
    DEFAULT_CONNECTION_CLEANUP_INTERVAL: float = 30.0
    DEFAULT_CONNECTION_IDLE_TIMEOUT: float = 60.0
    DEFAULT_CONNECTION_IDLE_CHECK_INTERVAL: float = 5.0
    DEFAULT_SESSION_CLEANUP_INTERVAL: float = 60.0
    DEFAULT_STREAM_CLEANUP_INTERVAL: float = 15.0

    DEFAULT_INITIAL_MAX_DATA: int = 1024 * 1024
    DEFAULT_INITIAL_MAX_STREAM_DATA_BIDI_LOCAL: int = 256 * 1024
    DEFAULT_INITIAL_MAX_STREAM_DATA_BIDI_REMOTE: int = 256 * 1024
    DEFAULT_INITIAL_MAX_STREAM_DATA_UNI: int = 256 * 1024
    DEFAULT_INITIAL_MAX_STREAMS_BIDI: int = 100
    DEFAULT_INITIAL_MAX_STREAMS_UNI: int = 3

    ALPN_H3: str = "h3"
    ALPN_H3_29: str = "h3-29"
    ALPN_H3_32: str = "h3-32"
    DEFAULT_ALPN_PROTOCOLS: tuple[str, str] = (ALPN_H3, ALPN_H3_29)


class ClientConfigDefaults(TypedDict):
    """A type definition for the client configuration dictionary."""

    connect_timeout: float
    read_timeout: float
    write_timeout: float
    close_timeout: float
    stream_creation_timeout: float
    connection_keepalive_timeout: float
    connection_cleanup_interval: float
    connection_idle_timeout: float
    connection_idle_check_interval: float
    stream_cleanup_interval: float
    max_connections: int
    max_streams: int
    max_incoming_streams: int
    stream_buffer_size: int
    alpn_protocols: list[str]
    http_version: str
    verify_mode: None
    check_hostname: bool
    user_agent: str
    keep_alive: bool


class ServerConfigDefaults(TypedDict):
    """A type definition for the server configuration dictionary."""

    bind_host: str
    bind_port: int
    max_connections: int
    max_sessions: int
    max_streams_per_connection: int
    max_incoming_streams: int
    connection_keepalive_timeout: float
    connection_cleanup_interval: float
    connection_idle_timeout: float
    connection_idle_check_interval: float
    session_cleanup_interval: float
    stream_cleanup_interval: float
    read_timeout: float
    write_timeout: float
    alpn_protocols: list[str]
    http_version: str
    backlog: int
    reuse_port: bool
    keep_alive: bool


_DEFAULT_CLIENT_CONFIG: ClientConfigDefaults = {
    "connect_timeout": WebTransportConstants.DEFAULT_CONNECT_TIMEOUT,
    "read_timeout": WebTransportConstants.DEFAULT_READ_TIMEOUT,
    "write_timeout": WebTransportConstants.DEFAULT_WRITE_TIMEOUT,
    "close_timeout": WebTransportConstants.DEFAULT_CLOSE_TIMEOUT,
    "stream_creation_timeout": WebTransportConstants.DEFAULT_STREAM_CREATION_TIMEOUT,
    "connection_keepalive_timeout": WebTransportConstants.DEFAULT_CONNECTION_KEEPALIVE_TIMEOUT,
    "connection_cleanup_interval": WebTransportConstants.DEFAULT_CONNECTION_CLEANUP_INTERVAL,
    "connection_idle_timeout": WebTransportConstants.DEFAULT_CONNECTION_IDLE_TIMEOUT,
    "connection_idle_check_interval": WebTransportConstants.DEFAULT_CONNECTION_IDLE_CHECK_INTERVAL,
    "stream_cleanup_interval": WebTransportConstants.DEFAULT_STREAM_CLEANUP_INTERVAL,
    "max_connections": WebTransportConstants.DEFAULT_CLIENT_MAX_CONNECTIONS,
    "max_streams": WebTransportConstants.DEFAULT_MAX_STREAMS,
    "max_incoming_streams": WebTransportConstants.DEFAULT_MAX_INCOMING_STREAMS,
    "stream_buffer_size": WebTransportConstants.DEFAULT_BUFFER_SIZE,
    "alpn_protocols": list(WebTransportConstants.DEFAULT_ALPN_PROTOCOLS),
    "http_version": "3",
    "verify_mode": None,
    "check_hostname": True,
    "user_agent": f"pywebtransport/{__version__}",
    "keep_alive": True,
}

_DEFAULT_SERVER_CONFIG: ServerConfigDefaults = {
    "bind_host": "localhost",
    "bind_port": WebTransportConstants.DEFAULT_DEV_PORT,
    "max_connections": WebTransportConstants.DEFAULT_SERVER_MAX_CONNECTIONS,
    "max_sessions": WebTransportConstants.DEFAULT_MAX_SESSIONS,
    "max_streams_per_connection": WebTransportConstants.DEFAULT_MAX_STREAMS_PER_CONNECTION,
    "max_incoming_streams": WebTransportConstants.DEFAULT_MAX_INCOMING_STREAMS,
    "connection_keepalive_timeout": WebTransportConstants.DEFAULT_CONNECTION_KEEPALIVE_TIMEOUT,
    "connection_cleanup_interval": WebTransportConstants.DEFAULT_CONNECTION_CLEANUP_INTERVAL,
    "connection_idle_timeout": WebTransportConstants.DEFAULT_CONNECTION_IDLE_TIMEOUT,
    "connection_idle_check_interval": WebTransportConstants.DEFAULT_CONNECTION_IDLE_CHECK_INTERVAL,
    "session_cleanup_interval": WebTransportConstants.DEFAULT_SESSION_CLEANUP_INTERVAL,
    "stream_cleanup_interval": WebTransportConstants.DEFAULT_STREAM_CLEANUP_INTERVAL,
    "read_timeout": WebTransportConstants.DEFAULT_READ_TIMEOUT,
    "write_timeout": WebTransportConstants.DEFAULT_WRITE_TIMEOUT,
    "alpn_protocols": list(WebTransportConstants.DEFAULT_ALPN_PROTOCOLS),
    "http_version": "3",
    "backlog": 128,
    "reuse_port": True,
    "keep_alive": True,
}


class Defaults:
    """Provides access to default configuration values."""

    @staticmethod
    def get_client_config() -> ClientConfigDefaults:
        """Return a copy of the default client configuration."""
        return _DEFAULT_CLIENT_CONFIG.copy()

    @staticmethod
    def get_server_config() -> ServerConfigDefaults:
        """Return a copy of the default server configuration."""
        return _DEFAULT_SERVER_CONFIG.copy()
