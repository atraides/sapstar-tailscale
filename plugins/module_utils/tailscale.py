# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json


def tailscale_binary(module):
    binary_path = module.params.get("binary_path")
    if binary_path:
        return binary_path
    return module.get_bin_path("tailscale", required=True)


def run_tailscale(module, args, check_rc=True):
    binary = tailscale_binary(module)
    command = [binary] + args
    rc, stdout, stderr = module.run_command(command)
    if check_rc and rc != 0:
        module.fail_json(
            msg="tailscale command failed",
            command=sanitize_command(command),
            rc=rc,
            stdout=stdout,
            stderr=stderr,
        )
    return rc, stdout, stderr, command


def run_tailscale_json(module, args, check_rc=True):
    rc, stdout, stderr, command = run_tailscale(module, args, check_rc=check_rc)
    if rc != 0 and not check_rc:
        return rc, None, stderr, command

    try:
        data = json.loads(stdout or "{}")
    except ValueError as exc:
        module.fail_json(
            msg="failed to parse tailscale JSON output",
            command=sanitize_command(command),
            stdout=stdout,
            stderr=stderr,
            error=str(exc),
        )
    return rc, data, stderr, command


def status_json(module, check_rc=True):
    return run_tailscale_json(module, ["status", "--json"], check_rc=check_rc)


def sanitize_command(command):
    sanitized = []
    redact_next = False
    sensitive_flags = {"--authkey", "--auth-key", "--authkey="}

    for item in command:
        if redact_next:
            sanitized.append("VALUE_SPECIFIED_IN_NO_LOG_PARAMETER")
            redact_next = False
            continue

        if item in sensitive_flags:
            sanitized.append(item)
            redact_next = True
            continue

        if item.startswith("--authkey=") or item.startswith("--auth-key="):
            flag = item.split("=", 1)[0]
            sanitized.append(flag + "=VALUE_SPECIFIED_IN_NO_LOG_PARAMETER")
            continue

        sanitized.append(item)

    return sanitized


def bool_flag(name, value):
    if value is None:
        return None
    return "--%s=%s" % (name.replace("_", "-"), str(bool(value)).lower())


def csv_flag(name, value):
    if value is None:
        return None
    return "--%s=%s" % (name.replace("_", "-"), ",".join(value))
