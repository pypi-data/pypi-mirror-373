import os
import re
import mlflow

ENV_PATTERNS = [
    re.compile(r"os\.getenv\(\s*[\"'](\w+)[\"']"),                # os.getenv("VAR")
    re.compile(r"os\.environ\.get\(\s*[\"'](\w+)[\"']"),           # os.environ.get("VAR")
    re.compile(r"os\.environ\[\s*[\"'](\w+)[\"']\s*\]"),           # os.environ["VAR"]
]

def find_env_vars_in_file(file_path):
    found_vars = set()
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            for pattern in ENV_PATTERNS:
                found_vars.update(pattern.findall(content))
    except (UnicodeDecodeError, OSError):
        pass  # Skip unreadable files
    return found_vars

def recursively_find_env_vars(start_path, exclude_dirs=None):
    if exclude_dirs is None:
        exclude_dirs = {"venv", ".venv", "__pycache__", ".git", ".mypy_cache", ".pytest_cache", "site-packages"}

    all_vars = set()
    for root, dirs, files in os.walk(start_path):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.startswith(".")]

        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(root, file)
                file_vars = find_env_vars_in_file(full_path)
                if file_vars:
                    all_vars.update(file_vars)
    return all_vars

def read_variables() -> str:
    current_path = os.getcwd()
    env_vars = recursively_find_env_vars(current_path)
    logged_vars = ""
    for var in env_vars:
        logged_vars += f"{var}\n"
    return logged_vars
