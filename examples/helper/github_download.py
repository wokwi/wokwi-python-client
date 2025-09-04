from pathlib import Path

import requests


def download_file(url: str, dest: Path) -> None:
    response = requests.get(url)
    response.raise_for_status()
    dest.parent.mkdir(parents=True, exist_ok=True)
    with open(dest, "wb") as f:
        f.write(response.content)


def download_github_dir(
    user: str, repo: str, path: str, base_path: Path, ref: str = "main"
) -> None:
    api_url = f"https://api.github.com/repos/{user}/{repo}/contents/{path}?ref={ref}"
    response = requests.get(api_url)
    response.raise_for_status()
    items = response.json()
    for item in items:
        if item["type"] == "file":
            print(f"Downloading {base_path / item['name']}...")
            download_file(item["download_url"], base_path / item["name"])
        elif item["type"] == "dir":
            subdir_name = item["name"]
            download_github_dir(user, repo, f"{path}/{subdir_name}", base_path / subdir_name, ref)
