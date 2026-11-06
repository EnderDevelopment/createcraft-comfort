"""Build a Modrinth .mrpack from compatible Modrinth project releases."""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

MINECRAFT_VERSION = "1.20.1"
LOADER = "forge"
OUTPUT_NAME = "dragonworks-create-dragons.mrpack"
ROOT = Path(__file__).parent
BUILD_DIR = ROOT / ".pack-build"
DIST_DIR = ROOT / "dist"

# These are Modrinth slugs. Book of Dragons is selected by its exact title below
# because the project slug may differ from the title shown on Modrinth.
PACK_MODS = [
    "create",
    "steam-n-rails",
    "create-big-cannons",
    "create-crafts-additions",
    "jei",
    "jade",
    "appleskin",
    "mouse-tweaks",
    "embeddium",
    "modernfix",
    "ferrite-core",
    "immediatelyfast",
    "entityculling",
    "journeymap",
]
BOOK_OF_DRAGONS_TITLE = "Book of Dragons"
API_ROOT = "https://api.modrinth.com/v2"


def api_get(path: str, params: dict[str, str | int] | None = None) -> object:
    url = API_ROOT + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(url, headers={"User-Agent": "DragonworksPackBuilder/1.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def find_project(slug: str) -> dict:
    try:
        return api_get(f"/project/{urllib.parse.quote(slug)}")  # type: ignore[return-value]
    except Exception as error:
        raise RuntimeError(f"Modrinth project not found: {slug}") from error


def find_book_of_dragons() -> dict:
    results = api_get("/search", {"query": BOOK_OF_DRAGONS_TITLE, "limit": 20})
    for project in results["hits"]:  # type: ignore[index]
        if project.get("title", "").casefold() == BOOK_OF_DRAGONS_TITLE.casefold():
            return find_project(project["slug"])
    raise RuntimeError(
        f'Modrinth has no project whose exact title is "{BOOK_OF_DRAGONS_TITLE}".'
    )


def select_version(project: dict) -> dict:
    versions = api_get(
        f"/project/{project['id']}/version",
        {"game_versions": json.dumps([MINECRAFT_VERSION]), "loaders": json.dumps([LOADER])},
    )
    if not versions:  # type: ignore[truthy-bool]
        raise RuntimeError(
            f"{project['title']} has no {LOADER} {MINECRAFT_VERSION} release on Modrinth."
        )
    return versions[0]  # type: ignore[index]


def download_file(file_info: dict, target: Path) -> None:
    request = urllib.request.Request(
        file_info["url"], headers={"User-Agent": "DragonworksPackBuilder/1.0"}
    )
    with urllib.request.urlopen(request, timeout=120) as response, target.open("wb") as output:
        shutil.copyfileobj(response, output)
    digest = hashlib.sha512(target.read_bytes()).hexdigest()
    if digest != file_info["hashes"]["sha512"]:
        raise RuntimeError(f"SHA-512 verification failed for {target.name}")


def main() -> None:
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    mods_dir = BUILD_DIR / "overrides" / "mods"
    mods_dir.mkdir(parents=True)
    projects = [find_project(slug) for slug in PACK_MODS]
    projects.append(find_book_of_dragons())
    files: list[dict[str, object]] = []
    downloaded: set[str] = set()

    for project in projects:
        version = select_version(project)
        file_info = next((item for item in version["files"] if item.get("primary")), version["files"][0])
        filename = file_info["filename"]
        if filename in downloaded:
            continue
        downloaded.add(filename)
        download_file(file_info, mods_dir / filename)
        files.append({
            "path": f"overrides/mods/{filename}",
            "hashes": file_info["hashes"],
            "env": {"client": "required", "server": "required"},
            "downloads": [file_info["url"]],
            "fileSize": file_info["size"],
        })
        print(f"Added {project['title']} {version['version_number']}")

    index = {
        "formatVersion": 1,
        "game": "minecraft",
        "versionId": "1.0.0",
        "name": "Dragonworks: Create & Dragons",
        "summary": "Create automation, Book of Dragons, add-ons, and QoL mods.",
        "files": files,
        "dependencies": {"minecraft": MINECRAFT_VERSION, "forge": "47.3.0"},
    }
    (BUILD_DIR / "modrinth.index.json").write_text(json.dumps(index, indent=2), encoding="utf-8")
    DIST_DIR.mkdir()
    archive = shutil.make_archive(str(DIST_DIR / OUTPUT_NAME.removesuffix(".mrpack")), "zip", BUILD_DIR)
    Path(archive).rename(DIST_DIR / OUTPUT_NAME)
    print(f"Built {DIST_DIR / OUTPUT_NAME}")


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError, urllib.error.URLError, json.JSONDecodeError) as error:
        print(f"Build failed: {error}", file=sys.stderr)
        sys.exit(1)
