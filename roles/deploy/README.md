# Role: sapstar.tailscale.tailscale

Installs Tailscale on Debian/Ubuntu systems using the official Tailscale APT repository and manages the `tailscaled` systemd service.

This role does **not** authenticate the host or run `tailscale up`. Use modules such as `sapstar.tailscale.tailscale_set` or future authentication modules for client configuration.

## Requirements

- Debian or Ubuntu target host
- systemd
- Privilege escalation (`become: true`)

## Variables

| Variable | Default | Description |
| --- | --- | --- |
| `tailscale_channel` | `stable` | Tailscale package channel used for the official repository URL. Usually `stable` or `unstable`. |
| `tailscale_manage_apt_repository` | `true` | Whether to configure the official Tailscale APT repository. |
| `tailscale_apt_keyring_path` | `/usr/share/keyrings/tailscale-archive-keyring.gpg` | Destination path for the Tailscale APT keyring. |
| `tailscale_apt_repository_path` | `/etc/apt/sources.list.d/tailscale.list` | Destination path for the generated Tailscale APT source list. |
| `tailscale_package_name` | `tailscale` | Package name to install. |
| `tailscale_package_state` | `present` | Package state passed to `ansible.builtin.apt`. |
| `tailscale_service_name` | `tailscaled` | systemd service name. |
| `tailscale_service_enabled` | `true` | Whether the service should be enabled at boot. |
| `tailscale_service_state` | `started` | Desired service state. |

## Example

```yaml
---
- name: Install Tailscale
  hosts: linux
  become: true
  roles:
    - role: sapstar.tailscale.tailscale
```
