# Flow SDK Test Suite - Simplified Structure

The test suite has been restructured following engineering excellence principles for simplicity and clarity.

## New Structure (70% Simpler)

```
tests/
├── fast/          # Unit tests (<1s execution, mocked dependencies)
├── slow/          # Integration/E2E tests (≥1s, real dependencies)
│   ├── e2e/       # End-to-end workflow tests
│   └── performance/ # Performance benchmarks
└── support/       # All supporting code
    ├── fixtures/  # Test data and mocks
    ├── framework/ # Test base classes and utilities
    ├── scripts/   # Test runners
    └── ...        # Other support files
```

## Key Principles

1. **Speed-Based Organization** - Fast tests run on every commit, slow tests on PR/nightly
2. **Clear Boundaries** - No confusion between test categories
3. **Single Responsibility** - Each directory has ONE clear purpose
4. **No Redundancy** - Eliminated overlapping categories (functional vs integration)

## Running Tests

```bash
# Run all fast tests (unit tests)
pytest tests/fast -v

# Run all slow tests (integration/e2e)
pytest tests/slow -v

# Run specific category
pytest tests/slow/e2e -v
pytest tests/slow/performance -v

# Run with markers (deprecated but still works)
pytest -m "unit"  # Maps to fast tests
pytest -m "integration"  # Maps to slow tests
```

## Migration from Old Structure

- `tests/unit/` → `tests/fast/`
- `tests/smoke/` → `tests/fast/`
- `tests/functional/` → `tests/fast/`
- `tests/integration/` → `tests/slow/`
- `tests/e2e/` → `tests/slow/e2e/`
- `tests/performance/` → `tests/slow/performance/`
- All support directories → `tests/support/`

## Writing New Tests

1. **Fast Tests** (`tests/fast/`)
   - Pure unit tests with mocked dependencies
   - Should complete in <1 second
   - No external service calls
   - No file I/O to real filesystem

2. **Slow Tests** (`tests/slow/`)
   - Integration tests with real components
   - E2E tests with full workflows
   - Performance benchmarks
   - May use test databases/services

## Benefits

- **70% simpler** than previous 10+ directory structure
- **Clear performance expectations** - you know if a test is fast or slow
- **No category confusion** - no more "is this functional or integration?"
- **Follows Google testing practices** - speed-based organization
- **Easy CI/CD integration** - run fast tests on every commit