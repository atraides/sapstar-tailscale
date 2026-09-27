#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r'''
---
module: tailscale_status_info
short_description: Gather Tailscale status from a local client
description:
  - Runs C(tailscale status --json) on the target host and returns the parsed data.
  - The Tailscale CLI must already be installed.
options:
  binary_path:
    description:
      - Optional absolute path to the C(tailscale) binary.
    type: path
author:
  - Sapstar
'''

EXAMPLES = r'''
- name: Gather Tailscale status
  sapstar.tailscale.tailscale_status_info:
  register: tailscale_status

- name: Show local backend state
  ansible.builtin.debug:
    var: tailscale_status.backend_state
'''

RETURN = r'''
status:
  description: Raw parsed output from C(tailscale status --json).
  returned: always
  type: dict
backend_state:
  description: Local Tailscale backend state.
  returned: always
  type: str
self:
  description: Local node information from the status payload.
  returned: always
  type: dict
peers:
  description: Peer map from the status payload.
  returned: always
  type: dict
command:
  description: Command executed by the module.
  returned: always
  type: list
  elements: str
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.sapstar.tailscale.plugins.module_utils.tailscale import status_json, sanitize_command


def main():
    module = AnsibleModule(
        argument_spec=dict(
            binary_path=dict(type="path"),
        ),
        supports_check_mode=True,
    )

    rc, status, stderr, command = status_json(module)
    module.exit_json(
        changed=False,
        status=status,
        backend_state=status.get("BackendState"),
        self=status.get("Self", {}),
        peers=status.get("Peer", {}),
        command=sanitize_command(command),
    )


if __name__ == "__main__":
    main()
