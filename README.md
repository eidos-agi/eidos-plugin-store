# Eidos Plugin Store

The Eidos Plugin Store is the Codex bootstrap plugin for Eidos plugins.

Install or load this plugin first, then ask Codex to use it to find and add the other Eidos plugins you need.

## Paste Into Codex

```text
I want to install the Eidos Plugin Store for Codex so you can use it to find and add more Eidos plugins.

Please bootstrap the Eidos Plugin Store plugin first, then use it as the catalog for other Eidos plugins:
https://eidosagi.com/plugins

Store plugin source:
https://github.com/eidos-agi/eidos-plugin-store

If Codex cannot install plugins directly yet, say that plainly, use the source repo instructions, and keep using the Eidos Plugin Store catalog as the source of truth.
```

## Catalog

- Human catalog: https://eidosagi.com/plugins
- Machine catalog: https://eidosagi.com/plugins.json

## What It Does

- Reads the Eidos Plugin Store catalog.
- Recommends the right Eidos plugin for a task.
- Gives direct install steps when available.
- Falls back to source repo instructions when direct Codex install is not live.

## Status

This is the first Codex bootstrap plugin for the public Eidos Plugin Store.
