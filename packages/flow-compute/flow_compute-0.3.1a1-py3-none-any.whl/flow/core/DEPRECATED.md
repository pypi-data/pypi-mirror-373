# DEPRECATED: core Directory

This directory is **DEPRECATED** and will be removed in v2.0.

## Migration Guide

All modules in this directory have been moved to new locations as part of the hexagonal architecture refactoring:

- `core/http/` → `flow.adapters.http/`
- `core/ssh_*` → `flow.adapters.transport/`
- `core/services/` → `flow.app/`
- `core/provider_interfaces` → `flow.protocols.provider`
- `core/storage` → `flow.protocols.storage`
- `core/data/` → `flow.domain/`

## Compatibility

The previous `flow.compat/` shims have been removed. Please update any legacy
imports to the new canonical modules (e.g. `flow.adapters.*`, `flow.application.*`,
`flow.protocols.*`, `flow.domain.*`). Importing `flow.compat` is no longer supported.

## Timeline

- v1.x: Deprecation warnings issued
- v2.0: Directory will be removed

Please update your imports to use the new locations.
