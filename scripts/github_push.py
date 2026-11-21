"""Zero-dependency automated GitHub repository publisher using GitHub REST API.

Can push this entire project to GitHub without requiring git.exe or gh CLI installed!
Usage:
    python scripts/github_push.py --token <YOUR_GITHUB_PERSONAL_ACCESS_TOKEN> [--repo <REPO_NAME>] [--private]
"""

import os
import sys
import json
import base64
import argparse
import urllib.request
import urllib.error
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Files and directories to ignore when uploading to GitHub
IGNORE_PATTERNS = {
    "__pycache__",
    ".pytest_cache",
    ".git",
    ".venv",
    "venv",
    "env",
    ".DS_Store",
    "Thumbs.db",
    ".system_generated",
}


def api_request(url: str, token: str, method: str = "GET", payload: dict = None) -> dict:
    """Make an authenticated GitHub API request."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "ApexRent-AI-Agent-Publisher",
    }
    data = json.dumps(payload).encode("utf-8") if payload is not None else None

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            content = resp.read().decode("utf-8")
            return json.loads(content) if content else {}
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        try:
            err_json = json.loads(error_body)
            msg = err_json.get("message", error_body)
        except Exception:
            msg = error_body
        raise RuntimeError(f"GitHub API Error {e.code}: {msg}")


def get_authenticated_user(token: str) -> str:
    """Verify GitHub token and retrieve username."""
    user_data = api_request("https://api.github.com/user", token)
    return user_data["login"]


def ensure_repository(token: str, owner: str, repo_name: str, private: bool = False, description: str = "") -> dict:
    """Check if repository exists; if not, create it."""
    url = f"https://api.github.com/repos/{owner}/{repo_name}"
    try:
        repo = api_request(url, token, method="GET")
        print(f"✅ Found existing repository: {repo['html_url']}")
        return repo
    except RuntimeError:
        print(f"📦 Creating new GitHub repository '{repo_name}' for user @{owner}...")
        create_url = "https://api.github.com/user/repos"
        payload = {
            "name": repo_name,
            "description": description or "ApexRent AI: Real estate rental price prediction & advisory agent",
            "private": private,
            "has_issues": True,
            "has_projects": True,
            "has_wiki": False,
        }
        repo = api_request(create_url, token, method="POST", payload=payload)
        print(f"🎉 Created repository: {repo['html_url']}")
        return repo


def get_existing_file_sha(token: str, owner: str, repo_name: str, path: str) -> str:
    """Fetch existing file SHA if it exists on GitHub (required for file updates)."""
    url = f"https://api.github.com/repos/{owner}/{repo_name}/contents/{path}"
    try:
        data = api_request(url, token, method="GET")
        return data.get("sha")
    except RuntimeError:
        return None


def upload_file(token: str, owner: str, repo_name: str, local_path: Path, rel_path: str):
    """Upload or update a single file via the GitHub Contents API."""
    posix_path = rel_path.replace("\\", "/")
    with open(local_path, "rb") as f:
        file_bytes = f.read()

    b64_content = base64.b64encode(file_bytes).decode("utf-8")
    existing_sha = get_existing_file_sha(token, owner, repo_name, posix_path)

    payload = {
        "message": f"Add {posix_path}",
        "content": b64_content,
    }
    if existing_sha:
        payload["sha"] = existing_sha
        payload["message"] = f"Update {posix_path}"

    url = f"https://api.github.com/repos/{owner}/{repo_name}/contents/{posix_path}"
    api_request(url, token, method="PUT", payload=payload)
    print(f"  ⬆️ Uploaded: {posix_path}")


def should_ignore(path: Path) -> bool:
    """Check whether a path should be skipped."""
    for part in path.parts:
        if part in IGNORE_PATTERNS or part.endswith(".pyc"):
            return True
    return False


def push_project_to_github(token: str, repo_name: str = "rent-prediction-ai-agent", private: bool = False):
    """Upload entire project directory to GitHub."""
    print("=" * 60)
    print("🚀 ApexRent AI - Automated GitHub Publisher")
    print("=" * 60)

    try:
        username = get_authenticated_user(token)
        print(f"👤 Authenticated as GitHub user: @{username}")
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        print("\nPlease verify your GitHub Personal Access Token (classic or fine-grained with 'repo' scope).")
        return

    repo = ensure_repository(
        token=token,
        owner=username,
        repo_name=repo_name,
        private=private,
        description="ApexRent AI - Machine Learning Rent Prediction & Real Estate Advisory Agent",
    )

    print("\n📂 Scanning project files to upload...")
    files_to_upload = []
    for root, dirs, files in os.walk(BASE_DIR):
        dirs[:] = [d for d in dirs if d not in IGNORE_PATTERNS]
        for f in files:
            full_p = Path(root) / f
            if not should_ignore(full_p):
                rel_p = str(full_p.relative_to(BASE_DIR))
                files_to_upload.append((full_p, rel_p))

    print(f"Found {len(files_to_upload)} files to upload.\n")

    for full_path, rel_path in files_to_upload:
        try:
            upload_file(token, username, repo_name, full_path, rel_path)
        except Exception as e:
            print(f"  ⚠️ Error uploading {rel_path}: {e}")

    print("\n" + "=" * 60)
    print(f"✨ SUCCESS! Project posted to GitHub:")
    print(f"🔗 {repo['html_url']}")
    print("=" * 60 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Publish Rent Prediction AI Agent to GitHub")
    parser.add_argument(
        "--token",
        default=os.getenv("GITHUB_TOKEN"),
        help="GitHub Personal Access Token (or set GITHUB_TOKEN env var)",
    )
    parser.add_argument(
        "--repo",
        default="rent-prediction-ai-agent",
        help="GitHub repository name (default: rent-prediction-ai-agent)",
    )
    parser.add_argument(
        "--private",
        action="store_true",
        help="Make repository private (default is public)",
    )

    args = parser.parse_args()

    token = args.token
    if not token:
        print("GitHub token not provided via --token or GITHUB_TOKEN environment variable.")
        token = input("Enter your GitHub Personal Access Token: ").strip()

    if not token:
        print("❌ No token provided. Aborting.")
        sys.exit(1)

    push_project_to_github(token=token, repo_name=args.repo, private=args.private)


if __name__ == "__main__":
    main()
