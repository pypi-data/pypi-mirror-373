from code_context_analyzer.main import app


def test_cli_runs(monkeypatch):
    monkeypatch.setattr("sys.argv", ["cca", "."])
    try:
        app()
    except SystemExit:
        pass  # argparse may call sys.exit(), which is fine
