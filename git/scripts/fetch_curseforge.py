#!/usr/bin/env python3
"""
Download mods from CurseForge automatically.

Usage:
  python git/scripts/fetch_curseforge.py           # download everything
  python git/scripts/fetch_curseforge.py server    # same as above

Configuration:
  * Set CURSEFORGE_API_KEY in the environment (get one at https://console.curseforge.com/).
  * Edit mods/sources/curseforge.json and list mods by slug or modId.
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
LIST_PATH = SOURCES_DIR / "curseforge.json"
DEST_DIR = ROOT / "mods" / "server"
LOG_FILE = SOURCES_DIR / "download_log.csv"

GAME_VERSION = os.environ.get("MINECRAFT_VERSION", "1.20.1")
MODLOADER_DEFAULT = os.environ.get("CURSEFORGE_MODLOADER", "forge")
API_KEY = os.environ.get("CURSEFORGE_API_KEY")

API_BASE = "https://api.curseforge.com/v1"
GAME_ID = 432  # Minecraft: Java Edition

MODLOADER_MAP = {
    "any": 0,
    "forge": 1,
    "cauldron": 2,
    "liteloader": 3,
    "fabric": 4,
    "quilt": 5,
    "neoforge": 6,
}


def ensure_log_header() -> None:
    if LOG_FILE.exists():
        return
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


def log_entry(name: str, slug: str, version: dict | None, dest_path: Path, status: str, message: str = "") -> None:
    ensure_log_header()
    version_id = ""
    version_number = ""
    version_type = ""
    file_name = ""
    file_url = ""

    if version:
        version_id = str(version.get("id", ""))
        version_number = version.get("displayName") or version.get("fileName", "")
        release_type = version.get("releaseType")
        version_type = {1: "release", 2: "beta", 3: "alpha"}.get(release_type, str(release_type))
        file_name = version.get("fileName", "")
        file_url = version.get("downloadUrl", "")

    with LOG_FILE.open("a", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(
            [
                dt.datetime.now(dt.timezone.utc).isoformat(),
                "server",
                name,
                slug,
                version_id,
                version_number,
                version_type,
                file_name,
                file_url,
                str(dest_path),
                status,
                message,
            ]
        )


def api_get(path: str, params: dict | None = None) -> dict:
    if params:
        query = urllib.parse.urlencode(params)
        url = f"{API_BASE}{path}?{query}"
    else:
        url = f"{API_BASE}{path}"
    req = urllib.request.Request(url, headers={"x-api-key": API_KEY, "Accept": "application/json"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


def find_mod(entry: dict) -> dict | None:
    if mod_id := entry.get("modId"):
        try:
            return api_get(f"/mods/{mod_id}")["data"]
        except (urllib.error.HTTPError, urllib.error.URLError, KeyError) as err:
            print(f"[error] Failed to fetch mod {mod_id}: {err}")
            return None

    slug = entry.get("slug") or entry["name"]
    params = {
        "gameId": GAME_ID,
        "slug": slug,
        "searchFilter": slug,
        "pageSize": 1,
    }
    try:
        data = api_get("/mods/search", params).get("data") or []
    except (urllib.error.HTTPError, urllib.error.URLError) as err:
        print(f"[error] Search failed for {slug}: {err}")
        return None

    if not data:
        print(f"[warn] No mod found for slug '{slug}'")
        return None
    return data[0]


def pick_file(mod_id: int, loader_value: int | None) -> dict | None:
    params = {
        "gameVersion": GAME_VERSION,
        "pageSize": 50,
        "index": 0,
        "sortField": 2,  # newest first
        "sortOrder": "desc",
    }
    if loader_value is not None:
        params["modLoaderType"] = loader_value
    try:
        files = api_get(f"/mods/{mod_id}/files", params).get("data") or []
    except (urllib.error.HTTPError, urllib.error.URLError) as err:
        print(f"[error] Failed to list files for mod {mod_id}: {err}")
        return None

    if not files:
        return None

    files.sort(key=lambda f: f.get("fileDate", ""), reverse=True)
    for f in files:
        if f.get("releaseType") == 1:
            return f
    return files[0]


def download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url) as resp, dest.open("wb") as fh:
        shutil.copyfileobj(resp, fh)


def run() -> int:
    if not API_KEY:
        print("[error] CURSEFORGE_API_KEY is not set. Get one from https://console.curseforge.com/.")
        return 1
    if not LIST_PATH.exists():
        print(f"[info] {LIST_PATH} not found, nothing to do.")
        return 0

    entries = json.loads(LIST_PATH.read_text(encoding="utf-8"))
    loader_default = MODLOADER_MAP.get(MODLOADER_DEFAULT.lower(), 1)
    exit_code = 0

    for entry in entries:
        name = entry["name"]
        slug = entry.get("slug") or name
        print(f"-> {name} ({slug})")

        mod_data = find_mod(entry)
        if not mod_data:
            log_entry(name, slug, None, DEST_DIR, "error", "mod not found")
            exit_code = 1
            continue

        loader_value = loader_default
        if "modLoaderType" in entry:
            custom = entry["modLoaderType"]
            if isinstance(custom, str):
                loader_value = MODLOADER_MAP.get(custom.lower(), loader_default)
            else:
                loader_value = custom

        file_info = pick_file(mod_data["id"], loader_value)
        if not file_info:
            print(f"[warn] No files for mod {mod_data['id']} ({slug}) matching version {GAME_VERSION}")
            log_entry(name, slug, None, DEST_DIR, "error", "file not found")
            exit_code = 1
            continue

        filename = file_info["fileName"]
        dest_path = DEST_DIR / filename

        if dest_path.exists():
            print(f"[skip] Already have {filename}")
            log_entry(name, slug, file_info, dest_path, "skipped", "file exists")
            continue

        download_url = file_info.get("downloadUrl")
        if not download_url:
            print(f"[error] Missing download URL for {filename}")
            log_entry(name, slug, file_info, dest_path, "error", "missing download url")
            exit_code = 1
            continue

        try:
            download(download_url, dest_path)
            print(f"[ok] Downloaded -> {dest_path}")
            log_entry(name, slug, file_info, dest_path, "downloaded", "")
        except urllib.error.URLError as err:
            print(f"[error] Download failed for {filename}: {err}")
            log_entry(name, slug, file_info, dest_path, "error", str(err))
            exit_code = 1

    return exit_code


if __name__ == "__main__":
    sys.exit(run())
