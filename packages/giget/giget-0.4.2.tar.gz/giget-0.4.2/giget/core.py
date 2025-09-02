import requests, os

def download_github_dir(owner, repo, path, branch="master", save_dir=".", flat=False, force=False, rename=False):
    """Download a GitHub folder recursively with overwrite/rename options."""

    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}?ref={branch}"
    response = requests.get(url).json()

    if isinstance(response, dict) and response.get("message"):
        raise Exception(f"GitHub API error: {response['message']}")

    for item in response:
        if item["type"] == "file":
            if flat:
                item_path = os.path.join(save_dir, os.path.basename(item["path"]))
            else:
                item_path = os.path.join(save_dir, item["path"])
                os.makedirs(os.path.dirname(item_path), exist_ok=True)

            # ⚡ Handle existing file
            if os.path.exists(item_path):
                if force:
                    print(f"⚠️ Overwriting {item_path}")
                elif rename:
                    base, ext = os.path.splitext(item_path)
                    counter = 1
                    new_path = f"{base}_{counter}{ext}"
                    while os.path.exists(new_path):  # keep incrementing until unique
                        counter += 1
                        new_path = f"{base}_{counter}{ext}"
                    item_path = new_path
                    print(f"📄 Renamed and saving as {item_path}")
                else:
                    raise FileExistsError(
                        f"❌ File already exists: {item_path}\n"
                        f"Use --force to overwrite or --rename to save with a new name."
                    )

            print(f"⬇️  Downloading {item['download_url']}")
            file_data = requests.get(item["download_url"]).content
            with open(item_path, "wb") as f:
                f.write(file_data)

        elif item["type"] == "dir":
            if flat:
                # ⚡ Skip making directories in flat mode, just recurse inside
                download_github_dir(owner, repo, item["path"], branch, save_dir, flat, force, rename)
            else:
                dir_path = os.path.join(save_dir, item["path"])

                # ⚡ Handle existing directory
                if os.path.exists(dir_path):
                    if force:
                        print(f"⚠️ Overwriting directory {dir_path}")
                    elif rename:
                        counter = 1
                        new_path = f"{dir_path}_{counter}"
                        while os.path.exists(new_path):
                            counter += 1
                            new_path = f"{dir_path}_{counter}"
                        dir_path = new_path
                        print(f"📂 Renamed directory to {dir_path}")
                    else:
                        raise FileExistsError(
                            f"❌ Directory already exists: {dir_path}\n"
                            f"Use --force to overwrite or --rename to save with a new name."
                        )

                os.makedirs(dir_path, exist_ok=True)

                # Recurse into subdirectory
                download_github_dir(owner, repo, item["path"], branch, save_dir, flat, force, rename)
