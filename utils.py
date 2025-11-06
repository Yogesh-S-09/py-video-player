# utils.py

def format_time(seconds):
    """Formats seconds into HH:MM:SS or MM:SS."""
    if seconds is None or seconds < 0:
        return "--:--"
    try:
        m, s = divmod(int(seconds), 60)
        h, m = divmod(m, 60)
        if h > 0:
            return f"{h:02d}:{m:02d}:{s:02d}"
        else:
            return f"{m:02d}:{s:02d}"
    except Exception:
        return "--:--"