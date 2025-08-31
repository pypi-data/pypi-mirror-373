import os
import shutil
import stat
import tempfile
from contextlib import contextmanager


def handle_remove_readonly(func, path, exc_info):
    """
    Error handler for shutil.rmtree to handle read-only files and directories
    across platforms including Windows.
    """
    try:
        # Try making file or directory writable
        os.chmod(path, stat.S_IWRITE | stat.S_IREAD | stat.S_IEXEC)
    except Exception:
        pass

    try:
        # Retry the original function (e.g., os.remove or os.rmdir)
        func(path)
    except Exception:
        # As last resort: try to remove manually
        try:
            if os.path.isdir(path) and not os.path.islink(path):
                os.rmdir(path)
            else:
                os.remove(path)
        except Exception:
            pass  # Still suppress – temp directory cleanup shouldn't crash app


@contextmanager
def temp_directory(suffix="", prefix="tmp", dir=None):
    path = tempfile.mkdtemp(suffix=suffix, prefix=prefix, dir=dir)
    try:
        yield path
    finally:
        try:
            shutil.rmtree(path, onerror=handle_remove_readonly)
            print(f"✅ Temp directory deleted: {path}")
        except Exception as e:
            print(f"❌ Failed to delete temp directory '{path}': {e}")
