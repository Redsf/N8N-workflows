#!/usr/bin/env python3
"""Validate n8n workflow JSON exports before they are published.

Run over one or more files or directories:

    python scripts/validate_workflows.py .

Exit codes:
    0  no errors (warnings may still be printed)
    1  at least one error

Errors block a merge. Warnings are advisory and describe reliability gaps
(missing error handling, orphaned nodes) rather than correctness problems.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Credential IDs that are safe to publish. Anything else is an instance-specific
# ID that leaks which credential a private n8n instance used and breaks import
# for anyone else.
PLACEHOLDER_CREDENTIAL_IDS = frozenset(
    {"REPLACE_WITH_CREDENTIAL_ID", "REPLACE_WITH_CREDENTIAL", "PLACEHOLDER", ""}
)

# Node types that legitimately have no connections on the canvas.
UNCONNECTED_NODE_TYPES = frozenset({"n8n-nodes-base.stickyNote"})

SECRET_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("OpenAI API key", re.compile(r"sk-(?:proj-)?[A-Za-z0-9_\-]{20,}")),
    ("GitHub token", re.compile(r"gh[pousr]_[A-Za-z0-9]{36,}")),
    ("AWS access key ID", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("Google API key", re.compile(r"AIza[0-9A-Za-z_\-]{35}")),
    ("Slack token", re.compile(r"xox[baprs]-[0-9A-Za-z-]{10,}")),
    ("Anthropic API key", re.compile(r"sk-ant-[A-Za-z0-9_\-]{20,}")),
    ("Private key block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("JWT", re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]+")),
)

# A match containing any of these is a documented placeholder, not a live secret.
PLACEHOLDER_MARKERS = ("REPLACE", "YOUR", "EXAMPLE", "PLACEHOLDER", "XXXX", "<", "...")


class Report:
    """Collects findings for a single validation run."""

    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, where: str, message: str) -> None:
        self.errors.append(f"{where}: {message}")

    def warn(self, where: str, message: str) -> None:
        self.warnings.append(f"{where}: {message}")


def looks_like_placeholder(match: str) -> bool:
    upper = match.upper()
    return any(marker in upper for marker in PLACEHOLDER_MARKERS)


def check_secrets(raw: str, where: str, report: Report) -> None:
    for label, pattern in SECRET_PATTERNS:
        for match in pattern.findall(raw):
            if looks_like_placeholder(match):
                continue
            redacted = match[:6] + "…" + match[-4:] if len(match) > 12 else "…"
            report.error(where, f"possible {label} in file ({redacted})")


def check_credentials(nodes: list[dict], where: str, report: Report) -> None:
    for node in nodes:
        credentials = node.get("credentials") or {}
        for cred_type, cred in credentials.items():
            if not isinstance(cred, dict):
                continue
            cred_id = cred.get("id")
            if cred_id is None:
                continue
            if cred_id not in PLACEHOLDER_CREDENTIAL_IDS:
                report.error(
                    where,
                    f'node "{node.get("name", "?")}" has a real {cred_type} credential ID '
                    f'("{cred_id}") — replace with REPLACE_WITH_CREDENTIAL_ID',
                )


def check_error_handling(nodes: list[dict], where: str, report: Report) -> None:
    has_error_trigger = any(
        node.get("type", "").endswith("errorTrigger") and not node.get("disabled")
        for node in nodes
    )
    if not has_error_trigger:
        report.warn(where, "no active Error Trigger — failures will pass unnoticed")


def check_orphans(nodes: list[dict], connections: dict, where: str, report: Report) -> None:
    sources = set(connections.keys())
    targets: set[str] = set()
    for outputs in connections.values():
        if not isinstance(outputs, dict):
            continue
        for branches in outputs.values():
            for branch in branches or []:
                for link in branch or []:
                    if isinstance(link, dict) and "node" in link:
                        targets.add(link["node"])

    connected = sources | targets
    for node in nodes:
        name = node.get("name", "?")
        if node.get("type") in UNCONNECTED_NODE_TYPES:
            continue
        if name not in connected:
            report.warn(where, f'node "{name}" is not connected to anything')


def check_disabled(nodes: list[dict], where: str, report: Report) -> None:
    for node in nodes:
        if node.get("disabled"):
            report.warn(where, f'node "{node.get("name", "?")}" is disabled')


def validate_file(path: Path, report: Report) -> None:
    where = str(path)
    raw = path.read_text(encoding="utf-8")

    check_secrets(raw, where, report)

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        report.error(where, f"invalid JSON — {exc}")
        return

    if not isinstance(data, dict) or "nodes" not in data:
        report.error(where, "not an n8n workflow export (no top-level 'nodes' key)")
        return

    nodes = data.get("nodes") or []
    connections = data.get("connections") or {}

    if not nodes:
        report.error(where, "workflow has no nodes")
        return

    check_credentials(nodes, where, report)
    check_error_handling(nodes, where, report)
    check_orphans(nodes, connections, where, report)
    check_disabled(nodes, where, report)


def collect_files(paths: list[str]) -> list[Path]:
    files: list[Path] = []
    for raw_path in paths:
        path = Path(raw_path)
        if path.is_dir():
            files.extend(
                p for p in sorted(path.rglob("*.json")) if ".git" not in p.parts
            )
        elif path.suffix == ".json":
            files.append(path)
    return files


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", default=["."], help="files or directories")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="treat warnings as errors",
    )
    args = parser.parse_args()

    files = collect_files(args.paths or ["."])
    if not files:
        print("No workflow JSON files found.", file=sys.stderr)
        return 1

    report = Report()
    for path in files:
        validate_file(path, report)

    for warning in report.warnings:
        print(f"WARN  {warning}")
    for error in report.errors:
        print(f"ERROR {error}")

    print(
        f"\nChecked {len(files)} workflow file(s): "
        f"{len(report.errors)} error(s), {len(report.warnings)} warning(s)."
    )

    if report.errors:
        return 1
    if args.strict and report.warnings:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
