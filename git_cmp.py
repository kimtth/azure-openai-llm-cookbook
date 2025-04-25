import os
import csv
import sys
import requests
import shutil
import subprocess
from pathlib import Path
from loguru import logger
from git_cmp_helper import (
    TargetRemote,
    find_partial_match_key,
    normalize_target_remote_path,
    is_ignored,
    safe_join,
    remote_is_skipped,
    iter_categories,
    github_api_headers,
    get_github_repo_info,
    list_all_files_in_repo,
    delete_non_doc_files,
    copy_cached_file,
    index_projects,
    calc_git_blob_sha,
    CACHE_DIR_NAME,
    REPO_CACHE_DIR_NAME,
    SIZE_DIFF_TOLERANCE,
    DELETE_VALUE,
    GIT_LOG_FILE_NAME,
)

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")  # Optional: for higher rate limits

# --- logging to file --------------------------------------------------------
logger.remove()
logger.add(GIT_LOG_FILE_NAME, level="INFO", encoding="utf-8", mode="a")
# ---------------------------------------------------------------------------

# Remote-repo helpers
# ---------------------------------------------------------------------------


def find_local_project_path(root_dir, project_name):
    """
    Find the local path of a project in the directory structure.
    Returns the path object if found, None otherwise.
    """
    for category in Path(root_dir).iterdir():
        if not category.is_dir():
            continue
        candidate = category / project_name
        if candidate.exists():
            return candidate
    return None


# ---------------------------------------------------------------------------
# Compare-helpers
# ---------------------------------------------------------------------------


def _init_stats(project_name: str, github_url: str, target_path: str) -> dict:
    """Return a fresh statistics dict used by _compare_project."""
    return {
        "project_name": project_name,
        "github_url": github_url,
        "target_remote_path": target_path,
        "compared_files": 0,
        "changed_files": 0,
        "local_only_files": 0,
        "remote_only_files": 0,
        "total_local_files": 0,
        "total_remote_files": 0,
        "extra_info": "",
    }


def _update_stats(
    stats: dict,
    *,
    compared: int = 0,
    changed: int = 0,
    local_only: int = 0,
    remote_only: int = 0,
    total_local: int | None = None,
    total_remote: int | None = None,
    extra: str = "",
):
    """Lightweight helper to fill the repetitive stats fields."""
    stats["compared_files"] = compared
    stats["changed_files"] = changed
    stats["local_only_files"] = local_only
    stats["remote_only_files"] = remote_only
    if total_local is not None:
        stats["total_local_files"] = total_local
    if total_remote is not None:
        stats["total_remote_files"] = total_remote
    stats["extra_info"] = extra


