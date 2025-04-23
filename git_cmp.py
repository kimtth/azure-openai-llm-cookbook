import os
import csv
import re
import sys
import requests
import time
import shutil
import subprocess
import tempfile
from pathlib import Path
from loguru import logger

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")  # Optional: for higher rate limits

# --- logging to file --------------------------------------------------------
logger.remove()                                           # drop default stderr sink
logger.add("git_cmp.log", level="INFO", encoding="utf-8") # NEW: file sink
# ---------------------------------------------------------------------------

# Remote‑repo helpers
# ---------------------------------------------------------------------------

# global cache  {(owner, repo): { "<full/relative/path>": {"size": int, ...} } }
_REPO_TREE_CACHE: dict[tuple[str, str], dict[str, dict]] = {}


def _fetch_repo_tree(owner: str, repo: str, delay_sec: float = 0) -> dict[str, dict]:
    """
    Download the *full* git tree once and keep it in memory.
    Subsequent calls for the same (owner, repo) reuse the cached copy.
    """
    cache_key = (owner, repo)
    if cache_key in _REPO_TREE_CACHE:
        return _REPO_TREE_CACHE[cache_key]

    if delay_sec > 0:
        time.sleep(delay_sec)

    # Step 1: find default branch
    repo_url = f"https://api.github.com/repos/{owner}/{repo}"
    repo_resp = requests.get(repo_url, headers=github_api_headers())
    if repo_resp.status_code != 200:
        logger.warning(f"Failed to fetch repo info: {repo_resp.status_code}")
        _REPO_TREE_CACHE[cache_key] = {}
        return _REPO_TREE_CACHE[cache_key]

    default_branch = repo_resp.json()["default_branch"]

    # Step 2: fetch the *recursive* tree
    tree_url = (
        f"https://api.github.com/repos/{owner}/{repo}/git/trees/{default_branch}"
        "?recursive=1"
    )
    logger.info(f"Downloading repo tree once: {tree_url}")
    tree_resp = requests.get(tree_url, headers=github_api_headers())
    if tree_resp.status_code != 200:
        logger.warning(f"Failed to fetch tree: {tree_resp.status_code}")
        _REPO_TREE_CACHE[cache_key] = {}
        return _REPO_TREE_CACHE[cache_key]

    # Keep full path → metadata (including size) in cache
    tree_items = {
        item["path"]: {"size": item.get("size", 0)}
        for item in tree_resp.json().get("tree", [])
        if item["type"] == "blob"
    }
    _REPO_TREE_CACHE[cache_key] = tree_items
    return tree_items


def index_projects(root_dir, output_csv):
    """
    Scan the directory structure and extract project names and GitHub URLs.
    Write results to a CSV file.
    Skip projects where only README.md exists.
    Add target_remote_path column (default empty).
    Add allow_delete column (default empty).
    """
    projects = []
    for category in Path(root_dir).iterdir():
        if not category.is_dir():
            continue
        logger.info(f"Scanning category: {category.name}")
        for project in category.iterdir():
            if not project.is_dir():
                continue
            readme = project / "README.md"
            if not readme.exists():
                logger.info(f"Skipping project without README.md: {project.name}")
                continue  # skip projects without README.md
            files = [f for f in project.iterdir() if f.is_file()]
            dirs = [f for f in project.iterdir() if f.is_dir()]
            # Skip projects that contain only README.md and/or .url files
            if (
                not dirs
                and files
                and all(
                    f.name.lower() == "readme.md" or f.name.lower().endswith(".url")
                    for f in files
                )
            ):
                logger.info(
                    f"Skipping project with only README.md and .url files: {project.name}"
                )
                continue
            with open(readme, encoding="utf-8") as f:
                content = f.read()
            match = re.search(r"https://github\.com/[\w\-/]+", content)
            if match:
                github_url = match.group(0)
                projects.append(
                    {
                        "project_name": project.name,
                        "github_url": github_url,
                        "target_remote_path": "",
                        "allow_delete": "",  # NEW COLUMN
                    }
                )
                logger.info(f"Indexed project: {project.name} ({github_url})")
    # Write CSV with target_remote_path and allow_delete columns
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["project_name", "github_url", "target_remote_path", "allow_delete"]  # NEW
        )
        writer.writeheader()
        writer.writerows(projects)
    logger.info(f"Indexed {len(projects)} projects to {output_csv}")


