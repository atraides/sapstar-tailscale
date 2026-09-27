#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r'''
---
module: tailscale_ip_info
short_description: Gather Tailscale IP addresses from a local client
description:
  - Runs C(tailscale ip) on the target host and returns assigned Tailscale IP addresses.
  - The Tailscale CLI must already be installed and the node should be authenticated.
options:
  ipv4:
    description:
      - Gather IPv4 addresses with C(tailscale ip -4).
    type: bool
    default: true
  ipv6:
    description:
      - Gather IPv6 addresses with C(tailscale ip -6).
    type: bool
    default: true
  binary_path:
    description:
      - Optional absolute path to the C(tailscale) binary.
    type: path
author:
  - Sapstar
'''

EXAMPLES = r'''
- name: Gather Tailscale IP addresses
  sapstar.tailscale.tailscale_ip_info:
  register: tailscale_ips

- name: Show Tailscale IPv4 addresses
  ansible.builtin.debug:
    var: tailscale_ips.ipv4_addresses
'''

RETURN = r'''
ipv4_addresses:
  description: Tailscale IPv4 addresses assigned to the local node.
  returned: always
  type: list
  elements: str
ipv6_addresses:
  description: Tailscale IPv6 addresses assigned to the local node.
  returned: always
  type: list
  elements: str
addresses:
  description: Combined list of Tailscale IP addresses requested by the module invocation.
  returned: always
  type: list
  elements: str
commands:
  description: Commands executed by the module.
  returned: always
  type: list
  elements: list
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.sapstar.tailscale.plugins.module_utils.tailscale import run_tailscale, sanitize_command


def lines(stdout):
    return [line.strip() for line in stdout.splitlines() if line.strip()]


def main():
    module = AnsibleModule(
        argument_spec=dict(
            ipv4=dict(type="bool", default=True),
            ipv6=dict(type="bool", default=True),
            binary_path=dict(type="path"),
        ),
        supports_check_mode=True,
    )

    ipv4_addresses = []
    ipv6_addresses = []
    commands = []

    if module.params["ipv4"]:
        rc, stdout, stderr, command = run_tailscale(module, ["ip", "-4"])
        ipv4_addresses = lines(stdout)
        commands.append(sanitize_command(command))

    if module.params["ipv6"]:
        rc, stdout, stderr, command = run_tailscale(module, ["ip", "-6"])
        ipv6_addresses = lines(stdout)
        commands.append(sanitize_command(command))

    module.exit_json(
        changed=False,
        ipv4_addresses=ipv4_addresses,
        ipv6_addresses=ipv6_addresses,
        addresses=ipv4_addresses + ipv6_addresses,
        commands=commands,
    )


if __name__ == "__main__":
    main()
