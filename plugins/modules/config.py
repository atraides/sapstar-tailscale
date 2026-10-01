#!/usr/bin/python
DOCUMENTATION = r"""
---
module: config
"""

EXAMPLES = r"""
"""

RETURN = r"""
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.sapstar.tailscale.plugins.module_utils.utils import (
    TailscaleError,
    TailscaleInstance,
)


def run_module():
    module_args = {
        "accept_dns": {"type": "bool", "required": False, "default": False},
        "accept_routes": {"type": "bool", "required": False, "default": False},
        "advertise-routes": {"type": "list", "required": False, "default": []},
        "auto_update": {"type": "bool", "required": False, "default": False},
        "snat_subnet_routes": {"type": "bool", "required": False, "default": False},
        "update_check": {"type": "bool", "required": False, "default": False},
    }
    result = {"changed": False, "update_result": None}

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    if module.check_mode:
        module.exit_json(**result)

    try:
        tailscale = TailscaleInstance()
        params = module.params
        config = tailscale.get_config_dict()
        config_diff = tailscale.get_config_diff(module.params)
        result_dict = {
            "params": params,
            "config": config,
            "config_diff": config_diff,
        }
        module.exit_json(**result_dict)
        result["changed"] = True
    except TailscaleError as e:
        module.fail_json(msg="Cannot enroll machine to Tailscale: " + str(e), **result)

    module.exit_json(**result)


def main():
    run_module()


if __name__ == "__main__":
    main()
