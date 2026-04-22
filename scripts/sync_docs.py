from __future__ import annotations

import shutil
import subprocess
import tempfile
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


def sync_from_github(
    source_repo: str,
    source_ref: str,
    slug: str,
    build_root: Path,
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
        except subprocess.CalledProcessError:
            print(
                f"[sync_docs] could not clone {source_repo}@{source_ref}; keeping placeholder."
            )
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
    build_root = DEFAULT_BUILD_ROOT.resolve()
    copy_site_source(build_root)

    local_root = SITE_ROOT.parent.resolve()

    for slug, source_repo in PACKAGE_SOURCES.items():
        if sync_from_local(slug, local_root, build_root):
            continue

        sync_from_github(source_repo, "main", slug, build_root)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
