# Initial design notes

## Collection identity

- Namespace: `sapstar`
- Collection: `tailscale`
- Primary role: `tailscale`

## Initial scope

- Supported platforms: Debian and Ubuntu
- Install method: official Tailscale APT repositories
- Role responsibilities:
  - Install Tailscale package
  - Enable/start `tailscaled`
- Module responsibilities:
  - Gather status data from installed clients
  - Gather assigned Tailscale IP addresses
  - Apply selected client settings through `tailscale set`

## Out of scope for the first skeleton

- Non-Debian package managers
- Authentication/login workflow with auth keys or OAuth clients
- Tailnet API management
- ACL or DNS management through the hosted Tailscale API

These can be added later as separate roles/modules once desired operating patterns are confirmed.
