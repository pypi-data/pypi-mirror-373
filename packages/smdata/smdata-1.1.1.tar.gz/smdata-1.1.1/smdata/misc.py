import ctypes


def is_process_admin() -> bool:
    """Checks is process started with admin rights"""

    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())

    except Exception:
        return False
