import os
import re
import time
from typing import Dict
import requests
from pathlib import Path
from enum import Enum, auto
from loguru import logger
from shutil import copy2
import csv
import hashlib

# ---------------------------------------------------------------------------
# Shared constants / enums
# ---------------------------------------------------------------------------
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
DELETE_VALUE = "DELETE"
IGNORE_EXTS = {".url"}
DONOTCMP_MARKER = "DONOTCMP"
README_APP_MD = "readme.app.md"
# ---------------------------------------------------------------------------
# Shared configurable constants (used by git_cmp.py and others)
# ---------------------------------------------------------------------------
CACHE_DIR_NAME = ".cache"
REPO_CACHE_DIR_NAME = ".repo_cache"
SIZE_DIFF_TOLERANCE = 2

GIT_LOG_FILE_NAME = "git_log.txt"


class TargetRemote(Enum):
    ROOT = auto()
    FILE = auto()
    SKIP = auto()
    SUBDIR = auto()


# ---------------------------------------------------------------------------
# GitHub low‑level helpers
# ---------------------------------------------------------------------------
def github_api_headers() -> dict[str, str]:
    hdr = {"Accept": "application/vnd.github.v3+json"}
    if GITHUB_TOKEN:
        hdr["Authorization"] = f"token {GITHUB_TOKEN}"
    return hdr


def get_github_repo_info(github_url: str) -> tuple[str | None, str | None]:
    m = re.match(r"https://github\.com/([^/]+)/([^/]+)", github_url)
    return (m.group(1), m.group(2)) if m else (None, None)


def list_github_files(
    owner: str, repo: str, path: str = "", delay_sec: float = 0
) -> Dict[str, dict]:
    """
    Recursively list all files in a GitHub repo directory using the GitHub API.
    Returns a dictionary keyed by the full path of each file.
    """
    results: Dict[str, dict] = {}
    page = 1
    per_page = 100

    while True:
        if delay_sec:
            time.sleep(delay_sec)

        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
        resp = requests.get(
            url,
            headers=github_api_headers(),
            params={"per_page": per_page, "page": page},
        )

        if resp.status_code != 200:
            raise Exception(f"GitHub API error {resp.status_code}: {resp.text}")

        items = resp.json()
        if not isinstance(items, list):
            break

        for item in items:
            item_type = item.get("type")
            if item_type == "file":
                results[item["path"]] = item
            elif item_type == "dir":
                sub_results = list_github_files(owner, repo, item["path"], delay_sec)
                results.update(sub_results)

        if len(items) < per_page:
            break

        page += 1

    return results


# ---------------------------------------------------------------------------
# Repo‑tree cache / traversal
# ---------------------------------------------------------------------------
_REPO_TREE_CACHE: dict[tuple[str, str], dict[str, dict]] = {}


def _fetch_repo_tree(owner: str, repo: str, delay_sec: float = 0) -> dict[str, dict]:
    if (owner, repo) in _REPO_TREE_CACHE:
        return _REPO_TREE_CACHE[(owner, repo)]
    if delay_sec:
        time.sleep(delay_sec)

    # default branch
    repo_resp = requests.get(
        f"https://api.github.com/repos/{owner}/{repo}", headers=github_api_headers()
    )
    if repo_resp.status_code != 200:
        logger.warning(f"Repo info fetch failed: {owner}/{repo}")
        return {}

    default_branch = repo_resp.json()["default_branch"]
    # recursive=1 → recursion enabled (i.e., “true”)
    tree_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{default_branch}?recursive=1"
    tree_resp = requests.get(tree_url, headers=github_api_headers())
    if tree_resp.status_code != 200:
        logger.warning(f"Tree fetch failed: {owner}/{repo}")
        return {}

    tree_items = {
        itm["path"]: {
            "size": itm.get("size", 0),
            "sha": itm.get("sha"),  # keep blob SHA for later comparison
        }
        for itm in tree_resp.json().get("tree", [])
        if itm["type"] == "blob"
    }
    _REPO_TREE_CACHE[(owner, repo)] = tree_items
    return tree_items


def list_all_files_in_repo(
    owner: str,
    repo: str,
    sub_path: str = "",
    delay_sec: float = 0,
    *,
    return_relative: bool = False,
    filter_substring: str = "",
) -> dict[str, dict]:
    full_tree = _fetch_repo_tree(owner, repo, delay_sec)
    if not full_tree:
        return {}

    sub_path, filter_substring = sub_path.strip("/"), filter_substring.strip()
    result: dict[str, dict] = {}

    for full_path, meta in full_tree.items():
        parent_dir = str(Path(full_path).parent).replace("\\", "/")
        if sub_path and sub_path not in parent_dir:
            continue
        if filter_substring and filter_substring not in full_path:
            continue

        if return_relative:
            rel_key = str(Path(full_path).relative_to(sub_path)) if sub_path and Path(full_path).is_relative_to(sub_path) else full_path
        else:
            rel_key = Path(full_path).name
        rel_key = str(rel_key).replace("\\", "/")
        result[rel_key] = meta
    return result


# ---------------------------------------------------------------------------
# Misc small helpers
# ---------------------------------------------------------------------------


def normalize_target_remote_path(value: str | None) -> TargetRemote:
    """
    Convert the *target_remote_path* CSV column into a TargetRemote enum:

        "" / "root"  -> TargetRemote.ROOT
        "file"       -> TargetRemote.FILE
        "skip"       -> TargetRemote.SKIP
        anything else-> TargetRemote.SUBDIR
    """
    v = (value or "").strip().lower()
    if v in {"", "root"}:
        return TargetRemote.ROOT
    if v == "file":
        return TargetRemote.FILE
    if v == "skip":
        return TargetRemote.SKIP
    return TargetRemote.SUBDIR


