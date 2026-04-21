from __future__ import annotations

import argparse
import shutil
import subprocess
import tempfile
from pathlib import Path


SITE_ROOT = Path(__file__).resolve().parents[1]
DOCS_ROOT = SITE_ROOT / "docs"
DEFAULT_SOURCE_REPO = "spatial-spur/spur-skills"
DEFAULT_SOURCE_SLUG = "spur-skills"


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
    parser.add_argument(
        "--source-slug",
        help="Destination slug under docs/, defaults to the repo name.",
    )
    parser.add_argument(
        "--local-root",
        default=str(SITE_ROOT.parent),
        help="Sibling root for local preview mode. Defaults to the parent directory.",
    )
    return parser.parse_args()


def replace_tree(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def sync_from_local(slug: str, local_root: Path) -> bool:
    src = local_root / slug / "docs"
    if not src.is_dir():
        print(f"[sync_docs] local docs not found at {src}; keeping placeholder.")
        return False

    dst = DOCS_ROOT / slug
    replace_tree(src, dst)
    print(f"[sync_docs] synced local docs from {src} -> {dst}")
    return True


def sync_from_github(source_repo: str, source_ref: str, slug: str) -> bool:
    clone_url = f"https://github.com/{source_repo}.git"

    with tempfile.TemporaryDirectory(prefix="spatial_spur_docs_") as tmpdir:
        tmp_path = Path(tmpdir)
        subprocess.run(
            ["git", "clone", "--depth", "1", "--branch", source_ref, clone_url, str(tmp_path)],
            check=True,
        )

        src = tmp_path / "docs"
        if not src.is_dir():
            print(
                f"[sync_docs] GitHub source {source_repo}@{source_ref} has no docs/; keeping placeholder."
            )
            return False

        dst = DOCS_ROOT / slug
        replace_tree(src, dst)
        print(f"[sync_docs] synced GitHub docs from {source_repo}@{source_ref} -> {dst}")
        return True


def main() -> int:
    args = parse_args()

    if args.source_repo or args.source_ref:
        if not args.source_repo or not args.source_ref:
            raise SystemExit(
                "--source-repo and --source-ref must be provided together for GitHub sync mode."
            )
        slug = args.source_slug or args.source_repo.rsplit("/", 1)[-1]
        sync_from_github(args.source_repo, args.source_ref, slug)
        return 0

    slug = args.source_slug or DEFAULT_SOURCE_SLUG
    local_root = Path(args.local_root).resolve()
    if sync_from_local(slug, local_root):
        return 0

    sync_from_github(DEFAULT_SOURCE_REPO, "main", slug)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
