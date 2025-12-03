#!/usr/bin/env python3
"""
Automatic Modrinth downloader.

Examples:
  python git/scripts/fetch_modrinth.py server
  python git/scripts/fetch_modrinth.py client
  python git/scripts/fetch_modrinth.py all

Mod lists live in mods/sources/modrinth-*.json.
For each mod we grab the latest Forge 1.20.1 build and log the URL.
"""

from __future__ import annotations

import csv
import datetime as dt
import json
import os
from pathlib import Path
import sys
import urllib.error
import urllib.parse
import urllib.request
import shutil

ROOT = Path(__file__).resolve().parents[2]
SOURCES_DIR = ROOT / "mods" / "sources"
LOG_FILE = SOURCES_DIR / "download_log.csv"
GAME_VERSION = os.environ.get("MINECRAFT_VERSION", "1.20.1")
LOADER = os.environ.get("MINECRAFT_LOADER", "forge")


def ensure_log_header() -> None:
    if not LOG_FILE.exists():
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with LOG_FILE.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(
                [
                    "timestamp",
                    "category",
                    "name",
                    "slug",
                    "version_id",
                    "version_number",
                    "version_type",
                    "file_name",
                    "file_url",
                    "dest_path",
                    "status",
                    "message",
                ]
            )


def log_entry(category: str, name: str, slug: str, version: dict | None, file_info: dict | None, dest: Path, status: str, message: str) -> None:
    ensure_log_header()
    version_id = version.get("id") if version else ""
    version_number = version.get("version_number") if version else ""
    version_type = version.get("version_type") if version else ""
    file_name = file_info.get("filename") if file_info else ""
    file_url = file_info.get("url") if file_info else ""

    with LOG_FILE.open("a", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(
            [
                dt.datetime.now(dt.timezone.utc).isoformat(),
                category,
                name,
                slug,
                version_id,
                version_number,
                version_type,
                file_name,
                file_url,
                str(dest),
                status,
                message,
            ]
        )


def fetch_versions(slug: str, featured_only: bool = True) -> list[dict]:
    params = {
        "game_versions": json.dumps([GAME_VERSION]),
        "loaders": json.dumps([LOADER]),
    }
    if featured_only:
        params["featured"] = "true"
    url = f"https://api.modrinth.com/v2/project/{slug}/version?{urllib.parse.urlencode(params)}"
    with urllib.request.urlopen(url) as resp:
        return json.loads(resp.read().decode("utf-8"))


def pick_version(slug: str) -> dict | None:
    try:
        versions = fetch_versions(slug, featured_only=True)
        if not versions:
            versions = fetch_versions(slug, featured_only=False)
    except urllib.error.HTTPError as err:
        print(f"[error] {slug}: HTTP {err.code}")
        return None
    except urllib.error.URLError as err:
        print(f"[error] {slug}: {err}")
        return None

    if not versions:
        print(f"[warn] No versions for {slug} (Forge {GAME_VERSION})")
        return None

    def latest_of_type(vtype: str) -> dict | None:
        candidates = [v for v in versions if (v.get("version_type") or "").lower() == vtype]
        if not candidates:
            return None
        return max(candidates, key=lambda v: v.get("date_published", ""))

    for vtype in ("release", "beta", "alpha"):
        chosen = latest_of_type(vtype)
        if chosen:
            return chosen
    return max(versions, key=lambda v: v.get("date_published", ""))


def pick_file(version: dict) -> dict | None:
    files = version.get("files") or []
    if not files:
        return None
    primary = next((f for f in files if f.get("primary")), None)
    return primary or files[0]


def download_file(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url) as resp, dest.open("wb") as fh:
        shutil.copyfileobj(resp, fh)


def process_list(category: str, list_path: Path, dest_dir: Path) -> None:
    if not list_path.exists():
        print(f"[info] {list_path} not found")
        return

    entries = json.loads(list_path.read_text(encoding="utf-8"))
    for entry in entries:
        name = entry["name"]
        slug = entry["slug"]
        print(f"-> {name} ({slug})")

        version = pick_version(slug)
        if not version:
            log_entry(category, name, slug, None, None, dest_dir, "error", "version not found")
            continue

        file_info = pick_file(version)
        if not file_info:
            print(f"[warn] No files in version {version.get('id')}")
            log_entry(category, name, slug, version, None, dest_dir, "error", "file not found")
            continue

        filename = file_info["filename"]
        dest_path = dest_dir / filename

        if dest_path.exists():
            print(f"[skip] Already have {filename}")
            log_entry(category, name, slug, version, file_info, dest_path, "skipped", "file exists")
            continue

        try:
            download_file(file_info["url"], dest_path)
            print(f"[ok] Downloaded -> {dest_path}")
            log_entry(category, name, slug, version, file_info, dest_path, "downloaded", "")
        except urllib.error.URLError as err:
            print(f"[error] Download failed for {filename}: {err}")
            log_entry(category, name, slug, version, file_info, dest_path, "error", str(err))


def main() -> None:
    target = (sys.argv[1] if len(sys.argv) > 1 else "all").lower()
    valid = {"server", "client", "all"}
    if target not in valid:
        print("Usage: python git/scripts/fetch_modrinth.py [server|client|all]")
        sys.exit(1)

    mapping = {
        "server": (SOURCES_DIR / "modrinth-server.json", ROOT / "mods" / "server"),
        "client": (SOURCES_DIR / "modrinth-client.json", ROOT / "mods" / "client"),
    }

    if target in ("server", "all"):
        process_list("server", mapping["server"][0], mapping["server"][1])
    if target in ("client", "all"):
        process_list("client", mapping["client"][0], mapping["client"][1])


if __name__ == "__main__":
    main()