def safe_join(base: Path, rel: str) -> Path:
    """Join *base* with *rel* while stripping trailing blanks of each part."""
    cleaned_parts = [p.rstrip() for p in Path(rel).parts]
    return base.joinpath(*cleaned_parts)


def find_partial_match_key(remote_root: dict, rel_path_str: str) -> str | None:
    for key in remote_root:
        if rel_path_str in key:
            return key
    return None


# ---------------------------------------------------------------------------
# DONOTCMP helpers
# ---------------------------------------------------------------------------
def _has_donotcmp(path: Path) -> bool:
    """
    True if *path* or any parent directory contains a **DONOTCMP** marker.
    """
    for p in [path] + list(path.parents):
        if (p / DONOTCMP_MARKER).exists():
            return True
    return False


def is_ignored(path: Path) -> bool:
    # Ignore everything that sits below a DONOTCMP marker
    if _has_donotcmp(path):
        return True
    if path.name.lower() == README_APP_MD:
        return True
    return path.suffix.lower() in IGNORE_EXTS


def iter_categories(root: Path):
    for cat in root.iterdir():
        if cat.is_dir():
            yield cat


# ---------------------------------------------------------------------------
# Manipulate‑files helpers
# ---------------------------------------------------------------------------
def delete_non_doc_files(dir_path: Path):
    """Remove everything below *dir_path* except
    • markdown files, *.url
    • anything inside a directory that carries a **DONOTCMP** marker.
    """
    for item in dir_path.glob("**/*"):
        # Skip content guarded by DONOTCMP
        if _has_donotcmp(item):
            continue
        if item.is_file():
            if is_ignored(item):
                continue
            item.unlink()
        elif item.is_dir():
            try:
                item.rmdir()
            except OSError:
                pass


def copy_cached_file(
    src_file: Path, # src_file is a placeholder
    cache_root: Path,
    project_path: Path,
    repo_cache_proj: Path | None,
):
    rel_path = src_file.relative_to(cache_root)
    dest_path = project_path / rel_path
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    if src_file.stat().st_size == 0:
        if repo_cache_proj is not None:
            candidates = []
            rel_str = str(rel_path).replace("\\", "/")
            candidates.append(repo_cache_proj / rel_str)
            
            for candidate in candidates:
                if candidate.exists() and candidate.is_file():
                    copy2(candidate, dest_path)
                    logger.info(f"Copied real file from repo cache: {candidate} -> {dest_path}")
                    break
        # else:
        #     dest_path.write_bytes(b"")
        #     logger.info(f"Zero-byte placeholder left for {dest_path}")
    else:
        copy2(src_file, dest_path)
        logger.info(f"Copied {src_file} -> {dest_path}")
    logger.info(f"Copied {dest_path}")


def index_projects(root_dir: str | Path, output_csv: str | Path):
    """
    Walk the workspace and create *git_cmp_index.csv* with columns:
    project_name, github_url, target_remote_path, allow_delete.
    """
    projects: list[dict[str, str]] = []
    for category in Path(root_dir).iterdir():
        if not category.is_dir():
            continue
        logger.info(f"Scanning category: {category.name}")
        for project in category.iterdir():
            if not project.is_dir():
                continue
            readme = project / "README.md"
            if not readme.exists():
                logger.info(f"Skipping - no README.md: {project.name}")
                continue
            files = [f for f in project.iterdir() if f.is_file()]
            dirs = [d for d in project.iterdir() if d.is_dir()]
            if (
                not dirs
                and files
                and all(is_ignored(f) or f.name.lower() == "readme.md" for f in files)
            ):
                logger.info(f"Skipping docs-only project: {project.name}")
                continue
            with open(readme, encoding="utf-8") as fh:
                m = re.search(r"https://github\.com/[\w\-/]+", fh.read())
            if m:
                projects.append(
                    dict(
                        project_name=project.name,
                        github_url=m.group(0),
                        target_remote_path="",
                        allow_delete="",
                    )
                )
                logger.info(f"Indexed project: {project.name}")
    with open(output_csv, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "project_name",
                "github_url",
                "target_remote_path",
                "allow_delete",
            ],
        )
        writer.writeheader()
        writer.writerows(projects)
    logger.info(f"Wrote index CSV → {output_csv}")


# ---------------------------------------------------------------------------
# Remote‑path filter (consumed by git_cmp.py)
# ---------------------------------------------------------------------------
def remote_is_skipped(local_root: Path, rel_path: str) -> bool:
    """
    Return True when a remote file *rel_path* should be ignored because the
    LOCAL project already contains a DONOTCMP marker somewhere above it or
    because the file would be ignored anyway (.url / readme.app.md).
    """
    parts = Path(rel_path).parts
    acc = Path()
    for part in parts[:-1]:
        acc /= part
        if (local_root / acc / DONOTCMP_MARKER).exists():
            return True
    p = Path(rel_path)
    return p.name.lower() == README_APP_MD or p.suffix.lower() in IGNORE_EXTS


# ---------------------------------------------------------------------------
# local helper to calculate a Git‑blob SHA1 identical to `git hash-object`
# ---------------------------------------------------------------------------
def calc_git_blob_sha(file_path: Path) -> str:
    """
    Return the Git-blob SHA1 of a file (same as `git hash-object <file>`).
    """
    data = file_path.read_bytes()
    header = f"blob {len(data)}\0".encode()
    return hashlib.sha1(header + data).hexdigest()
