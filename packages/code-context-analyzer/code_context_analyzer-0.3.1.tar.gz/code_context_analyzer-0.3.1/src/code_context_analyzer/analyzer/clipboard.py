"""
Clipboard abstraction (pyperclip) with safe fallback to printing.
"""
# analyzer/clipboard.py

try:
    import pyperclip
except ImportError:
    pyperclip = None


def copy_to_clipboard(text: str) -> bool:
    """
    Copy given text to system clipboard.

    Returns True on success, False otherwise.
    """
    if pyperclip is None:
        print("pyperclip is not installed. Run `pip install pyperclip`.")
        return False

    try:
        pyperclip.copy(text)
        return True
    except Exception as e:
        print(f"Failed to copy to clipboard: {e}")
        return False
