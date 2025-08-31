"""CLI entrypoint for cca."""

import argparse
import sys

from code_context_analyzer.analyzer import Analyzer
from code_context_analyzer.repo_system import RepositorySession


def app(argv=None):
    parser = argparse.ArgumentParser(
        prog="cca", description="Codebase Context Analyzer"
    )
    parser.add_argument("source", help="Local path or GitHub repository URL")
    parser.add_argument(
        "--branch", default="main", help="Branch name (for GitHub repos)"
    )
    parser.add_argument(
        "--ignore",
        default="",
        help="Comma-separated ignore patterns (dist/*, *min.js/, docs/)",
    )
    parser.add_argument(
        "--max-files", type=int, default=1000, help="Max files to analyze"
    )
    # parser.add_argument("--depth", type=int, default=3, help="Module depth to summarize")
    parser.add_argument(
        "--ignore-tests",
        type=lambda x: x.lower() == "true",
        default=True,
        help="Ignore all tests that start with 'tests' (true/false)",
    )
    parser.add_argument(
        "--no-clipboard", action="store_true", help="Do not copy to clipboard"
    )
    args = parser.parse_args(argv)

    ignore_patterns = [s.strip() for s in args.ignore.split(",") if s.strip()]

    with RepositorySession(args.source, args.branch) as session:
        analyzer = Analyzer(
            session.path,
            max_files=args.max_files,
            # depth=args.depth,
            ignore_tests=args.ignore_tests,
            ignore=ignore_patterns,
        )
        results = analyzer.run_analysis()

        print(results)

        if not args.no_clipboard:
            try:
                from code_context_analyzer.analyzer.clipboard import (
                    copy_to_clipboard,
                )

                copy_to_clipboard(results)
                print("[info] Copied summary to clipboard")
            except Exception as e:
                print(f"[warn] Clipboard copy failed: {e}")


if __name__ == "__main__":
    app(sys.argv[1:])
