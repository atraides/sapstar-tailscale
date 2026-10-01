#!/usr/bin/python
DOCUMENTATION = r"""
---
module: config

short_description: Configure selected local Tailscale client settings

description:
    - Applies only settings explicitly supplied to the module.
    - Omitted settings are left unchanged.
    - The module invokes C(tailscale set) only when a requested setting differs
      from the local client configuration.

requirements:
    - The Tailscale CLI must be installed on the managed host.

options:
    accept_dns:
        description: Whether to accept DNS configuration from Tailscale.
        type: bool
    accept_routes:
        description: Whether to accept subnet routes advertised by other nodes.
        type: bool
    advertise-routes:
        description: Subnet routes to advertise as a comma-separated Tailscale setting.
        type: list
        elements: str
    auto_update:
        description: Whether the Tailscale client should update automatically.
        type: bool
    snat_subnet_routes:
        description: Whether advertised subnet routes use source NAT.
        type: bool
    update_check:
        description: Whether the Tailscale client checks for updates.
        type: bool

attributes:
    check_mode:
        description: Calculates configuration changes without applying them.
        support: full
"""

EXAMPLES = r"""
- name: Configure only DNS and route acceptance
  sapstar.tailscale.config:
    accept_dns: true
    accept_routes: true

- name: Clear advertised subnet routes without changing other settings
  sapstar.tailscale.config:
    advertise-routes: []
"""

RETURN = r"""
config:
    description: Local Tailscale configuration after applying changes.
    type: dict
    returned: always
config_diff:
    description: Explicitly requested settings that differ from local configuration.
    type: dict
    returned: always
"""

from typing import Any, cast

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.sapstar.tailscale.plugins.module_utils.utils import (
    TailscaleError,
    TailscaleInstance,
)


def run_module():
    module_args = {
        "accept_dns": {"type": "bool", "required": False},
        "accept_routes": {"type": "bool", "required": False},
        "advertise-routes": {"type": "list", "elements": "str", "required": False},
        "auto_update": {"type": "bool", "required": False},
        "snat_subnet_routes": {"type": "bool", "required": False},
        "update_check": {"type": "bool", "required": False},
    }
    result = {"changed": False, "config": None, "config_diff": {}, "params": {}}

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    try:
        tailscale = TailscaleInstance()
        params = cast(dict[str, Any], module.params)
        result["params"] = {
            key: value for key, value in params.items() if value is not None
        }
        result["config"] = tailscale.get_config_dict()
        result["config_diff"] = tailscale.get_config_diff(params)
        result["changed"] = bool(result["config_diff"])

        if module.check_mode or not result["changed"]:
            module.exit_json(**result)

        tailscale.set_config(params)
        result["config"] = tailscale.get_config_dict()
    except TailscaleError as e:
        module.fail_json(msg="Cannot configure Tailscale: " + str(e), **result)

    module.exit_json(**result)


def main():
    run_module()


if __name__ == "__main__":
    main()