def _compare_project(
    row: dict[str, str],
    root_path: Path,
    cache_dir: Path,
    delay_sec: float,
) -> tuple[dict, bool]:
    """
    Process ONE row (project) from the index CSV file and decide whether the
    local copy is in-sync with the corresponding GitHub repo.

    Steps performed:
    1.  Extract fields from CSV row (project_name, github_url …).
    2.  Derive helper values (category, TargetRemote-kind, paths …).
    3.  Abort early for SKIP flag / invalid URL / missing folders.
    4.  Depending on TargetRemote-kind run a dedicated comparison branch:
        • FILE   - compare only top-level files (Jupyter notebooks etc.).
        • ROOT   - compare entire project tree to repo root.
        • SUBDIR - compare a specific sub-directory.
    5.  When differences are found create a mirror of the local files inside
        .cache/<category>/<project> so that later steps can act on them.
    6.  Assemble a `stats` dict for reporting and return it together with a
        boolean indicating “needs update”.
    """
    # --- unpack & pre-checks ----------------------------------------------#
    project_name = row["project_name"]
    github_url = row["github_url"]
    target_path = row.get("target_remote_path", "").strip()
    kind = normalize_target_remote_path(target_path)

    logger.info(
        f"Processing - project: {project_name} | target_remote_path={target_path}"
    )

    category_name = next(  # find category
        (
            cat.name
            for cat in iter_categories(root_path)
            if (cat / project_name).exists()
        ),
        None,
    )

    if kind is TargetRemote.SKIP:
        logger.info(f"Skipping project (target_remote_path=skip): {project_name}")
        return {}, False

    local_project = find_local_project_path(root_path, project_name)
    if not local_project:
        logger.warning(f"Local project not found: {project_name}")
        return {}, False

    owner, repo = get_github_repo_info(github_url)
    if not owner:
        logger.warning(f"Invalid GitHub URL: {github_url}")
        return {}, False

    file_diff = False
    stats = _init_stats(project_name, github_url, target_path)

    # ----------------------------------------------------------------------#
    # Select comparison strategy based on `kind`.  Each branch updates
    # `stats` and toggles `file_diff` when mismatches are discovered.
    # ----------------------------------------------------------------------#
    if kind is TargetRemote.FILE:
        # --- MODE: compare individual files in project root -------------- #
        local_files = [
            f for f in local_project.iterdir() if f.is_file() and not is_ignored(f)
        ]
        # --- compare locals vs remotes ------------------------------
        remote_root = list_all_files_in_repo(
            owner,
            repo,
            delay_sec=delay_sec,
            return_relative=True,
        )
        stats["total_remote_files"] = len(remote_root)
        changed_files = compared_files = local_only = 0
        changed_set: set[str] = set()
        for local_file in local_files:
            rel_path = local_file.relative_to(local_project)
            rel_path_str = str(rel_path).replace("\\", "/")

            # use full relative path for look-up
            if not any(rel_path_str in key for key in remote_root):
                logger.info(f"File missing remotely: {rel_path_str}")
                file_diff = True
                changed_files += 1
                local_only += 1
                continue

            local_size = local_file.stat().st_size
            rel_path_str = (
                find_partial_match_key(remote_root, rel_path_str) or rel_path_str
            )
            remote_meta = remote_root[rel_path_str]
            remote_size = remote_meta.get("size", 0)
            remote_sha = remote_meta.get("sha")
            compared_files += 1
            sha_mismatch = remote_sha and calc_git_blob_sha(local_file) != remote_sha
            if abs(local_size - remote_size) > SIZE_DIFF_TOLERANCE or sha_mismatch:
                logger.info(
                    f"File differs: {rel_path_str} "
                    f"(local size: {local_size}, remote size: {remote_size}, "
                    f"sha mismatch: {sha_mismatch})"
                )
                file_diff = True
                changed_files += 1
                changed_set.add(rel_path_str)

        local_file_names = {
            str(f.relative_to(local_project)).replace("\\", "/") for f in local_files
        }
        remote_file_names = set(remote_root.keys())
        extra_remote = remote_file_names - local_file_names

        # updated stats to include remote-only
        _update_stats(
            stats,
            compared=compared_files,
            changed=changed_files,
            local_only=local_only,
            remote_only=len(extra_remote),
            total_local=len(local_files),
            total_remote=len(remote_root),
            extra=(
                f"Local files: {len(local_files)}, Remote files: {len(remote_root)}, "
                f"Extra remote files: {len(extra_remote)}"
            ),
        )

        if file_diff:
            cache_proj = cache_dir / (category_name or "unknown") / project_name
            cache_proj.mkdir(parents=True, exist_ok=True)
            # placeholders for changed files
            for rel in changed_set:
                dest_path = safe_join(cache_proj, rel)
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                with open(dest_path, "w", encoding="utf-8"):
                    pass
            if any(cache_proj.glob("**/*")):
                return stats, True
            else:
                logger.warning(f"Cache not created for {project_name}")
                return stats, False

    elif kind is TargetRemote.ROOT:
        # --- MODE: compare full project tree against repo root ----------- #
        local_files = [
            f for f in local_project.glob("**/*") if f.is_file() and not is_ignored(f)
        ]
        stats["total_local_files"] = len(local_files)
        if not local_files:
            logger.info(f"No files to compare for project: {project_name}")
            # Copy all remote files to .cache as placeholders
            # NOTE: we only create **zero-byte** files that mirror the remote
            # directory structure here.  The real content (or updates) is
            # pulled later by `manipulate_local_files`, which replaces each
            # placeholder with the actual file fetched from the repo clone /
            # remote repository.
            remote_root = list_all_files_in_repo(
                owner,
                repo,
                delay_sec=delay_sec,
                return_relative=True,
            )
            cache_proj = cache_dir / (category_name or "unknown") / project_name
            if not cache_proj.exists():
                cache_proj.mkdir(parents=True, exist_ok=True)
            for rel_path in remote_root:
                dest_path = safe_join(cache_proj, rel_path)  # ← helper
                # Ensure all parent directories exist and strip any trailing spaces in each part
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                with open(dest_path, "w", encoding="utf-8") as pf:
                    pf.write("")
            if any(cache_proj.glob("**/*")):
                return stats, True

            # logging
            _update_stats(
                stats,
                total_local=0,
                total_remote=len(remote_root),
                remote_only=len(remote_root),
                extra=(
                    f"Local files: 0, Remote files: {len(remote_root)}, "
                    f"Extra remote files: {len(remote_root)}"
                ),
            )
            return stats, False

        # --- use relative-path map instead of filename map ---
        remote_root = {
            k: v
            for k, v in list_all_files_in_repo(
                owner, repo, delay_sec=delay_sec, return_relative=True
            ).items()
            if not remote_is_skipped(local_project, k)
        }
        # ------------------------------------------------------
        stats["total_remote_files"] = len(remote_root)
        changed_files = compared_files = local_only = 0
        changed_set = set()
        for local_file in local_files:
            rel_path = local_file.relative_to(local_project)
            rel_path_str = str(rel_path).replace("\\", "/")

            # use full relative path for look-up
            if not any(rel_path_str in key for key in remote_root):
                logger.info(f"File missing remotely: {rel_path_str}")
                file_diff = True
                changed_files += 1
                local_only += 1
                continue

            local_size = local_file.stat().st_size
            remote_meta = remote_root[rel_path_str]
            remote_size = remote_meta.get("size", 0)
            remote_sha = remote_meta.get("sha")
            compared_files += 1
            sha_mismatch = remote_sha and calc_git_blob_sha(local_file) != remote_sha
            if abs(local_size - remote_size) > SIZE_DIFF_TOLERANCE or sha_mismatch:
                logger.info(
                    f"File differs: {rel_path_str} "
                    f"(local size: {local_size}, remote size: {remote_size}, "
                    f"sha mismatch: {sha_mismatch})"
                )
                file_diff = True
                changed_files += 1
                changed_set.add(rel_path_str)

        local_file_names = set(
            str(f.relative_to(local_project)).replace("\\", "/") for f in local_files
        )
        remote_file_names = set(remote_root.keys())
        extra_remote_files = {
            p
            for p in (remote_file_names - local_file_names)
            if not remote_is_skipped(local_project, p)
        }

        # logging
        _update_stats(
            stats,
            compared=compared_files,
            changed=changed_files,
            local_only=local_only,
            remote_only=len(extra_remote_files),
            total_local=len(local_files),
            total_remote=len(remote_root),
            extra=(
                f"Local files: {len(local_files)}, "
                f"Remote files: {len(remote_root)}, "
                f"Extra remote files: {len(extra_remote_files)}"
            ),
        )

        if extra_remote_files:
            logger.info(f"Extra files in remote: {len(extra_remote_files)}")
            file_diff = True

        if file_diff:
            # --- use category in cache path ---
            cache_proj = cache_dir / (category_name or "unknown") / project_name
            cache_proj.mkdir(parents=True, exist_ok=True)
            # placeholders for files that differ
            for rel in changed_set:
                dest_path = safe_join(cache_proj, rel)  # ← use helper
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                with open(dest_path, "w", encoding="utf-8"):
                    pass
            # add placeholders for REMOTE‑only files
            for extra_rel in extra_remote_files:
                dest_path = safe_join(cache_proj, extra_rel)
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                with open(dest_path, "w", encoding="utf-8"):
                    pass
            # Only add to needs_update if files were actually copied to cache
            if any(cache_proj.glob("**/*")):
                return stats, True
            else:
                logger.warning(f"Cache not created for {project_name}")

    elif kind is TargetRemote.SKIP:
        logger.info(f"Skipping project (target_remote_path=skip): {project_name}")
        return {}, False

    else:  # TargetRemote.SUBDIR
        # --- MODE: compare a specific subdirectory ----------------------- #
        # Remote path to inspect: <target_remote_path>
        remote_sub_path = target_path.strip("/")
        local_dir = local_project / remote_sub_path
        # Always check for remote-only files even if local_dir is empty/absent
        local_files = [
            f for f in local_dir.glob("**/*") if f.is_file() and not is_ignored(f)
        ]
        stats["total_local_files"] = len(local_files)

        remote_file_directory = {
            k: v
            for k, v in list_all_files_in_repo(
                owner, repo, remote_sub_path, delay_sec=delay_sec, return_relative=True
            ).items()
            if not remote_is_skipped(local_dir, k)
        }
        # Always check for remote-only files even if local_dir is empty/absent
        stats["total_remote_files"] = len(remote_file_directory)

        changed_files = compared_files = local_only = 0
        remote_only_set = set(remote_file_directory.keys())
        changed_set = set()

        # Compare local files to remote
        for local_file in local_files:
            rel_path = local_file.relative_to(local_dir)
            rel_path_str = str(rel_path).replace("\\", "/")
            if not any(rel_path_str in key for key in remote_file_directory):
                logger.info(f"File missing remotely: {remote_sub_path}/{rel_path_str}")
                file_diff = True
                changed_files += 1
                local_only += 1
                continue
            local_size = local_file.stat().st_size
            rel_path_str = (
                find_partial_match_key(remote_file_directory, rel_path_str)
                or rel_path_str
            )
            remote_meta = remote_file_directory[rel_path_str]
            remote_size = remote_meta.get("size", 0)
            remote_sha = remote_meta.get("sha")
            compared_files += 1
            sha_mismatch = remote_sha and calc_git_blob_sha(local_file) != remote_sha
            if abs(local_size - remote_size) > SIZE_DIFF_TOLERANCE or sha_mismatch:
                logger.info(
                    f"File differs: {remote_sub_path}/{rel_path_str} "
                    f"(local size: {local_size}, remote size: {remote_size}, "
                    f"sha mismatch: {sha_mismatch})"
                )
                file_diff = True
                changed_files += 1
                changed_set.add(rel_path_str)
                remote_only_set.discard(rel_path_str)
            else:
                remote_only_set.discard(rel_path_str)

        # If there are remote-only files, mark as needing update
        if remote_only_set:
            logger.info(f"Extra files in remote: {len(remote_only_set)}")
            file_diff = True

        # logging
        _update_stats(
            stats,
            compared=compared_files,
            changed=changed_files,
            local_only=local_only,
            remote_only=len(remote_only_set),
            total_local=len(local_files),
            total_remote=len(remote_file_directory),
            extra=(
                f"Local files: {len(local_files)}, "
                f"Remote files: {len(remote_file_directory)}, "
                f"Extra remote files: {len(remote_only_set)}"
            ),
        )

        if file_diff:
            # --- use category in cache path ---
            cache_proj = (
                cache_dir
                / (category_name or "unknown")
                / project_name
                / remote_sub_path
            )
            cache_proj.mkdir(parents=True, exist_ok=True)
            # placeholders for files that differ
            for rel in changed_set:
                dest_path = safe_join(cache_proj, rel)  # ← use helper
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                with open(dest_path, "w", encoding="utf-8"):
                    pass
            # add placeholders for REMOTE‑only files
            for extra_rel in remote_only_set:
                dest_path = safe_join(cache_proj, extra_rel)
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                with open(dest_path, "w", encoding="utf-8"):
                    pass
            if any(cache_proj.glob("**/*")):
                return stats, True
            logger.warning(f"Cache not created for {project_name}")

    logger.info(
        f"Processing completed - project: {project_name} | target_remote_path={target_path}"
    )
    # Hand back the summary for this project
    return stats, file_diff


