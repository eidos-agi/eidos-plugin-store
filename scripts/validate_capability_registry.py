#!/usr/bin/env python3
"""Validate an Eidos capability registry sample without external dependencies."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

REQUIRED_TOP_LEVEL = {
    "kind",
    "version",
    "generated_at",
    "public_catalog_url",
    "plugins",
}

REQUIRED_PLUGIN_FIELDS = {
    "slug",
    "name",
    "owns",
    "commands",
    "proof_types",
    "hard_stops",
    "dependencies",
    "works_with",
    "eidos_routes",
    "install_status",
    "quality",
}

REQUIRED_OWN_FIELDS = {"domain", "boundary"}
REQUIRED_INSTALL_FIELDS = {"source", "installed", "public_catalog"}
REQUIRED_QUALITY_FIELDS = {"test_command", "smoke_command", "docs", "last_proof"}

REQUIRED_EIDOS_OWNED_SLUGS = {
    "eidos",
    "eidos-plugin-store",
    "foreman",
    "emux",
    "stepproof",
    "converge",
    "surfari",
    "knox",
    "felix",
    "rhea",
    "forge-forge",
}

SECRET_FIELD_RE = re.compile(
    r"(password|passkey|secret|token|api[_-]?key|private[_-]?key|card|mfa|otp)",
    re.IGNORECASE,
)
LOCAL_PATH_RE = re.compile(r"(/Users/|/Volumes/|/private/|/var/folders/|~/.codex|~/.eidos)")


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path}: invalid JSON: {exc}") from exc


def require_keys(obj: dict[str, Any], keys: set[str], where: str, errors: list[str]) -> None:
    missing = sorted(keys - set(obj))
    if missing:
        errors.append(f"{where}: missing required keys: {', '.join(missing)}")


def require_string_list(value: Any, where: str, errors: list[str], *, allow_empty: bool = False) -> None:
    if not isinstance(value, list):
        errors.append(f"{where}: expected a list")
        return
    if not allow_empty and not value:
        errors.append(f"{where}: expected at least one item")
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item.strip():
            errors.append(f"{where}[{index}]: expected a non-empty string")


def scan_sensitive_keys(value: Any, where: str, errors: list[str]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if SECRET_FIELD_RE.search(str(key)):
                errors.append(f"{where}.{key}: secret-like field names are not allowed")
            scan_sensitive_keys(child, f"{where}.{key}", errors)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            scan_sensitive_keys(child, f"{where}[{index}]", errors)


def scan_public_local_paths(plugin: dict[str, Any], errors: list[str]) -> None:
    slug = plugin.get("slug", "<unknown>")
    public_catalog = plugin.get("install_status", {}).get("public_catalog", {})
    for key, value in public_catalog.items():
        if isinstance(value, str) and LOCAL_PATH_RE.search(value):
            errors.append(f"{slug}.install_status.public_catalog.{key}: local paths are not public-safe")


def validate_plugin(plugin: Any, index: int, errors: list[str]) -> str | None:
    if not isinstance(plugin, dict):
        errors.append(f"plugins[{index}]: expected an object")
        return None

    slug = plugin.get("slug")
    where = f"plugins[{index}]"
    if not isinstance(slug, str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]*", slug):
        errors.append(f"{where}.slug: expected lowercase slug")
        slug = None
    else:
        where = slug

    require_keys(plugin, REQUIRED_PLUGIN_FIELDS, where, errors)

    owns = plugin.get("owns")
    if isinstance(owns, dict):
        require_keys(owns, REQUIRED_OWN_FIELDS, f"{where}.owns", errors)
        require_string_list(owns.get("does_not_own", []), f"{where}.owns.does_not_own", errors, allow_empty=True)
    else:
        errors.append(f"{where}.owns: expected an object")

    commands = plugin.get("commands")
    if not isinstance(commands, list) or not commands:
        errors.append(f"{where}.commands: expected at least one command")
    else:
        for command_index, command in enumerate(commands):
            if not isinstance(command, dict):
                errors.append(f"{where}.commands[{command_index}]: expected an object")
                continue
            require_keys(command, {"name", "command", "purpose"}, f"{where}.commands[{command_index}]", errors)

    for field in ("proof_types", "hard_stops", "dependencies", "works_with"):
        require_string_list(plugin.get(field), f"{where}.{field}", errors)

    routes = plugin.get("eidos_routes")
    if not isinstance(routes, list) or not routes:
        errors.append(f"{where}.eidos_routes: expected at least one route")
    else:
        for route_index, route in enumerate(routes):
            if not isinstance(route, dict):
                errors.append(f"{where}.eidos_routes[{route_index}]: expected an object")
                continue
            require_keys(route, {"when", "stack"}, f"{where}.eidos_routes[{route_index}]", errors)
            require_string_list(route.get("stack"), f"{where}.eidos_routes[{route_index}].stack", errors)
            if "proof_required" in route:
                require_string_list(
                    route["proof_required"],
                    f"{where}.eidos_routes[{route_index}].proof_required",
                    errors,
                )

    install = plugin.get("install_status")
    if isinstance(install, dict):
        require_keys(install, REQUIRED_INSTALL_FIELDS, f"{where}.install_status", errors)
        if not isinstance(install.get("source"), dict) or not install["source"].get("repo"):
            errors.append(f"{where}.install_status.source.repo: required")
        if install.get("installed", {}).get("status") not in {"installed", "not_installed", "unknown"}:
            errors.append(f"{where}.install_status.installed.status: invalid or missing")
        if install.get("public_catalog", {}).get("status") not in {"listed", "not_listed", "unknown"}:
            errors.append(f"{where}.install_status.public_catalog.status: invalid or missing")
    else:
        errors.append(f"{where}.install_status: expected an object")

    quality = plugin.get("quality")
    if isinstance(quality, dict):
        require_keys(quality, REQUIRED_QUALITY_FIELDS, f"{where}.quality", errors)
        require_string_list(quality.get("docs"), f"{where}.quality.docs", errors)
        if quality.get("last_proof", {}).get("status") not in {"current", "stale", "missing", "unknown"}:
            errors.append(f"{where}.quality.last_proof.status: invalid or missing")
    else:
        errors.append(f"{where}.quality: expected an object")

    scan_sensitive_keys(plugin, where, errors)
    scan_public_local_paths(plugin, errors)
    return slug


def validate_registry(registry: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(registry, dict):
        return ["registry: expected an object"]

    require_keys(registry, REQUIRED_TOP_LEVEL, "registry", errors)
    if registry.get("kind") != "eidos.capability-registry":
        errors.append("registry.kind: expected eidos.capability-registry")

    plugins = registry.get("plugins")
    if not isinstance(plugins, list) or not plugins:
        errors.append("registry.plugins: expected at least one plugin")
        return errors

    slugs: list[str] = []
    for index, plugin in enumerate(plugins):
        slug = validate_plugin(plugin, index, errors)
        if slug:
            slugs.append(slug)

    duplicates = sorted({slug for slug in slugs if slugs.count(slug) > 1})
    if duplicates:
        errors.append(f"registry.plugins: duplicate slugs: {', '.join(duplicates)}")

    missing_required = sorted(REQUIRED_EIDOS_OWNED_SLUGS - set(slugs))
    if missing_required:
        errors.append(
            "registry.plugins: missing required Eidos-owned capability slugs: "
            + ", ".join(missing_required)
        )

    return errors


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: validate_capability_registry.py <registry.json>", file=sys.stderr)
        return 2

    registry_path = Path(argv[1])
    try:
        schema_path = Path(__file__).resolve().parents[1] / "schemas" / "capability-registry.schema.json"
        load_json(schema_path)
        registry = load_json(registry_path)
    except ValueError as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 1

    errors = validate_registry(registry)
    if errors:
        print("FAIL capability registry validation")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        "PASS capability registry validation: "
        f"{len(registry['plugins'])} plugins, "
        f"{len(REQUIRED_EIDOS_OWNED_SLUGS)} required Eidos-owned capabilities covered"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
