import os
import subprocess
from urllib.parse import urlparse


class RepositoryHandler:
    def is_github_url(self, source: str) -> bool:
        parsed = urlparse(source)
        return parsed.netloc == "github.com" and parsed.scheme == "https"

    def is_git_repo(self, path: str) -> bool:
        return os.path.isdir(os.path.join(path, ".git"))

    def clone(self, repo_url: str, target_dir: str, branch: str = "main"):
        subprocess.check_call([
            "git", "clone", "--branch", branch, "--single-branch", repo_url, target_dir
        ])

    def get_remote_branches(self, repo_dir: str) -> list[str]:
        if not self.is_git_repo(repo_dir):
            raise ValueError(
                f"The directory '{self.repo_path}' is not a valid Git "
                f"repository."
            )
        result = subprocess.check_output([
            "git", "-C", repo_dir, "branch", "-r"
        ], text=True)

        return [
            line.strip().replace("origin/", "")
            for line in result.splitlines()
            if "->" not in line
        ]

    def checkout_branch(self, repo_dir: str, branch_name: str):
        if not self.is_git_repo(repo_dir):
            raise ValueError(
                f"The directory '{self.repo_path}' is not a valid Git "
                f"repository."
            )
        subprocess.check_call(["git", "-C", repo_dir, "fetch", "origin", branch_name])
        subprocess.check_call(["git", "-C", repo_dir, "checkout", "-B", branch_name, f"origin/{branch_name}"])