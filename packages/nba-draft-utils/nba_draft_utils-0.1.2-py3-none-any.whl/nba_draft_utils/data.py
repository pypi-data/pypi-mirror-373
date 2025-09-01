from pathlib import Path
import pandas as pd

def read_csv_smart(path: str | Path) -> pd.DataFrame:
    """Read CSV with a tolerant encoding fallback (fixes cp1252/latin1 issues)."""
    p = Path(path)
    try:
        return pd.read_csv(p, encoding="utf-8")
    except UnicodeDecodeError:
        for enc in ("utf-8-sig", "cp1252", "latin1", "iso-8859-1"):
            try:
                return pd.read_csv(p, encoding=enc)
            except Exception:
                continue
        # last resort
        return pd.read_csv(p, encoding="cp1252", on_bad_lines="skip", engine="python")
