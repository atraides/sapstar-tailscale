#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r'''
---
module: tailscale_set
short_description: Apply local Tailscale client settings
description:
  - Runs C(tailscale set) with selected settings on the target host.
  - This module is intended for already installed and authenticated clients.
  - The current Tailscale CLI does not expose every setting in stable machine-readable status output, so this module reports changed when it executes C(tailscale set).
options:
  hostname:
    description:
      - Hostname to advertise for this Tailscale node.
    type: str
  accept_dns:
    description:
      - Whether to accept DNS configuration from the tailnet.
    type: bool
  accept_routes:
    description:
      - Whether to accept subnet routes advertised by other nodes.
    type: bool
  advertise_routes:
    description:
      - Subnet routes to advertise from this node.
    type: list
    elements: str
  advertise_tags:
    description:
      - Tailscale ACL tags to advertise for this node.
    type: list
    elements: str
  ssh:
    description:
      - Whether to enable Tailscale SSH.
    type: bool
  operator:
    description:
      - Local UNIX user allowed to operate the Tailscale CLI without sudo.
    type: str
  shields_up:
    description:
      - Whether to block incoming connections from other Tailscale nodes.
    type: bool
  force:
    description:
      - Execute C(tailscale set) even if only settings with partially detectable current state are supplied.
    type: bool
    default: false
  binary_path:
    description:
      - Optional absolute path to the C(tailscale) binary.
    type: path
author:
  - Sapstar
'''

EXAMPLES = r'''
- name: Enable Tailscale SSH and accept routes
  sapstar.tailscale.tailscale_set:
    ssh: true
    accept_routes: true

- name: Advertise subnet routes and tags
  sapstar.tailscale.tailscale_set:
    advertise_routes:
      - 10.10.0.0/16
    advertise_tags:
      - tag:server
'''

RETURN = r'''
command:
  description: Command executed or that would be executed in check mode.
  returned: always
  type: list
  elements: str
stdout:
  description: Standard output from C(tailscale set).
  returned: when executed
  type: str
stderr:
  description: Standard error from C(tailscale set).
  returned: when executed
  type: str
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.sapstar.tailscale.plugins.module_utils.tailscale import (
    bool_flag,
    csv_flag,
    run_tailscale,
    sanitize_command,
    status_json,
)


def build_args(params):
    args = ["set"]

    if params.get("hostname") is not None:
        args.append("--hostname=%s" % params["hostname"])

    for name in ["accept_dns", "accept_routes", "ssh", "shields_up"]:
        flag = bool_flag(name, params.get(name))
        if flag:
            args.append(flag)

    for name in ["advertise_routes", "advertise_tags"]:
        flag = csv_flag(name, params.get(name))
        if flag:
            args.append(flag)

    if params.get("operator") is not None:
        args.append("--operator=%s" % params["operator"])

    return args


def detectable_changes(module, args):
    rc, status, stderr, command = status_json(module, check_rc=False)
    if rc != 0 or not status:
        return True

    self_status = status.get("Self") or {}

    desired_hostname = module.params.get("hostname")
    if desired_hostname is not None and self_status.get("HostName") != desired_hostname:
        return True

    desired_tags = module.params.get("advertise_tags")
    if desired_tags is not None:
        current_tags = self_status.get("Tags") or []
        if sorted(current_tags) != sorted(desired_tags):
            return True

    partially_detectable_options = [
        "accept_dns",
        "accept_routes",
        "advertise_routes",
        "ssh",
        "operator",
        "shields_up",
    ]
    for name in partially_detectable_options:
        if module.params.get(name) is not None:
            return True

    return False


def main():
    module = AnsibleModule(
        argument_spec=dict(
            hostname=dict(type="str"),
            accept_dns=dict(type="bool"),
            accept_routes=dict(type="bool"),
            advertise_routes=dict(type="list", elements="str"),
            advertise_tags=dict(type="list", elements="str"),
            ssh=dict(type="bool"),
            operator=dict(type="str"),
            shields_up=dict(type="bool"),
            force=dict(type="bool", default=False),
            binary_path=dict(type="path"),
        ),
        supports_check_mode=True,
    )

    args = build_args(module.params)
    if len(args) == 1:
        module.exit_json(changed=False, command=[])

    changed = module.params["force"] or detectable_changes(module, args)

    if module.check_mode:
        module.exit_json(changed=changed, command=sanitize_command([module.params.get("binary_path") or "tailscale"] + args))

    if not changed:
        module.exit_json(changed=False, command=[])

    rc, stdout, stderr, command = run_tailscale(module, args)
    module.exit_json(
        changed=True,
        command=sanitize_command(command),
        stdout=stdout,
        stderr=stderr,
    )


if __name__ == "__main__":
    main()
