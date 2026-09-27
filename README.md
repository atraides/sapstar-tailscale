# sapstar.tailscale

Ansible collection for installing, inspecting, and configuring Tailscale on Linux systems.

This collection currently provides:

- A `sapstar.tailscale.tailscale` role that installs Tailscale from the official Tailscale APT repository on Debian/Ubuntu systems and manages the `tailscaled` service.
- Python modules for collecting local Tailscale data and applying selected client settings:
  - `sapstar.tailscale.tailscale_status_info`
  - `sapstar.tailscale.tailscale_ip_info`
  - `sapstar.tailscale.tailscale_set`
- Example playbooks under `playbooks/`.

## Requirements

- Ansible Core 2.14 or newer is recommended.
- Target hosts must currently be Debian or Ubuntu.
- The `tailscale` CLI must be installed before using the info/configuration modules. Use the included role for this.
- Configuration modules operate on the local installed Tailscale client and usually require privilege escalation.

## Installation

From a built collection artifact:

```bash
ansible-galaxy collection install sapstar-tailscale-0.1.0.tar.gz
```

From this source tree during development:

```bash
ansible-galaxy collection build
ansible-galaxy collection install sapstar-tailscale-0.1.0.tar.gz --force
```

## Quick start

Install Tailscale and ensure `tailscaled` is running:

```yaml
---
- name: Install Tailscale
  hosts: linux
  become: true
  roles:
    - role: sapstar.tailscale.tailscale
```

Gather status information:

```yaml
---
- name: Gather Tailscale status
  hosts: linux
  become: true
  tasks:
    - name: Read local Tailscale status
      sapstar.tailscale.tailscale_status_info:
      register: tailscale_status

    - name: Show backend state
      ansible.builtin.debug:
        var: tailscale_status.backend_state
```

Apply selected local settings:

```yaml
---
- name: Configure Tailscale settings
  hosts: linux
  become: true
  tasks:
    - name: Enable Tailscale SSH and accept routes
      sapstar.tailscale.tailscale_set:
        ssh: true
        accept_routes: true
```

## Role variables

See [`roles/tailscale/README.md`](roles/tailscale/README.md).

## Example playbooks

- [`playbooks/install.yml`](playbooks/install.yml)
- [`playbooks/gather_info.yml`](playbooks/gather_info.yml)
- [`playbooks/configure_settings.yml`](playbooks/configure_settings.yml)

## Development status

This is an initial skeleton. The role supports Debian/Ubuntu via official repositories. The modules are intentionally small and CLI-backed so they can evolve with real operational requirements.
