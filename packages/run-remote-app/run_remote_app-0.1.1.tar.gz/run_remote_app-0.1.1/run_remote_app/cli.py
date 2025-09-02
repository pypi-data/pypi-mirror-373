#!/usr/bin/env python3
import subprocess
import pathlib
import sys

CACHE_DIR = pathlib.Path.home() / ".cache" / "run_remote_app"
REPO_URL = "https://github.com/nguyenduongit/remote-app.git"

def ensure_latest_repo():
    if CACHE_DIR.exists():
        try:
            subprocess.run(["git", "-C", str(CACHE_DIR), "pull"], check=True)
        except subprocess.CalledProcessError:
            print("⚠️ Pull thất bại, xoá cache và clone lại...")
            subprocess.run(["rm", "-rf", str(CACHE_DIR)])
            subprocess.run(["git", "clone", REPO_URL, str(CACHE_DIR)], check=True)
    else:
        subprocess.run(["git", "clone", REPO_URL, str(CACHE_DIR)], check=True)

def main():
    ensure_latest_repo()
    sys.path.insert(0, str(CACHE_DIR))
    from app import run_app  # import từ repo remote-app
    run_app()