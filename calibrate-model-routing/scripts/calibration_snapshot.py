#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fcntl
import json
import os
import re
import sys
import tempfile
from contextlib import contextmanager
from datetime import date
from pathlib import Path
from typing import Iterator
from urllib.parse import urlparse


DEFAULT_PATH = Path("~/.agents/model-routing/calibration.md").expanduser()
PROVIDERS = {"codex": "Codex", "claude": "Claude"}
OFFICIAL_DOMAINS = {
    "codex": ("openai.com", "chatgpt.com"),
    "claude": ("anthropic.com", "claude.com"),
}
REQUIRED_FIELDS = (
    "Verified at",
    "Official sources",
    "Client or account constraints",
    "Workhorse",
    "Frontier",
    "Long-horizon or exceptional tier",
    "Helper or high-volume tier",
    "Effort guidance",
    "Routing notes",
)
SCALAR_FIELDS = tuple(field for field in REQUIRED_FIELDS if field != "Official sources")


class SnapshotError(ValueError):
    pass


def target_path(value: str | None = None) -> Path:
    configured = value or os.environ.get("MODEL_ROUTING_CALIBRATION_PATH")
    return Path(configured).expanduser() if configured else DEFAULT_PATH


def _frontmatter(snapshot: str) -> dict[str, str]:
    match = re.match(r"\A---\n(?P<body>.*?)\n---\n", snapshot, re.DOTALL)
    if not match:
        raise SnapshotError("snapshot must start with YAML frontmatter")
    fields: dict[str, str] = {}
    for line in match.group("body").splitlines():
        if ":" not in line:
            raise SnapshotError(f"invalid frontmatter line: {line}")
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip()
    if fields.get("schema_version") != "1":
        raise SnapshotError("schema_version must be 1")
    try:
        if int(fields.get("stale_after_days", "0")) <= 0:
            raise ValueError
    except ValueError as error:
        raise SnapshotError("stale_after_days must be a positive integer") from error
    return fields


def _section_bounds(snapshot: str, provider: str) -> tuple[int, int]:
    display = PROVIDERS[provider]
    heading = f"## {display}\n"
    start = snapshot.find(heading)
    if start < 0:
        raise SnapshotError(f"missing {display} section")
    later = [
        snapshot.find(f"## {other}\n", start + len(heading))
        for key, other in PROVIDERS.items()
        if key != provider
    ]
    ends = [position for position in later if position >= 0]
    return start, min(ends) if ends else len(snapshot)


def provider_section(snapshot: str, provider: str) -> str:
    start, end = _section_bounds(snapshot, provider)
    return snapshot[start:end].rstrip() + "\n"


def _provider_date(section: str) -> date:
    match = re.search(r"(?m)^- Verified at: (\d{4}-\d{2}-\d{2})$", section)
    if not match:
        raise SnapshotError("provider section needs an ISO Verified at date")
    try:
        return date.fromisoformat(match.group(1))
    except ValueError as error:
        raise SnapshotError("Verified at must be a valid ISO date") from error


def validate_provider_section(
    provider: str,
    section: str,
    today: date | None = None,
) -> None:
    if provider not in PROVIDERS:
        raise SnapshotError(f"unknown provider: {provider}")
    display = PROVIDERS[provider]
    if not section.startswith(f"## {display}\n"):
        raise SnapshotError(f"section must start with ## {display}")

    field_values: dict[str, str] = {}
    for field in REQUIRED_FIELDS:
        matches = re.findall(
            rf"(?m)^- {re.escape(field)}:(?P<value>[^\n]*)$",
            section,
        )
        if len(matches) != 1:
            raise SnapshotError(f"{display} section must contain {field} exactly once")
        field_values[field] = matches[0]

    for field in SCALAR_FIELDS:
        if not field_values[field].strip():
            raise SnapshotError(f"{display} section {field} needs a non-empty value")

    if field_values["Official sources"].strip():
        raise SnapshotError(f"{display} Official sources must be an indented list")
    sources_heading = re.search(r"(?m)^- Official sources:[ \t]*\n", section)
    if sources_heading is None:
        raise SnapshotError(f"{display} Official sources must be an indented list")
    constraints_heading = re.search(
        r"(?m)^- Client or account constraints:",
        section[sources_heading.end():],
    )
    if constraints_heading is None:
        raise SnapshotError(
            f"{display} Client or account constraints must follow Official sources"
        )
    sources_block = section[
        sources_heading.end():
        sources_heading.end() + constraints_heading.start()
    ]
    source_urls: list[str] = []
    for line in sources_block.splitlines():
        if not line.strip():
            continue
        source = re.fullmatch(r"  - (https://\S+)[ \t]*", line)
        if not source:
            raise SnapshotError(
                f"{display} Official sources must contain only indented HTTPS URL items"
            )
        source_urls.append(source.group(1))
    if not source_urls:
        raise SnapshotError(
            f"{display} Official sources needs at least one indented HTTPS URL"
        )

    verified_at = _provider_date(section)
    current = today or date.today()
    if verified_at > current:
        raise SnapshotError(
            f"{display} Verified at date cannot be in the future: {verified_at}"
        )
    allowed = OFFICIAL_DOMAINS[provider]
    for url in source_urls:
        host = (urlparse(url).hostname or "").lower()
        if not any(host == domain or host.endswith(f".{domain}") for domain in allowed):
            raise SnapshotError(f"source must use an official {display} domain: {url}")


