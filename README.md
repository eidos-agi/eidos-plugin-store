# Eidos AGI Catalog Bootstrap

This repo contains the Codex bootstrap/catalog plugin for Eidos AGI plugins.

The public marketplace identity is **Eidos AGI**. This plugin is an entry inside
that marketplace, not a second store. Install or load it when Codex needs help
discovering the right Eidos AGI plugin for a task.

## Paste Into Codex

```text
I want to install the Eidos AGI plugin catalog for Codex so you can use it to find and add more Eidos plugins.

Please use the Eidos AGI marketplace as the single source of truth for Eidos plugins:
https://eidosagi.com/plugins

Store plugin source:
https://github.com/eidos-agi/eidos-plugin-store

If Codex cannot install plugins directly yet, say that plainly, use the source repo instructions, and keep using the Eidos AGI catalog as the source of truth.
```

## Catalog

- Human catalog: https://eidosagi.com/plugins
- Machine catalog: https://eidosagi.com/.well-known/eidos/plugin-store.json

## Capability Registry

Eidos routes work from a public-safe capability contract, not from human catalog
copy alone. The first local contract lives here:

- Contract docs: `docs/capability-contract.md`
- JSON Schema: `schemas/capability-registry.schema.json`
- Sample registry: `examples/capability-registry.sample.json`
- Validator: `scripts/validate_capability_registry.py`

Validate it before publishing or wiring the public catalog:

```bash
python3 scripts/validate_capability_registry.py examples/capability-registry.sample.json
```

## What It Does

- Reads the Eidos AGI plugin catalog.
- Reads public-safe capability metadata when present.
- Recommends the right Eidos plugin for a task.
- Gives direct install steps when available.
- Falls back to source repo instructions when direct Codex install is not live.

## Status

This is the Codex bootstrap/catalog plugin for the public Eidos AGI marketplace.
