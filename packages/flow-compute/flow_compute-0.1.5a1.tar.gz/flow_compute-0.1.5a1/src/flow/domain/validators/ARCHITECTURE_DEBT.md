# Architecture Debt in Domain Validators

## Issue
The `instance_validator.py` file currently imports types from the Mithril adapter, which violates hexagonal architecture principles. The domain layer should not depend on adapters.

## Current Violations
- Imports `AuctionModel`, `GPUModel`, `InstanceTypeModel`, etc. from `flow.adapters.providers.builtin.mithril.api.types`

## Required Refactoring
1. Create domain models for these types in `src/flow/domain/models/`
2. Create a protocol/interface for instance validation that adapters can implement
3. Move provider-specific validation logic to the respective adapters
4. Update the domain validator to use dependency injection for provider-specific validation

## Impact
- Medium priority: The current design works but creates coupling
- Should be addressed in a future PR focused on domain model consolidation

## Temporary Workaround
The imports are documented with comments explaining the architectural violation.