import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from shutil import which
from subprocess import CalledProcessError
from subprocess import run as run_command


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
    advertise_routes: list[str] | None = None
    auto_update: bool = False
    snat_subnet_routes: bool = False
    update_check: bool = False


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
        if isinstance(binary, Path):
            self.binary = binary

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

    def get_config(self) -> TailscaleConfig:
        try:
            result = self.run("get", "--json")
        except CalledProcessError as e:
            raise TailscaleError(
                f"Tailscale get command failed: {e.stderr.strip()}"
            ) from e

        config_data = json.loads(result)
        return TailscaleConfig(
            accept_dns=config_data.get("accept-dns", False),
            accept_routes=config_data.get("accept-routes", False),
            advertise_routes=config_data.get("advertise-routes", []),
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
