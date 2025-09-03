# Provider Template Overrides

This directory contains provider-specific template overrides for Mithril.

- Canonical templates live under `flow/resources/templates/runtime/sections`.
- Only add files here when an override is required. If a file is identical to
  the canonical template, prefer removing it to avoid duplication.

Template resolution order is provider-first via `TemplateLoader`, then
canonical resources. This keeps customizations local while avoiding drift.

