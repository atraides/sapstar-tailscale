import json
from dataclasses import dataclass, field, fields, is_dataclass
from enum import Enum
from pathlib import Path
from shutil import which
from subprocess import CalledProcessError
from subprocess import run as run_command
from typing import Any


class TailscaleError(Exception):
    """Base class for Tailscale errors."""


class BackendState(Enum):
    NoState = 0
    InUseOtherUser = 1
    NeedsLogin = 2
    NeedsMachineAuth = 3
    Stopped = 4
    Starting = 5
    Running = 6


@dataclass
class TailscaleNode:
    hostname: str | None = None
    online: bool = False


@dataclass
class TailscaleStatus:
    version: str | None = None
    backend_state: BackendState = BackendState.NoState
    health: list[str] | None = None
    self_node: TailscaleNode | None = None


@dataclass
class TailscaleConfig:
    accept_dns: bool = False
    accept_routes: bool = False
    advertise_routes: list[str] = field(default_factory=list)
    auto_update: bool = False
    snat_subnet_routes: bool = False
    update_check: bool = False


def as_result_data(value: Any) -> Any:
    """Convert dataclass models into Ansible/JSON-friendly result data."""
    if is_dataclass(value) and not isinstance(value, type):
        return {
            dataclass_field.name: as_result_data(getattr(value, dataclass_field.name))
            for dataclass_field in fields(value)
        }

    if isinstance(value, Enum):
        return value.name

    if isinstance(value, list):
        return [as_result_data(item) for item in value]

    if isinstance(value, tuple):
        return [as_result_data(item) for item in value]

    if isinstance(value, dict):
        return {key: as_result_data(item) for key, item in value.items()}

    return value


def get_tailscale_binary() -> Path:
    """Get the path to the Tailscale system binary."""
    tailscale_binary = which("tailscale")
    if tailscale_binary is None:
        raise TailscaleError("Tailscale binary not found in PATH")
    return Path(tailscale_binary)


class TailscaleInstance:
    """Represents a Tailscale instance."""

    def __init__(self, binary: Path | None = None):
        self.binary = get_tailscale_binary()  # Default to the system binary
        self._config = TailscaleConfig()

        if isinstance(binary, Path):
            self.binary = binary
        self.update_config()

    @property
    def config(self) -> TailscaleConfig:
        return self._config

    def get_config_dict(self) -> dict[str, Any]:
        return as_result_data(self.config)

    def get_config_diff(self, desired_config: dict[str, Any]) -> dict[str, Any]:
        """Return desired config values that differ from the current config."""
        current_config = as_result_data(self.config)
        normalized_config = {
            key.replace("-", "_"): value
            for key, value in desired_config.items()
            if value is not None
        }

        return {
            key: value
            for key, value in normalized_config.items()
            if key in current_config and current_config[key] != value
        }

    def set_config(self, desired_config: dict[str, Any]) -> dict[str, Any]:
        """Apply only explicitly requested settings that differ from the current state."""
        config_diff = self.get_config_diff(desired_config)
        if not config_diff:
            return config_diff

        args = ["set"]
        for key, value in config_diff.items():
            option = key.replace("_", "-")
            if isinstance(value, bool):
                value = str(value).lower()
            elif isinstance(value, list):
                value = ",".join(value)
            args.append(f"--{option}={value}")

        self.run(*args)
        self.update_config()
        return config_diff

    def run(self, *args: str) -> str:
        """Run the Tailscale command with the given arguments."""
        try:
            result = run_command(
                [str(self.binary), *args], capture_output=True, text=True, check=True
            )
        except CalledProcessError as e:
            raise TailscaleError(f"Tailscale command failed: {e.stderr.strip()}") from e
        return result.stdout.strip()

    def get_status(self) -> TailscaleStatus:
        """Get the status of the Tailscale instance."""
        try:
            result = self.run("status", "--json", "--peers=false")
        except CalledProcessError as e:
            raise TailscaleError(
                f"Tailscale status command failed: {e.stderr.strip()}"
            ) from e

        status_data = json.loads(result)
        backend_state = BackendState[status_data.get("BackendState", "NoState")]
        health = status_data.get("Health", [])
        self_node_data = status_data.get("Self", {})
        self_node = TailscaleNode(
            hostname=self_node_data.get("HostName"),
            online=self_node_data.get("Online", False),
        )
        return TailscaleStatus(
            version=status_data.get("Version"),
            backend_state=backend_state,
            health=health,
            self_node=self_node,
        )

    def update_config(self, force: bool = False) -> None:
        try:
            result = self.run("get", "--json")
        except CalledProcessError as e:
            raise TailscaleError(
                f"Tailscale get command failed: {e.stderr.strip()}"
            ) from e

        config_data = json.loads(result)
        advertise_routes = config_data.get("advertise-routes", "")
        self._config = TailscaleConfig(
            accept_dns=config_data.get("accept-dns", False),
            accept_routes=config_data.get("accept-routes", False),
            advertise_routes=advertise_routes.split(",") if advertise_routes else [],
            auto_update=config_data.get("auto-update", False),
            snat_subnet_routes=config_data.get("snat-subnet-routes", False),
            update_check=config_data.get("update-check", False),
        )

    def enroll_machine(self, auth_key: str) -> dict[str, list[object] | list[str]]:
        """Enroll the machine with the given auth key."""
        # `tailscale up --json` writes one JSON object for each state change.
        # In particular, it can write a NeedsMachineAuth object followed by a
        # Running object. It can also append human-readable warnings, so the
        # output is a mixed stream rather than one JSON document suitable for
        # json.loads().
        result = self.run("up", f"--auth-key={auth_key}", "--json")
        decoder = json.JSONDecoder()
        json_results: list[object] = []
        plain_results: list[str] = []
        offset = 0

        while offset < len(result):
            while offset < len(result) and result[offset].isspace():
                offset += 1
            if offset == len(result):
                break

            try:
                document, next_offset = decoder.raw_decode(result, offset)
            except json.JSONDecodeError:
                # Tailscale may write a human-readable warning to stdout even
                # when --json was requested. Keep that output instead of
                # treating it as a module failure.
                line_end = result.find("\n", offset)
                if line_end == -1:
                    line_end = len(result)
                plain_result = result[offset:line_end].strip()
                if plain_result:
                    plain_results.append(plain_result)
                offset = line_end + 1
                continue

            json_results.append(document)
            offset = next_offset

        return {"json_results": json_results, "plain_results": plain_results}
