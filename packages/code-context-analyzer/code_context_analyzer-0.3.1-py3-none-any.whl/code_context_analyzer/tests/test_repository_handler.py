import os

from code_context_analyzer.repo_system.session import RepositorySession


def test_local_path_resolution(tmp_path):
    for path in [tmp_path, "https://github.com/ahasanular/classScheduleMaker"]:
        with RepositorySession(str(path)) as session:
            assert os.path.exists(session.path)