def validate_snapshot(snapshot: str, today: date | None = None) -> None:
    current = today or date.today()
    _frontmatter(snapshot)
    if "# Model routing calibration\n" not in snapshot:
        raise SnapshotError("snapshot needs the model routing calibration title")
    codex_start, _ = _section_bounds(snapshot, "codex")
    claude_start, _ = _section_bounds(snapshot, "claude")
    if codex_start >= claude_start:
        raise SnapshotError("Codex section must precede Claude section")
    for provider in PROVIDERS:
        validate_provider_section(
            provider,
            provider_section(snapshot, provider),
            today=current,
        )


def replace_provider(
    snapshot: str,
    provider: str,
    section: str,
    today: date | None = None,
) -> str:
    current = today or date.today()
    validate_snapshot(snapshot, today=current)
    normalized = section.rstrip() + "\n"
    validate_provider_section(provider, normalized, today=current)
    start, end = _section_bounds(snapshot, provider)
    separator = "\n" if end < len(snapshot) else ""
    updated = snapshot[:start] + normalized + separator + snapshot[end:]
    validate_snapshot(updated, today=current)
    return updated


def stale_providers(snapshot: str, today: date | None = None) -> list[str]:
    fields = _frontmatter(snapshot)
    current = today or date.today()
    validate_snapshot(snapshot, today=current)
    limit = int(fields["stale_after_days"])
    return [
        provider
        for provider in PROVIDERS
        if (current - _provider_date(provider_section(snapshot, provider))).days > limit
    ]


def atomic_install(
    path: Path,
    snapshot: str,
    today: date | None = None,
) -> None:
    validate_snapshot(snapshot, today=today)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=path.parent, delete=False
        ) as handle:
            handle.write(snapshot)
            temporary = Path(handle.name)
        os.replace(temporary, path)
    finally:
        if temporary and temporary.exists():
            temporary.unlink()


@contextmanager
def _snapshot_lock(path: Path) -> Iterator[None]:
    path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = Path(f"{path}.lock")
    with lock_path.open("a+") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage model routing calibration")
    commands = parser.add_subparsers(dest="command", required=True)
    validate = commands.add_parser("validate")
    validate.add_argument("--input", required=True)
    install = commands.add_parser("install")
    install.add_argument("--input", required=True)
    install.add_argument("--path")
    replace = commands.add_parser("replace-provider")
    replace.add_argument("--provider", choices=PROVIDERS, required=True)
    replace.add_argument("--input", required=True)
    replace.add_argument("--path")
    status = commands.add_parser("status")
    status.add_argument("--path")
    return parser


def main() -> int:
    args = _parser().parse_args()
    try:
        if args.command == "validate":
            validate_snapshot(Path(args.input).read_text())
            print("valid")
            return 0
        path = target_path(args.path)
        if args.command == "install":
            with _snapshot_lock(path):
                atomic_install(path, Path(args.input).read_text())
            print(path)
            return 0
        if args.command == "replace-provider":
            with _snapshot_lock(path):
                current = path.read_text()
                updated = replace_provider(
                    current,
                    args.provider,
                    Path(args.input).read_text(),
                )
                atomic_install(path, updated)
            print(path)
            return 0
        if not path.exists():
            print(json.dumps({"status": "missing", "path": str(path)}))
            return 0
        text = path.read_text()
        stale = stale_providers(text)
        print(json.dumps({
            "status": "stale" if stale else "fresh",
            "path": str(path),
            "stale_providers": stale,
        }))
        return 0
    except (OSError, SnapshotError) as error:
        if getattr(args, "command", None) == "status":
            print(json.dumps({"status": "invalid", "error": str(error)}))
            return 0
        print(str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
