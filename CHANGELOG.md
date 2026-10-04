## v0.6.3 (2026-10-04)

### Fix

- **config**: Make sure the advertised route list is sorted the same way as Tailscale's

## v0.6.2 (2026-10-02)

### Fix

- **enroll**: Skip configuration when the machine is not enrolled

## v0.6.1 (2026-10-02)

### Fix

- **config**: Add privilege escalation for the appropriate configuration steps

## v0.6.0 (2026-10-02)

### Feat

- **config**: Separate the configuration task from the main tasks to it's own space
- **config**: Separate validation from the main task and add sensible validation before configuration

### Fix

- **config**: Fix incorrect parameter name to follow the standard

## v0.5.0 (2026-10-01)

### Feat

- **config**: apply requested Tailscale settings
- **config**: add Tailscale config module

## v0.4.0 (2026-10-01)

### Feat

- **enroll**: Add tasks necessary to enroll the machine if an auth_key present
- **install**: Separate the install task from repository management
- **enroll**: Add support for machine enrollment

### Fix

- **enroll**: Fix incorrect variable name for enrollment output
- **apt**: Streamline variable names to better match intent

## v0.3.0 (2026-09-28)

### Feat

- **config**: Allow gathering the current configuration for Tailscale
- **dev**: Add pyright configuration to detect local Ansible modules
- **status**: Add status ansible module to allow querying tailscale status
- **status**: Add initial utilities to work with the tailscale binary

### Fix

- **git**: Remove pyright configuration from gitignore
- **git**: Update gitignore to include python files and directories

## v0.2.6 (2026-09-27)

### Fix

- **deploy**: Revert the addition of raspbian repository

## v0.2.5 (2026-09-27)

### Fix

- **deploy**: Fix incorrect version pinning

## v0.2.4 (2026-09-27)

### Fix

- **deploy**: Incorrect package base variable
- **deploy**: Add support back to raspbian detection

## v0.2.3 (2026-09-27)

### Fix

- **deploy**: Replace incorrect variables and add apt update handler

## v0.2.2 (2026-09-27)

### Fix

- **deploy**: Update incorrect variable names to use the new standard
- **deploy**: Add missing package list to all supported OS

## v0.2.1 (2026-09-27)

### Fix

- **core**: Cleanup features which will not be implement initially

## v0.2.0 (2026-09-27)

### Feat

- **core**: Initial commit

### Fix

- **cz**: Disable signed commits to work with the GH release workflow