def compare_projects(csv_path, root_dir, report_path, update_csv_path, delay_sec=0):
    """
    Orchestrate the full comparison workflow.

    • Cleans/creates the .cache directory.
    • Iterates through the index CSV and delegates per-project work to
      `_compare_project`.
    • Collects statistics and builds two lists:
        - needs_update : projects with detected differences
        - up_to_date   : projects already in sync
    • Finally writes a human-readable report + a CSV for next steps.
    """
    needs_update, up_to_date, project_stats = [], [], []
    cache_dir = Path(root_dir) / CACHE_DIR_NAME
    root_path = Path(root_dir)

    if cache_dir.exists():
        shutil.rmtree(cache_dir)
    cache_dir.mkdir(exist_ok=True)

    with open(csv_path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            stats, diff = _compare_project(row, root_path, cache_dir, delay_sec)
            if not stats:  # skipped / invalid
                continue
            project_stats.append(stats)

            entry = {
                "project_name": row["project_name"],
                "github_url": row["github_url"],
                "target_remote_path": row.get("target_remote_path", "").strip(),
            }
            (needs_update if diff else up_to_date).append(entry)

    # delegate report writing ↓
    write_report_and_update_csv(
        report_path,
        needs_update,
        up_to_date,
        update_csv_path,
        project_stats,
        index_csv_path=csv_path,
    )


def write_report_and_update_csv(
    report_path,
    needs_update,
    up_to_date,
    update_csv_path,
    project_stats=None,
    index_csv_path=None,
):
    """
    Write the report and needs_update CSV, with detailed stats if provided.
    Copy allow_delete column from index CSV if available.
    """
    # --- Load allow_delete from index CSV if available ---
    allow_delete_map = {}
    if index_csv_path and os.path.exists(index_csv_path):
        with open(index_csv_path, encoding="utf-8") as idxf:
            idx_reader = csv.DictReader(idxf)
            for row in idx_reader:
                allow_delete_map[row["project_name"]] = row.get("allow_delete", "")

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("Projects needing updates:\n")
        for p in needs_update:
            f.write(
                f"- {p['project_name']} ({p['github_url']}) "
                f"[target_remote_path={p['target_remote_path']}] "
                f"-> local need to update\n"
            )
            # Add stats if available
            if project_stats:
                stat = next(
                    (
                        s
                        for s in project_stats
                        if s["project_name"] == p["project_name"]
                    ),
                    None,
                )
                if stat:
                    f.write(
                        f"    Compared files: {stat['compared_files']}\n"
                        f"    Changed files: {stat['changed_files']}\n"
                        f"    Local only files: {stat['local_only_files']}\n"
                        f"    Remote only files: {stat['remote_only_files']}\n"
                        f"    Total local files: {stat['total_local_files']}\n"
                        f"    Total remote files: {stat['total_remote_files']}\n"
                        f"    Extra info: {stat['extra_info']}\n"
                    )
        f.write("\nProjects up-to-date:\n")
        for p in up_to_date:
            f.write(
                f"- {p['project_name']} ({p['github_url']}) "
                f"[target_remote_path={p['target_remote_path']}] "
                f"-> project up-to-date\n"
            )
            # Add stats if available
            if project_stats:
                stat = next(
                    (
                        s
                        for s in project_stats
                        if s["project_name"] == p["project_name"]
                    ),
                    None,
                )
                if stat:
                    f.write(
                        f"    Compared files: {stat['compared_files']}\n"
                        f"    Changed files: {stat['changed_files']}\n"
                        f"    Local only files: {stat['local_only_files']}\n"
                        f"    Remote only files: {stat['remote_only_files']}\n"
                        f"    Total local files: {stat['total_local_files']}\n"
                        f"    Total remote files: {stat['total_remote_files']}\n"
                        f"    Extra info: {stat['extra_info']}\n"
                    )

    logger.info(f"Report written to {report_path}")
    # Write needs_update CSV with allow_delete column
    with open(update_csv_path, "w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "project_name",
            "github_url",
            "target_remote_path",
            "allow_delete",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for p in needs_update:
            row = dict(p)
            row["allow_delete"] = allow_delete_map.get(p["project_name"], "")
            writer.writerow(row)
    logger.info(f"Needs-update CSV written to {update_csv_path}")


def manipulate_local_files(update_csv_path, root_dir):
    """
    Synchronise workspace with contents prepared in .cache.

    Workflow overview
    1.  Read the *git_cmp_needs_update.csv* produced by `compare_projects`.
    2.  For each row:
        a. Ensure a shallow clone of the referenced repo exists (cached).
        b. Find the matching .cache/<category>/<project> directory.
        c. If `allow_delete == 'DELETE'` remove all non-doc files locally.
        d. Copy (or replace) every file from cache into the real project
           directory, expanding 0-byte placeholders by pulling real content
           from the shallow clone when possible.
    3.  After completion the workspace reflects the remote repositories for
        all flagged projects.
    """
    cache_dir = Path(root_dir) / CACHE_DIR_NAME
    repo_cache_dir = Path(root_dir) / REPO_CACHE_DIR_NAME
    repo_cache_dir.mkdir(exist_ok=True)

    default_branch_cache: dict[tuple[str, str], str] = {}
    repo_clone_cache: dict[tuple[str, str, str], Path | None] = {}

    with open(update_csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            project_name = row["project_name"]
            github_url = row["github_url"]
            # target_remote = row.get("target_remote_path", "").strip()
            # build full remote path when SUBDIR is used
            # kind = normalize_target_remote_path(target_remote)
            allow_delete_flag = row.get("allow_delete", "").strip().upper()

            owner, repo = get_github_repo_info(github_url)
            if not owner:
                logger.warning(f"Invalid GitHub URL: {github_url}")
                continue

            # --- get default branch (cached) --------------------------------
            if (owner, repo) not in default_branch_cache:
                repo_json = requests.get(
                    f"https://api.github.com/repos/{owner}/{repo}",
                    headers=github_api_headers(),
                ).json()
                default_branch_cache[(owner, repo)] = repo_json.get(
                    "default_branch", "main"
                )
            branch = default_branch_cache[(owner, repo)]

            # --- shallow clone once per repo/branch -------------------------
            repo_key = (owner, repo, branch)
            if repo_key not in repo_clone_cache:
                local_repo = repo_cache_dir / f"{owner}__{repo}__{branch}"
                if not local_repo.exists():
                    # Clone with --no-checkout to avoid checkout errors on Windows
                    result = subprocess.run(
                        [
                            "git",
                            "clone",
                            "--depth",
                            "1",
                            "--branch",
                            branch,
                            "--no-checkout",
                            f"https://github.com/{owner}/{repo}.git",
                            str(local_repo),
                        ],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        check=False,
                    )
                    if result.returncode == 0:
                        # Try to checkout, but ignore errors due to invalid paths
                        checkout_result = subprocess.run(
                            ["git", "checkout", branch],
                            cwd=str(local_repo),
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            check=False,
                        )
                        if checkout_result.returncode != 0:
                            logger.warning(
                                f"Checkout failed for {owner}/{repo} (branch: {branch}): "
                                f"{checkout_result.stderr.decode()}"
                            )

                    if result.returncode != 0:
                        logger.error(
                            f"Error cloning repo {owner}/{repo} (branch: {branch}) "
                            f"Error: {result.stderr.decode()}"
                        )
                        continue

                repo_clone_cache[repo_key] = local_repo if local_repo.exists() else None
            repo_cache_proj = repo_clone_cache[repo_key]
            # ----------------------------------------------------------------

            # locate category and local project folder
            category = next(
                (
                    c
                    for c in Path(root_dir).iterdir()
                    if c.is_dir() and (c / project_name).exists()
                ),
                None,
            )
            cache_proj = (
                cache_dir / (category.name if category else "unknown") / project_name
            )
            if not cache_proj.exists():
                logger.warning(f"No cache for {project_name}")
                continue

            project_path = category / project_name if category else None

            # create folder if missing
            if project_path is None or not project_path.exists():
                project_path = (category or Path(root_dir)) / project_name
                project_path.mkdir(parents=True, exist_ok=True)

            # remote repo is the source of truth → wipe local (honours DONOTCMP)
            if allow_delete_flag == DELETE_VALUE:
                delete_non_doc_files(project_path)

            # sync cache -> project
            for src in cache_proj.glob("**/*"):
                if src.is_file():
                    # At this stage `src` might be the placeholder created
                    # during the compare step.  `_copy_cached_file` will
                    # detect zero-byte placeholders and try to replace them
                    # with the real remote content before copying.
                    copy_cached_file(
                        src,
                        cache_proj,
                        project_path,
                        repo_cache_proj
                    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--index", action="store_true", help="Index projects and write CSV"
    )
    parser.add_argument(
        "--compare", action="store_true", help="Compare projects and write report"
    )
    parser.add_argument(
        "--manipulate",
        action="store_true",
        help="Manipulate local files based on update CSV",
    )
    parser.add_argument("--root", type=str, default=".", help="Root directory")
    parser.add_argument(
        "--csv", type=str, default="git_cmp_index.csv", help="CSV file path"
    )
    parser.add_argument(
        "--report", type=str, default="git_cmp_report.txt", help="Report file path"
    )
    parser.add_argument(
        "--update_csv",
        type=str,
        default="git_cmp_needs_update.csv",
        help="Needs-update CSV file path",
    )
    parser.add_argument(
        "--delay_sec",
        type=float,
        default=1,
        help="Delay (seconds) between GitHub API calls",
    )
    parser.add_argument(
        "--delete_cache",
        action="store_true",
        help="Delete .cache and .repo_cache directories and exit",
    )
    args = parser.parse_args()

    # args.index = True
    # args.compare = True
    args.manipulate = True
    # args.delete_cache = True
    # args.csv = "git_cmp_index_incremental.csv"

    if args.index:
        index_projects(args.root, args.csv)
    elif args.compare:
        compare_projects(
            args.csv, args.root, args.report, args.update_csv, delay_sec=args.delay_sec
        )
    elif args.manipulate:
        manipulate_local_files(args.update_csv, args.root)
        if args.delete_cache:
            cache_dir = Path(args.root) / CACHE_DIR_NAME
            repo_cache_dir = Path(args.root) / REPO_CACHE_DIR_NAME
            if cache_dir.exists():
                shutil.rmtree(cache_dir)
                logger.info(f"Deleted cache directory {cache_dir}")
            if repo_cache_dir.exists():
                shutil.rmtree(repo_cache_dir)
                logger.info(f"Deleted repo cache directory {repo_cache_dir}")
            print("Cache directories deleted.")
            sys.exit(0)
    else:
        print("Specify --index or --compare or --manipulate")
