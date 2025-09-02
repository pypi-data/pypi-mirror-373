import re
from typing import Optional

DEFAULT_PAT = re.compile(r"_barcode(\d{1,2})\b", re.IGNORECASE)

class BarcodeDetector:
    def __init__(self, pattern: Optional[str] = None, min_bc: int = 1, max_bc: int = 96, unassigned: str = "unassigned"):
        self.regex = re.compile(pattern, re.IGNORECASE) if pattern else DEFAULT_PAT
        self.min_bc = min_bc
        self.max_bc = max_bc
        self.unassigned = unassigned

    def _fmt(self, n: int) -> str:
        return f"barcode{n:02d}"

    def normalize(self, n: int) -> Optional[str]:
        if self.min_bc <= n <= self.max_bc:
            return self._fmt(n)
        return None

    def from_text(self, s: str) -> str:
        m = self.regex.search(s or "")
        if m:
            try:
                n = int(m.group(1))
                lab = self.normalize(n)
                if lab:
                    return lab
            except Exception:
                pass
        return self.unassigned
