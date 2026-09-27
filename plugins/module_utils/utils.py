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
    id: str | None = None
    hostname: str | None = None
    online: bool = False


@dataclass
class TailscaleStatus:
    version: str | None = None
    backend_state: BackendState = BackendState.NoState
    health: list[str] | None = None
    self_node: TailscaleNode | None = None


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
