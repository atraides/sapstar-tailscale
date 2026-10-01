# Role: sapstar.tailscale.deploy

Installs Tailscale on Debian/Ubuntu systems using the official Tailscale APT repository and manages the `tailscaled` systemd service.

This role does **not** authenticate the host or run `tailscale up`. Use modules such as `sapstar.tailscale.tailscale_set` or future authentication modules for client configuration.

## Requirements

- Debian or Ubuntu target host
- systemd
- Privilege escalation (`become: true`)

## Variables

| Variable | Default | Description |
| --- | --- | --- |
| `deploy_package_version` | `null` | Optional Tailscale package version to install. |
| `deploy_raspbian` | `false` | Whether Raspbian-specific deployment behavior is enabled. |
| `deploy_channel` | `stable` | Tailscale package channel used for the official repository URL. Usually `stable` or `unstable`. |
| `deploy_package_base` | `https://pkgs.tailscale.com` | Base URL for the Tailscale package repositories. |
| `deploy_repository_url` | Derived from `deploy_package_base`, `deploy_channel`, and the distribution | URL of the distribution-specific Tailscale APT repository. |
| `deploy_aptkey_url` | Derived from `deploy_repository_url` and the distribution release | URL of the repository signing key. |

## Example

```yaml
---
- name: Install Tailscale
  hosts: linux
  become: true
  roles:
    - role: sapstar.tailscale.deploy
```
