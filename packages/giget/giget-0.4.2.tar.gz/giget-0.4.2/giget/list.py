#!/usr/bin/env python3
import sys
import requests
from urllib.parse import urlparse

# ANSI colors for pretty output
BLUE = "\033[94m"
GREEN = "\033[92m"
RESET = "\033[0m"
CYAN = "\033[96m"
YELLOW = "\033[93m"

def parse_github_url(url: str):
    """Extract owner, repo, branch, and path from a GitHub URL."""
    try:
        # Remove the base GitHub URL part
        parts = url.split("github.com/")[1].split("/")
        
        if "tree" in parts:
            # URL format: github.com/owner/repo/tree/branch/path/to/dir
            owner, repo, _, branch, *path = parts
            folder_path = "/".join(path)
        else:
            # URL format: github.com/owner/repo or github.com/owner/repo/
            owner, repo, *path = parts
            branch = "master"  # default branch
            folder_path = "/".join(path)
            
        return owner, repo, branch, folder_path
    except Exception:
        raise ValueError("Invalid GitHub URL structure")

def fetch_contents(owner, repo, path, branch):
    """Fetch contents of a GitHub directory via API."""
    api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}?ref={branch}"
    headers = {"Accept": "application/vnd.github.v3+json"}
    
    resp = requests.get(api_url, headers=headers)
    
    if resp.status_code == 404:
        raise Exception(f"Path not found: {path}")
    elif resp.status_code != 200:
        try:
            error_data = resp.json()
            raise Exception(f"GitHub API error: {error_data.get('message', 'Unknown error')}")
        except:
            raise Exception(f"GitHub API error: HTTP {resp.status_code}")
    
    return resp.json()

def print_tree(owner, repo, branch, data, prefix=""):
    """Recursively print GitHub folder structure like `tree`."""
    for idx, item in enumerate(data):
        connector = "└── " if idx == len(data) - 1 else "├── "
        if item["type"] == "dir":
            print(prefix + connector + BLUE + item["name"] + RESET)
            try:
                sub_data = fetch_contents(owner, repo, item["path"], branch)
                new_prefix = prefix + ("    " if idx == len(data) - 1 else "│   ")
                print_tree(owner, repo, branch, sub_data, new_prefix)
            except Exception as e:
                print(prefix + ("    " if idx == len(data) - 1 else "│   ") + f"[Error: {e}]")
        else:
            print(prefix + connector + GREEN + item["name"] + RESET)

def list_github_folder(url: str):
    """List files/folders in a GitHub repo folder in tree format."""
    try:
        owner, repo, branch, repo_path = parse_github_url(url)
        data = fetch_contents(owner, repo, repo_path, branch)
        
        # Display the root path being listed
        display_path = f"{owner}/{repo}"
        if repo_path:
            display_path += f"/{repo_path}"
        
        print(f"{CYAN}{display_path}{RESET} (branch: {branch})")
        print_tree(owner, repo, branch, data)
        
    except Exception as e:
        raise Exception(f"Failed to list GitHub folder: {str(e)}")