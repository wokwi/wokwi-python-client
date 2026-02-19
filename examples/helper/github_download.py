import os
from pathlib import Path
from typing import Optional

import requests

# Use GITHUB_TOKEN for higher API rate limits (automatic in GitHub Actions)
_GITHUB_TOKEN: Optional[str] = os.getenv("GITHUB_TOKEN")


def _github_headers() -> dict[str, str]:
    headers: dict[str, str] = {}
    if _GITHUB_TOKEN:
        headers["Authorization"] = f"token {_GITHUB_TOKEN}"
    return headers


def download_file(url: str, dest: Path) -> None:
    response = requests.get(url, headers=_github_headers())
    response.raise_for_status()
    dest.parent.mkdir(parents=True, exist_ok=True)
    with open(dest, "wb") as f:
        f.write(response.content)


def download_github_dir(
    user: str, repo: str, path: str, base_path: Path, ref: str = "main"
) -> None:
    api_url = f"https://api.github.com/repos/{user}/{repo}/contents/{path}?ref={ref}"
    response = requests.get(api_url, headers=_github_headers())
    response.raise_for_status()
    items = response.json()
    for item in items:
        if item["type"] == "file":
            dest = base_path / item["name"]
            if dest.exists():
                continue
            print(f"Downloading {dest}...")
            download_file(item["download_url"], dest)
        elif item["type"] == "dir":
            subdir_name = item["name"]
            download_github_dir(user, repo, f"{path}/{subdir_name}", base_path / subdir_name, ref)
