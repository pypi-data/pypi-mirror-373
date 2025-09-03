#!/usr/bin/env python3
# pyright: strict

from collections.abc import Mapping
from pathlib import Path
from typing import Any, Iterator, List, Literal, Optional, overload


class AnantaHost(Mapping[str, Any]):
    """Represents an Ananta host entry.

    This class stores the configuration details for connecting to a host
    via SSH, intended for use with the Ananta system.

    The expected format for representing a host is a comma-separated string:
    alias,ip,port,username,key_path[,tags]

    Where:
        - alias: A short name or identifier for the host.
        - ip: The IP address or hostname of the host.
        - port: The SSH port number (defaults to 22 if empty or omitted).
        - username: The username for SSH login (defaults to 'root' if empty or omitted).
        - key_path: The path to the SSH private key file. Use '#' if not applicable or managed elsewhere.
        - tags (optional): Colon-separated tags for categorization (e.g., 'web', 'db', 'arch:web').

    Examples:
        - host-1,10.0.0.1,22,user,/home/user/.ssh/id_ed25519
        - host-2,10.0.0.2,22,user,#,web
        - host-3,10.0.0.3,22,user,#,arch:web
        - host-4,10.0.0.4,22,user,#,ubuntu:db
    """

    alias: str
    ip: str
    port: int
    username: str
    key_path: str
    tags: List[str]

    def __init__(
        self,
        alias: str,
        ip: str,
        port: str,
        username: str,
        key_path: str,
        tags: List[str],
        relocate: Optional[Path],
    ):
        if not alias:
            raise ValueError("ERROR: alias cannot be empty.")
        self.alias = alias

        if not ip:
            raise ValueError("ERROR: ip cannot be empty.")
        self.ip = ip

        try:
            self.port = int(port) if port else 22
            if not (0 < self.port < 65536):
                raise ValueError(
                    f"ERROR: Port number {port} must be greater than 0 and less than 65536."
                )
        except (ValueError, TypeError) as e:
            raise ValueError(f"ERROR: Invalid port number: {port}.") from e

        self.username = username or "root"

        self.key_path = key_path or "#"
        if key_path and relocate:
            key_path_obj = relocate / Path(key_path).name
            if not key_path_obj.is_file():
                raise FileNotFoundError(
                    f"ERROR: SSH Key {key_path_obj} could not be found OR it is not a regular file."
                )
            self.key_path = str(key_path_obj)

        self.tags = tags

        self._data = {
            "alias": self.alias,
            "ip": self.ip,
            "port": self.port,
            "username": self.username,
            "key_path": self.key_path,
            "tags": self.tags,
        }

    @overload
    def __getitem__(self, key: Literal["alias"]) -> str: ...

    @overload
    def __getitem__(self, key: Literal["ip"]) -> str: ...

    @overload
    def __getitem__(self, key: Literal["port"]) -> int: ...

    @overload
    def __getitem__(self, key: Literal["username"]) -> str: ...

    @overload
    def __getitem__(self, key: Literal["key_path"]) -> str: ...

    @overload
    def __getitem__(self, key: Literal["tags"]) -> List[str]: ...

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def dump_comma_separated_str(self) -> str:
        parts = [
            self.alias,
            self.ip,
            str(self.port),
            self.username,
            self.key_path,
        ]
        if self.tags:
            parts.append(":".join(self.tags))
        return ",".join(parts) + "\n"

    def dump_host_info(self) -> Mapping[str, Any]:
        host_info = {k: v for k, v in self._data.items() if k != "alias" and v}
        return host_info
