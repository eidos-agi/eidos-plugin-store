# Eidos Capability Contract

The Eidos AGI Catalog has two audiences:

- Humans browsing `https://eidosagi.com/plugins`.
- Agents routing work to the smallest specialist stack that can produce proof.

The capability registry is the machine-readable layer for the second audience.
It is public-safe metadata. It must not contain raw secrets, private credentials,
Apple account details, card data, provisioning profile contents, or exact
private machine paths.

## Files

- Schema: `schemas/capability-registry.schema.json`
- Sample registry: `examples/capability-registry.sample.json`
- Validator: `scripts/validate_capability_registry.py`

Validate the sample:

```bash
python3 scripts/validate_capability_registry.py examples/capability-registry.sample.json
```

## Registry Shape

Each plugin entry declares:

- `owns`: the domain the plugin owns, the boundary of that ownership, and what
  it explicitly does not own.
- `commands`: the smallest useful CLI or public catalog entrypoints. These are
  discovery and proof commands, not secret-revealing commands.
- `proof_types`: evidence the plugin can produce or verify.
- `hard_stops`: actions where Eidos must stop, request approval, or route to a
  human.
- `dependencies`: required binaries, plugins, services, or host capabilities.
- `works_with`: graph edges to complementary plugins.
- `eidos_routes`: route rules with the specialist stack Eidos should assemble.
- `install_status`: separate source repo, installed copy, and public catalog
  listing status.
- `quality`: test command, smoke command, docs, and last proof status.

## Boundary Rule

Eidos is the coordinator, not the container. Capability metadata should help
Eidos choose and verify specialist tools; it should not move Foreman, Emux,
StepProof, Converge, Surfari, Knox, Felix, Rhea, or Forge-Forge runtime behavior
into Eidos.

Use this routing test:

- If the field helps Eidos choose an owner, require proof, escalate, close out,
  or learn from a result, it belongs in the capability registry.
- If the field teaches Eidos how to run a specialist's domain runtime internally,
  keep it out of the registry and link to the specialist command instead.

## Public Catalog Integration

The existing machine catalog may expose capability data in either of two ways:

1. Inline `capability` metadata on each plugin row.
2. A public `capability_url` on each plugin row that points to a versioned
   capability document.

The second form is safer for the first publication because it keeps the human
catalog readable and lets maintainers validate capability metadata independently.
Either form must validate against `capability-registry.schema.json` before
publication.

## Source, Installed, Public

Do not collapse these states:

- `install_status.source`: canonical source-of-truth repo.
- `install_status.installed`: whether this host or environment has an installed
  plugin copy. Public output should use `path_kind`, not exact local paths.
- `install_status.public_catalog`: whether the public catalog lists the plugin
  and, later, whether it links to capability metadata.

This distinction is what lets Eidos report drift: a plugin can exist in source,
be missing from the Codex cache, and still be listed publicly, or any other
combination.

## Required First Coverage

The first registry must cover:

- Eidos
- Eidos AGI Catalog
- Foreman
- Emux
- StepProof
- Converge
- Surfari
- Knox / Eidos Vault
- Felix
- Rhea
- Forge-Forge

Additional plugins can be added as their maintainers provide ownership,
commands, proof, dependencies, hard stops, and quality metadata.
