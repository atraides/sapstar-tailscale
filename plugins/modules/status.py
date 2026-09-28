#!/usr/bin/python
DOCUMENTATION = r"""
---
module: status

short_description: Retrieve the status of a local Tailscale client

version_added: "0.2.6"

description:
    - Retrieves the current status of the local Tailscale client.
    - The module invokes the Tailscale CLI in JSON mode without collecting peer information.
    - This module is read-only and always returns C(changed) as C(false).

requirements:
    - The Tailscale CLI must be installed on the managed host.

options:
    binary:
        description:
            - Path to the Tailscale executable.
            - If omitted, the module uses the C(tailscale) executable found in the managed host's PATH.
        type: str
        required: false

attributes:
    check_mode:
        description:
            - Can run in check mode and returns the current status without changing the managed host.
        support: full

author:
    - Sapstar
"""

EXAMPLES = r"""
- name: Read the local Tailscale status
  sapstar.tailscale.status:
  register: tailscale_status

- name: Display the Tailscale backend state
  ansible.builtin.debug:
    msg: "Tailscale backend state: {{ tailscale_status.status.backend_state }}"

- name: Read the status using an explicit Tailscale executable
  sapstar.tailscale.status:
    binary: /usr/bin/tailscale
  register: tailscale_status
"""

RETURN = r"""
status:
    description: Status information returned by the local Tailscale client.
    type: dict
    returned: always
    contains:
        version:
            description: Version of the local Tailscale client.
            type: str
            returned: always
            sample: 1.82.5
        backend_state:
            description:
                - Current state of the Tailscale backend.
                - Common values include C(NoState), C(NeedsLogin), C(Stopped), and C(Running).
            type: str
            returned: always
            sample: Running
        health:
            description: Health warnings reported by the Tailscale client.
            type: list
            elements: str
            returned: always
            sample: []
        self_node:
            description: Information about the local Tailscale node.
            type: dict
            returned: always
            contains:
                id:
                    description: Identifier of the local Tailscale node, when available.
                    type: str
                    returned: always
                    sample: null
                hostname:
                    description: Hostname advertised by the local Tailscale node.
                    type: str
                    returned: always
                    sample: workstation
                online:
                    description: Whether the local Tailscale node is online.
                    type: bool
                    returned: always
                    sample: true
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.sapstar.tailscale.plugins.module_utils.utils import (
    TailscaleError,
    TailscaleInstance,
)


def run_module():
    module_args = {"binary": {"type": "str", "required": False}}
    result = {"changed": False, "status": None, "config": None}

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)
    tailscale = TailscaleInstance()

    try:
        status = tailscale.get_status()
        result["status"] = {
            "version": status.version,
            "backend_state": status.backend_state.name,
            "health": status.health,
            "self_node": status.self_node.__dict__ if status.self_node else None,
        }
        config = tailscale.get_config()
        result["config"] = {
            "accept_dns": config.accept_dns,
            "accept_routes": config.accept_routes,
            "advertise_routes": config.advertise_routes,
            "auto_update": config.auto_update,
            "snat_subnet_routes": config.snat_subnet_routes,
            "update_check": config.update_check,
        }
    except TailscaleError:
        module.fail_json(msg="Something wrong happened", **result)

    if module.check_mode:
        module.exit_json(**result)

    module.exit_json(**result)


def main():
    run_module()


if __name__ == "__main__":
    main()
