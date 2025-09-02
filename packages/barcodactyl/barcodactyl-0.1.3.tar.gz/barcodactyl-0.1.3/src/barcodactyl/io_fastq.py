import gzip, os, sys
from collections import defaultdict
from typing import Dict, TextIO
from .detector import BarcodeDetector

def _open_maybe_gz(path: str, mode: str = "rt"):
    if path.endswith(".gz"):
        return gzip.open(path, mode)
    return open(path, mode)

def split_fastq(in_path: str, out_dir: str, prefix: str, detector: BarcodeDetector, out_ext: str = ".fastq", quiet: bool = False) -> int:
    os.makedirs(out_dir, exist_ok=True)
    writers: Dict[str, TextIO] = {}
    counts = defaultdict(int)

    def get_writer(label: str) -> TextIO:
        fn = os.path.join(out_dir, f"{prefix}{label}{out_ext}")
        w = writers.get(label)
        if w is None:
            w = open(fn, "a")
            writers[label] = w
        return w

    total = 0
    with _open_maybe_gz(in_path, "rt") as fh:
        while True:
            h = fh.readline()
            if not h: break
            s = fh.readline(); plus = fh.readline(); q = fh.readline()
            if not q:
                sys.stderr.write("Warning: truncated FASTQ record at EOF\n")
                break
            label = detector.from_text(h)
            w = get_writer(label)
            w.write(h); w.write(s); w.write(plus); w.write(q)
            counts[label] += 1
            total += 1

    for w in writers.values():
        w.close()

    if not quiet:
        sys.stderr.write("\n=== Per-barcode counts ===\n")
        total2 = 0
        for k in sorted(counts):
            sys.stderr.write(f"{k}\t{counts[k]:,}\n")
            total2 += counts[k]
        sys.stderr.write(f"Total reads written:\t{total2:,}\n")
    return total
