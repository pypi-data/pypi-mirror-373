import os

from code_context_analyzer.utils.temp_dir import temp_directory

from .handler import RepositoryHandler


class RepositorySession:
    def __init__(self, repo_url: str, default_branch: str = "main"):
        self.repo_url = repo_url
        self.default_branch = default_branch
        self.repo_path = None
        self.handler = RepositoryHandler()
        self._branches = None

    def __enter__(self):
        if self.handler.is_github_url(self.repo_url):
            # GitHub: clone into temp directory
            self._temp_context = temp_directory(prefix="repo_session_")
            self.repo_path = self._temp_context.__enter__()
            self.handler.clone(
                self.repo_url,
                self.repo_path,
                self.default_branch
            )
            self._branches = self.handler.get_remote_branches(self.repo_path)
            self._cleanup_required = True
        else:
            # Local path: validate and use
            if not os.path.exists(self.repo_url) or not os.path.isdir(
                    self.repo_url
            ):
                raise ValueError(f"Invalid local path: {self.source}")
            self.repo_path = os.path.abspath(self.repo_url)
            self._cleanup_required = False
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._cleanup_required and self._temp_context:
            self._temp_context.__exit__(exc_type, exc_val, exc_tb)

    @property
    def path(self):
        return self.repo_path

    @property
    def branches(self):
        return self._branches

    def checkout(self, branch_name: str):
        self.handler.checkout_branch(self.repo_path, branch_name)