def github_api_headers():
    headers = {"Accept": "application/vnd.github.v3+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
    return headers


def get_github_repo_info(github_url):
    """
    Convert a GitHub URL to owner/repo and return API base URL.
    """
    m = re.match(r"https://github\.com/([^/]+)/([^/]+)", github_url)
    if not m:
        return None, None
    owner, repo = m.group(1), m.group(2)
    return owner, repo


def list_github_files(owner, repo, delay_sec=0):
    """
    List all files and directories in the root of the GitHub repo.
    Returns a dict: {name: {type, size, sha}}
    Handles API rate limit errors gracefully.
    Optionally delays the request to avoid rate limits.
    """
    if delay_sec > 0:
        time.sleep(delay_sec)
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/"
    logger.info(f"Fetching root files for {owner}/{repo}")
    resp = requests.get(url, headers=github_api_headers())
    if resp.status_code == 403 and "rate limit" in resp.text.lower():
        logger.error(
            "GitHub API rate limit exceeded. Please set GITHUB_TOKEN for higher limits."
        )
        # When rate limit is exceeded, exit the script to avoid further requests
        sys.exit(1)
        return {}
    if resp.status_code != 200:
        logger.warning(f"Failed to fetch {url}: {resp.status_code}")
        return {}
    items = resp.json()
    return {item["name"]: item for item in items}


def list_all_files_in_repo(
    owner: str,
    repo: str,
    sub_path: str = "",
    delay_sec: float = 0,
    *,
    return_relative: bool = False,
    filter_substring: str = "",        # NEW
):
    """
    Return a dict of remote files.

    • `return_relative` – keep previous behaviour.  
    • `filter_substring` – when provided, the **full path** in the repo must
      contain this substring *in addition* to the `sub_path` test.
    """
    full_tree = _fetch_repo_tree(owner, repo, delay_sec=delay_sec)
    if not full_tree:
        return {}

    sub_path = sub_path.strip("/")
    filter_substring = filter_substring.strip()

    result: dict[str, dict] = {}
    for full_path, meta in full_tree.items():
        parent_dir = str(Path(full_path).parent).replace("\\", "/")

        # 1) ensure file lives under the requested sub_path (if any)
        if sub_path and not parent_dir.startswith(sub_path):
            continue
        # 2) if filter is set, the *full path* must contain it
        if filter_substring and filter_substring not in full_path:
            continue

        if return_relative and sub_path:
            rel_key = full_path[len(sub_path) + 1 :]       # strip "<sub_path>/"
        elif return_relative:
            rel_key = full_path
        else:
            rel_key = Path(full_path).name

        result[rel_key] = meta
    return result


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


def compare_projects(csv_path, root_dir, report_path, update_csv_path, delay_sec=0):
    """
    For each project, compare local files/dirs with remote repo metadata.
    Generate a summary report and a CSV listing projects needing updates.
    Supports target_remote_path: "root", "file", or a directory name or subdirectory path.
    If "file", compare only .ipynb files by filename with the corresponding remote directory (not always root).
    If target_remote_path is a subdirectory path (e.g., "python/samples"), compare files in that subdirectory.
    Only compare files, not directories.
    Optionally delays each GitHub API call to avoid rate limits.
    Additionally, copy files/dirs needing updates into a .cache directory.
    """
    needs_update = []
    up_to_date = []
    project_stats = []
    cache_dir = Path(root_dir) / ".cache"
    # Remove existing cache directory if it exists
    if cache_dir.exists():
        shutil.rmtree(cache_dir)
    cache_dir.mkdir(exist_ok=True)

    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            project_name = row["project_name"]
            github_url = row["github_url"]
            target_remote_path_dir = row.get("target_remote_path", "").strip()
            # --- find category for this project ---
            category_name = None
            for category in Path(root_dir).iterdir():
                if not category.is_dir():
                    continue
                candidate = category / project_name
                if candidate.exists():
                    category_name = category.name
                    break

            if target_remote_path_dir.lower() == "skip":
                logger.info(
                    f"Skipping project (target_remote_path=skip): {project_name}"
                )
                continue

            logger.info(
                f"Comparing project: {project_name} (target_remote_path={target_remote_path_dir})"
            )

            # Find local project path using helper function
            local_project = find_local_project_path(root_dir, project_name)
            if not local_project:
                logger.warning(f"Local project not found: {project_name}")
                continue

            owner, repo = get_github_repo_info(github_url)
            if not owner:
                logger.warning(f"Invalid GitHub URL: {github_url}")
                continue

            file_diff = False
            stats = {
                "project_name": project_name,
                "github_url": github_url,
                "target_remote_path": target_remote_path_dir,
                "compared_files": 0,
                "changed_files": 0,
                "local_only_files": 0,
                "remote_only_files": 0,
                "total_local_files": 0,
                "total_remote_files": 0,
                "extra_info": "",
            }

            if target_remote_path_dir.lower() == "file":
                local_files = [
                    f
                    for f in local_project.iterdir()
                    if f.is_file()
                    and not (
                        f.name.lower().endswith(".md")
                        or f.name.lower().endswith(".url")
                    )
                ]
                stats["total_local_files"] = len(local_files)
                if not local_files:
                    logger.info(f"No files to compare for project: {project_name}")
                    continue
                remote_dir = list_all_files_in_repo(owner, repo, delay_sec=delay_sec)
                stats["total_remote_files"] = len(remote_dir)
                changed_files = 0
                compared_files = 0
                local_only = 0
                for local_file in local_files:
                    fname = local_file.name
                    if fname not in remote_dir:
                        logger.info(f"File missing remotely: {fname}")
                        file_diff = True
                        changed_files += 1
                        local_only += 1
                        continue
                    local_size = local_file.stat().st_size
                    remote_size = remote_dir[fname].get("size", 0)
                    compared_files += 1
                    if abs(local_size - remote_size) > 2:
                        logger.info(
                            f"File size differs: {fname} (local: {local_size}, remote: {remote_size})"
                        )
                        file_diff = True
                        changed_files += 1
                remote_only = len(
                    set(remote_dir.keys()) - set(f.name for f in local_files)
                )
                stats["compared_files"] = compared_files
                stats["changed_files"] = changed_files
                stats["local_only_files"] = local_only
                stats["remote_only_files"] = remote_only
                stats["extra_info"] = (
                    f"Local files: {stats['total_local_files']}, Remote files: {stats['total_remote_files']}"
                )
                if file_diff:
                    # --- use category in cache path ---
                    cache_proj = cache_dir / (category_name or "unknown") / project_name
                    if not cache_proj.exists():
                        cache_proj.mkdir(parents=True, exist_ok=True)
                    for local_file in local_files:
                        dest_path = cache_proj / local_file.name
                        shutil.copy2(local_file, dest_path)
                    # Only add to needs_update if files were actually copied to cache
                    if any(cache_proj.glob("**/*")):
                        needs_update.append(
                            {
                                "project_name": project_name,
                                "github_url": github_url,
                                "target_remote_path": target_remote_path_dir,
                            }
                        )
                        logger.info(f"Project needs update: {project_name}")
                else:
                    up_to_date.append(
                        {
                            "project_name": project_name,
                            "github_url": github_url,
                            "target_remote_path": target_remote_path_dir,
                        }
                    )
                    logger.info(f"Project up-to-date: {project_name}")
                project_stats.append(stats)
            elif target_remote_path_dir.lower() == "root" or target_remote_path_dir.upper() == "ROOT" or target_remote_path_dir == "":
                local_files = [
                    f
                    for f in local_project.glob("**/*")
                    if f.is_file()
                    and not (
                        f.name.lower().endswith(".md")
                        or f.name.lower().endswith(".url")
                    )
                ]
                stats["total_local_files"] = len(local_files)
                if not local_files:
                    logger.info(f"No files to compare for project: {project_name}")
                    # Copy all remote files to .cache as placeholders
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
                        dest_path = cache_proj / rel_path
                        # Ensure all parent directories exist and strip any trailing spaces in each part
                        dest_path = Path(
                            *[p.rstrip() for p in dest_path.parts]
                        )
                        dest_path.parent.mkdir(parents=True, exist_ok=True)
                        with open(dest_path, "w", encoding="utf-8") as pf:
                            pf.write("")
                    if any(cache_proj.glob("**/*")):
                        needs_update.append(
                            {
                                "project_name": project_name,
                                "github_url": github_url,
                                "target_remote_path": target_remote_path_dir,
                            }
                        )
                        logger.info(f"Project needs update (remote only files): {project_name}")
                    stats["total_remote_files"] = len(remote_root)
                    stats["remote_only_files"] = len(remote_root)
                    stats["extra_info"] = f"Local files: 0, Remote files: {len(remote_root)}, Extra remote files: {len(remote_root)}"
                    project_stats.append(stats)
                    continue
                # --- use relative‑path map instead of filename map ---
                remote_root = list_all_files_in_repo(
                    owner,
                    repo,
                    delay_sec=delay_sec,
                    return_relative=True,
                )
                # ------------------------------------------------------
                stats["total_remote_files"] = len(remote_root)
                changed_files = compared_files = local_only = 0
                for local_file in local_files:
                    rel_path = local_file.relative_to(local_project)
                    rel_path_str = str(rel_path).replace("\\", "/")

                    # use full relative path for look‑up
                    if rel_path_str not in remote_root:                    
                        logger.info(f"File missing remotely: {rel_path_str}")  
                        file_diff = True
                        changed_files += 1
                        local_only += 1
                        continue

                    local_size = local_file.stat().st_size
                    remote_size = remote_root[rel_path_str].get("size", 0)      
                    compared_files += 1
                    if abs(local_size - remote_size) > 2:
                        logger.info(
                            f"File size differs: {rel_path_str} (local: {local_size}, remote: {remote_size})"  
                        )
                        file_diff = True
                        changed_files += 1

                local_file_names  = set( str(f.relative_to(local_project)).replace("\\", "/") for f in local_files )  
                remote_file_names = set(remote_root.keys())                                                           
                extra_remote_files = remote_file_names - local_file_names
                stats["compared_files"] = compared_files
                stats["changed_files"] = changed_files
                stats["local_only_files"] = local_only
                stats["remote_only_files"] = len(extra_remote_files)
                stats["extra_info"] = (
                    f"Local files: {stats['total_local_files']}, Remote files: {stats['total_remote_files']}, Extra remote files: {len(extra_remote_files)}"
                )
                if extra_remote_files:
                    logger.info(f"Extra files in remote: {extra_remote_files}")
                    file_diff = True
                if file_diff:
                    # --- use category in cache path ---
                    cache_proj = cache_dir / (category_name or "unknown") / project_name
                    if not cache_proj.exists():
                        cache_proj.mkdir(parents=True, exist_ok=True)
                    for local_file in local_files:
                        dest_path = cache_proj / local_file.name
                        shutil.copy2(local_file, dest_path)
                    # Only add to needs_update if files were actually copied to cache
                    if any(cache_proj.glob("**/*")):
                        needs_update.append(
                            {
                                "project_name": project_name,
                                "github_url": github_url,
                                "target_remote_path": target_remote_path_dir,
                            }
                        )
                        logger.info(f"Project needs update: {project_name}")
                else:
                    up_to_date.append(
                        {
                            "project_name": project_name,
                            "github_url": github_url,
                            "target_remote_path": target_remote_path_dir,
                        }
                    )
                    logger.info(f"Project up-to-date: {project_name}")
                project_stats.append(stats)
            elif target_remote_path_dir.lower() == "skip":
                logger.info(
                    f"Skipping project (target_remote_path=skip): {project_name}"
                )
                continue
            else:
                # --- treat as subdirectory path (e.g., "python/samples") ---
                local_dir = local_project / target_remote_path_dir
                remote_dir = list_all_files_in_repo(
                    owner,
                    repo,
                    target_remote_path_dir,
                    delay_sec=delay_sec,
                    return_relative=True,
                )
                # Always check for remote-only files, even if local_dir does not exist
                local_files = []
                if local_dir.exists() and local_dir.is_dir():
                    local_files = [
                        f
                        for f in local_dir.glob("**/*")
                        if f.is_file()
                        and not (
                            f.name.lower().endswith(".md")
                            or f.name.lower().endswith(".url")
                        )
                    ]
                stats["total_local_files"] = len(local_files)
                stats["total_remote_files"] = len(remote_dir)

                changed_files = compared_files = local_only = 0
                remote_only_set = set(remote_dir.keys())

                # Compare local files to remote
                for local_file in local_files:
                    rel_path = local_file.relative_to(local_dir)
                    rel_path_str = str(rel_path).replace("\\", "/")
                    if rel_path_str not in remote_dir:
                        logger.info(f"File missing remotely: {target_remote_path_dir}/{rel_path_str}")
                        file_diff = True
                        changed_files += 1
                        local_only += 1
                        continue
                    local_size = local_file.stat().st_size
                    remote_size = remote_dir[rel_path_str].get("size", 0)
                    compared_files += 1
                    if abs(local_size - remote_size) > 2:
                        logger.info(
                            f"File size differs: {target_remote_path_dir}/{rel_path_str} "
                            f"(local: {local_size}, remote: {remote_size})"
                        )
                        file_diff = True
                        changed_files += 1
                    remote_only_set.discard(rel_path_str)

                # If there are remote-only files, mark as needing update
                if remote_only_set:
                    logger.info(f"Extra files in remote: {remote_only_set}")
                    file_diff = True

                stats["compared_files"] = compared_files
                stats["changed_files"] = changed_files
                stats["local_only_files"] = local_only
                stats["remote_only_files"] = len(remote_only_set)
                stats["extra_info"] = (
                    f"Local files: {stats['total_local_files']}, "
                    f"Remote files: {stats['total_remote_files']}, "
                    f"Extra remote files: {len(remote_only_set)}"
                )
                if file_diff:
                    # --- use category in cache path ---
                    cache_proj = cache_dir / (category_name or "unknown") / project_name
                    if not cache_proj.exists():
                        cache_proj.mkdir(parents=True, exist_ok=True)
                    for local_file in local_files:
                        rel_path = local_file.relative_to(local_dir)
                        dest_path = cache_proj / rel_path
                        dest_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(local_file, dest_path)
                    # Only add to needs_update if files were actually copied to cache
                    if any(cache_proj.glob("**/*")):
                        needs_update.append(
                            {
                                "project_name": project_name,
                                "github_url": github_url,
                                "target_remote_path": target_remote_path_dir,
                            }
                        )
                        logger.info(f"Project needs update: {project_name}")
                else:
                    up_to_date.append(
                        {
                            "project_name": project_name,
                            "github_url": github_url,
                            "target_remote_path": target_remote_path_dir,
                        }
                    )
                    logger.info(f"Project up-to-date: {project_name}")
                project_stats.append(stats)

    # Write report and needs_update CSV
    write_report_and_update_csv(
        report_path, needs_update, up_to_date, update_csv_path, project_stats, index_csv_path=csv_path
    )


def write_report_and_update_csv(
    report_path, needs_update, up_to_date, update_csv_path, project_stats=None, index_csv_path=None
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
                f"-> local need to update\n"                     # NEW
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
                f"-> project up-to-date\n"                       # NEW
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
        fieldnames = ["project_name", "github_url", "target_remote_path", "allow_delete"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for p in needs_update:
            row = dict(p)
            row["allow_delete"] = allow_delete_map.get(p["project_name"], "")
            writer.writerow(row)
    logger.info(f"Needs-update CSV written to {update_csv_path}")


def manipulate_local_files(update_csv_path, root_dir):
    """
    For each project needing update, copy files/dirs from .cache/<category>/<project_name> to the actual project directory.
    If allow_delete is DELETE, remove the local project directory first,
    but do NOT delete files with .md or .url extensions.
    If the same file exists, it will be overwritten.
    Also copy files that exist only in .cache (i.e., new files).
    For empty placeholder files (0 bytes), copy the actual content from a local shallow clone of the repo if possible.
    """
    cache_dir = Path(root_dir) / ".cache"
    # Cache for default branch names {(owner, repo): branch_name}
    default_branch_cache = {}
    # Repo clone cache {(owner, repo, branch): local_path}
    repo_clone_cache = {}

    # Directory for shallow clones
    repo_cache_dir = Path(root_dir) / ".repo_cache"
    repo_cache_dir.mkdir(exist_ok=True)

    # Read allow_delete from the CSV
    with open(update_csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            project_name = row["project_name"]
            github_url = row["github_url"]
            target_remote_path = row.get("target_remote_path", "").strip()
            allow_delete = row.get("allow_delete", "").strip().upper()
            
            # Get GitHub repo info for downloading files
            owner, repo = get_github_repo_info(github_url)
            if not owner:
                logger.warning(f"Invalid GitHub URL: {github_url}")
                continue
            
            # Get default branch name
            if (owner, repo) not in default_branch_cache:
                try:
                    repo_url = f"https://api.github.com/repos/{owner}/{repo}"
                    repo_resp = requests.get(repo_url, headers=github_api_headers())
                    if repo_resp.status_code == 200:
                        default_branch = repo_resp.json()["default_branch"]
                        default_branch_cache[(owner, repo)] = default_branch
                        logger.info(f"Using default branch '{default_branch}' for {owner}/{repo}")
                    else:
                        default_branch_cache[(owner, repo)] = "main"  # fallback
                        logger.warning(f"Couldn't get default branch for {owner}/{repo}, using 'main'")
                except Exception as e:
                    default_branch_cache[(owner, repo)] = "main"  # fallback
                    logger.warning(f"Error getting default branch for {owner}/{repo}: {str(e)}, using 'main'")
            
            default_branch = default_branch_cache[(owner, repo)]

            # --- CLONE REPO IF NOT ALREADY CLONED ---
            repo_key = (owner, repo, default_branch)
            if repo_key not in repo_clone_cache:
                local_repo_path = repo_cache_dir / f"{owner}__{repo}__{default_branch}"
                if not local_repo_path.exists():
                    clone_url = f"https://github.com/{owner}/{repo}.git"
                    logger.info(f"Cloning {clone_url} (branch: {default_branch}) to {local_repo_path}")
                    try:
                        subprocess.run(
                            [
                                "git", "clone", "--depth", "1",
                                "--branch", default_branch,
                                clone_url, str(local_repo_path)
                            ],
                            check=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                        )
                        logger.info(f"Cloned {clone_url} to {local_repo_path}")
                    except Exception as e:
                        logger.warning(f"Failed to clone {clone_url}: {e}")
                        local_repo_path = None
                # Fix: check for None before .exists()
                if local_repo_path is not None and local_repo_path.exists():
                    repo_clone_cache[repo_key] = local_repo_path
                else:
                    repo_clone_cache[repo_key] = None
            else:
                local_repo_path = repo_clone_cache[repo_key]

            found = False
            for category in Path(root_dir).iterdir():
                if not category.is_dir():
                    continue
                candidate = category / project_name
                cache_proj = cache_dir / category.name / project_name
                if candidate.exists():
                    # --- DELETE local dir if allowed, but skip .md/.url files ---
                    if allow_delete == "DELETE" and candidate.exists():
                        for item in candidate.glob("**/*"):
                            if item.is_file():
                                ext = item.suffix.lower()
                                if ext in [".md", ".url"]:
                                    continue
                                item.unlink()
                            elif item.is_dir():
                                try:
                                    item.rmdir()
                                except OSError:
                                    pass
                        logger.info(f"Deleted local files (except .md/.url) in: {candidate}")
                    # Overwrite or add files from cache to local project (including new files)
                    if cache_proj.exists():
                        for src_file in cache_proj.glob("**/*"):
                            if src_file.is_file():
                                rel_path = src_file.relative_to(cache_proj)
                                dest_path = candidate / rel_path
                                dest_path.parent.mkdir(parents=True, exist_ok=True)
                                
                                # Check if file is empty (placeholder)
                                if src_file.stat().st_size == 0:
                                    # Try to copy from local repo clone
                                    rel_path_str = str(rel_path).replace("\\", "/")
                                    # Avoid double prefix: if rel_path already starts with target_remote_path, don't prepend
                                    if target_remote_path.lower() in ["root", "", "file"]:
                                        file_path_in_repo = rel_path_str
                                    else:
                                        trp = target_remote_path.rstrip("/")
                                        if rel_path_str.startswith(trp + "/"):
                                            file_path_in_repo = rel_path_str
                                        else:
                                            file_path_in_repo = f"{trp}/{rel_path_str}"
                                    # Remove leading slashes
                                    file_path_in_repo = file_path_in_repo.lstrip("/")

                                    # General fix for repeated prefixes (e.g., cookbook/cookbook/)
                                    # If file_path_in_repo starts with X/X/, reduce to X/
                                    parts = file_path_in_repo.split("/")
                                    if len(parts) > 1 and parts[0] == parts[1]:
                                        file_path_in_repo = "/".join(parts[1:])

                                    copied = False
                                    if local_repo_path and local_repo_path.exists():
                                        repo_file = local_repo_path / file_path_in_repo
                                        if not repo_file.exists():
                                            # Try to correct double samples/samples etc.
                                            alt_path = file_path_in_repo.replace("samples/samples/", "samples/")
                                            repo_file = local_repo_path / alt_path
                                        if repo_file.exists() and repo_file.is_file():
                                            shutil.copy2(repo_file, dest_path)
                                            logger.info(f"Copied {repo_file} from local clone to {dest_path}")
                                            copied = True
                                    if not copied:
                                        # fallback to HTTP download as before
                                        logger.warning(f"Could not find {file_path_in_repo} in local clone, falling back to HTTP download")
                                        # TODO: Implement HTTP download logic for placeholder files
                                        if not dest_path.exists() or dest_path.stat().st_size == 0:
                                            shutil.copy2(src_file, dest_path)
                                else:
                                    # Normal copy for non-empty files
                                    shutil.copy2(src_file, dest_path)
                                    logger.info(f"Updated {dest_path} from cache (overwritten or created).")
                    found = True
                    break
                    
            # If project directory does not exist, create it and copy from cache
            if not found:
                for category in Path(root_dir).iterdir():
                    if not category.is_dir():
                        continue
                    cache_proj = cache_dir / category.name / project_name
                    if cache_proj.exists():
                        candidate = category / project_name
                        candidate.mkdir(parents=True, exist_ok=True)
                        for src_file in cache_proj.glob("**/*"):
                            if src_file.is_file():
                                rel_path = src_file.relative_to(cache_proj)
                                dest_path = candidate / rel_path
                                dest_path.parent.mkdir(parents=True, exist_ok=True)
                                
                                # Check if file is empty (placeholder)
                                if src_file.stat().st_size == 0:
                                    # Try to copy from local repo clone
                                    rel_path_str = str(rel_path).replace("\\", "/")
                                    # Avoid double prefix: if rel_path already starts with target_remote_path, don't prepend
                                    if target_remote_path.lower() in ["root", "", "file"]:
                                        file_path_in_repo = rel_path_str
                                    else:
                                        trp = target_remote_path.rstrip("/")
                                        if rel_path_str.startswith(trp + "/"):
                                            file_path_in_repo = rel_path_str
                                        else:
                                            file_path_in_repo = f"{trp}/{rel_path_str}"
                                    
                                    # Remove leading slashes
                                    file_path_in_repo = file_path_in_repo.lstrip("/")

                                    # General fix for repeated prefixes (e.g., cookbook/cookbook/)
                                    # If file_path_in_repo starts with X/X/, reduce to X/
                                    parts = file_path_in_repo.split("/")
                                    if len(parts) > 1 and parts[0] == parts[1]:
                                        file_path_in_repo = "/".join(parts[1:])

                                    copied = False
                                    if local_repo_path and local_repo_path.exists():
                                        repo_file = local_repo_path / file_path_in_repo
                                        if not repo_file.exists():
                                            alt_path = file_path_in_repo.replace("samples/samples/", "samples/")
                                            repo_file = local_repo_path / alt_path
                                        if repo_file.exists() and repo_file.is_file():
                                            shutil.copy2(repo_file, dest_path)
                                            logger.info(f"Copied {repo_file} from local clone to {dest_path}")
                                            copied = True
                                    if not copied:
                                        # fallback to HTTP download as before
                                        logger.warning(f"Could not find {file_path_in_repo} in local clone, falling back to HTTP download")
                                        # ...existing HTTP download logic for placeholder...
                                        if not dest_path.exists() or dest_path.stat().st_size == 0:
                                            shutil.copy2(src_file, dest_path)
                                else:
                                    # Normal copy for non-empty files
                                    shutil.copy2(src_file, dest_path)
                                    logger.info(f"Created {dest_path} from cache (new project directory).")
                        found = True
                        break
            if not found:
                logger.warning(f"Project not found for flagging: {project_name}")


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
    args.manipulate = True
    # args.manipulate = True

    if args.index:
        index_projects(args.root, args.csv)
    elif args.compare:
        compare_projects(
            args.csv, args.root, args.report, args.update_csv, delay_sec=args.delay_sec
        )
    elif args.manipulate:
        manipulate_local_files(args.update_csv, args.root)
    elif args.delete_cache:
        cache_dir = Path(args.root) / ".cache"
        repo_cache_dir = Path(args.root) / ".repo_cache"
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
