#!/usr/bin/python
DOCUMENTATION = r"""
---
module: enroll
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
        "authkey": {"type": "str", "required": True, "no_log": True}
    }
    result = {"changed": False, "enroll_result": None}

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    if module.check_mode:
        module.exit_json(**result)

    tailscale = TailscaleInstance()

    try:
        enroll_result = tailscale.enroll_machine(module.params["authkey"])
        result["changed"] = True
        result["enroll_result"] = enroll_result
    except TailscaleError as e:
        module.fail_json(msg="Cannot enroll machine to Tailscale: " + str(e), **result)

    module.exit_json(**result)


def main():
    run_module()


if __name__ == "__main__":
    main()
