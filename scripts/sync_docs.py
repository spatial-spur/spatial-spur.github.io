from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import tempfile
import urllib.error
import urllib.request
from pathlib import Path


SITE_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DOCS_ROOT = SITE_ROOT / "docs"
DEFAULT_BUILD_ROOT = SITE_ROOT / ".build" / "site-src"
PACKAGE_SOURCES = {
    "spur-skills": "spatial-spur/spur-skills",
    "spuR": "spatial-spur/spuR",
    "spur-python": "spatial-spur/spur-python",
    "spur-stata": "spatial-spur/spur-stata",
    "scpcR": "spatial-spur/scpcR",
    "scpc-python": "spatial-spur/scpc-python",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sync package docs into the central spatial-spur site."
    )
    parser.add_argument(
        "--source-repo",
        help="GitHub repo in owner/name form, e.g. spatial-spur/spur-skills.",
    )
    parser.add_argument(
        "--source-ref",
        help="Git ref to fetch from GitHub, e.g. main or v0.1.0b1.",
    )
    return parser.parse_args()


def replace_tree(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def copy_site_source(build_root: Path) -> None:
    if build_root.exists():
        shutil.rmtree(build_root)

    build_root.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SITE_ROOT / "mkdocs.yml", build_root / "mkdocs.yml")
    shutil.copytree(SOURCE_DOCS_ROOT, build_root / "docs")


def has_real_docs(src: Path) -> bool:
    if not src.is_dir():
        return False

    for path in src.rglob("*"):
        if path.is_file() and path.name != ".gitkeep":
            return True

    return False


def sync_docs_tree(src: Path, slug: str, build_root: Path) -> None:
    dst = build_root / "docs" / slug
    replace_tree(src, dst)


def sync_from_local(slug: str, local_root: Path, build_root: Path) -> bool:
    src = local_root / slug / "docs"
    if not has_real_docs(src):
        print(f"[sync_docs] local docs missing or empty at {src}; keeping placeholder.")
        return False

    sync_docs_tree(src, slug, build_root)
    print(f"[sync_docs] synced local docs from {src} -> {build_root / 'docs' / slug}")
    return True


def resolve_latest_published_release_tag(source_repo: str) -> str | None:
    url = f"https://api.github.com/repos/{source_repo}/releases?per_page=1"
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )

    try:
        with urllib.request.urlopen(request) as response:
            releases = json.load(response)
    except urllib.error.HTTPError as exc:
        print(
            f"[sync_docs] could not query releases for {source_repo}: {exc}; keeping placeholder."
        )
        return None
    except urllib.error.URLError as exc:
        print(
            f"[sync_docs] could not reach GitHub for {source_repo}: {exc}; keeping placeholder."
        )
        return None

    if not releases:
        print(
            f"[sync_docs] no published releases found for {source_repo}; keeping placeholder."
        )
        return None

    tag_name = releases[0].get("tag_name")
    if not tag_name:
        print(
            f"[sync_docs] latest release for {source_repo} has no tag name; keeping placeholder."
        )
        return None

    return tag_name


def sync_from_github(
    source_repo: str,
    source_ref: str,
    slug: str,
    build_root: Path,
    *,
    strict: bool = False,
) -> bool:
    clone_url = f"https://github.com/{source_repo}.git"

    with tempfile.TemporaryDirectory(prefix="spatial_spur_docs_") as tmpdir:
        tmp_path = Path(tmpdir)
        try:
            subprocess.run(
                [
                    "git",
                    "clone",
                    "--depth",
                    "1",
                    "--branch",
                    source_ref,
                    clone_url,
                    str(tmp_path),
                ],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except subprocess.CalledProcessError as exc:
            message = f"[sync_docs] could not clone {source_repo}@{source_ref}"
            if strict:
                raise SystemExit(message) from exc
            print(f"{message}; keeping placeholder.")
            return False

        src = tmp_path / "docs"
        if not has_real_docs(src):
            print(
                f"[sync_docs] GitHub source {source_repo}@{source_ref} has no real docs/; keeping placeholder."
            )
            return False

        sync_docs_tree(src, slug, build_root)
        print(
            f"[sync_docs] synced GitHub docs from {source_repo}@{source_ref} -> {build_root / 'docs' / slug}"
        )
        return True


def main() -> int:
    args = parse_args()
    build_root = DEFAULT_BUILD_ROOT.resolve()
    copy_site_source(build_root)

    explicit_slug: str | None = None
    explicit_repo: str | None = None
    explicit_ref: str | None = None

    if args.source_repo or args.source_ref:
        if not args.source_repo or not args.source_ref:
            raise SystemExit(
                "--source-repo and --source-ref must be provided together for GitHub sync mode."
            )
        explicit_repo = args.source_repo
        explicit_ref = args.source_ref
        explicit_slug = args.source_repo.rsplit("/", 1)[-1]
        if (
            explicit_slug not in PACKAGE_SOURCES
            or PACKAGE_SOURCES[explicit_slug] != args.source_repo
        ):
            raise SystemExit(
                f"--source-repo must be one of: {', '.join(PACKAGE_SOURCES.values())}"
            )

    local_root = SITE_ROOT.parent.resolve()

    for slug, source_repo in PACKAGE_SOURCES.items():
        if slug == explicit_slug:
            if explicit_repo is None or explicit_ref is None:
                raise AssertionError("explicit GitHub sync inputs must be set")
            sync_from_github(explicit_repo, explicit_ref, slug, build_root, strict=True)
            continue

        if sync_from_local(slug, local_root, build_root):
            continue

        latest_ref = resolve_latest_published_release_tag(source_repo)
        if latest_ref is None:
            continue

        sync_from_github(source_repo, latest_ref, slug, build_root)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
