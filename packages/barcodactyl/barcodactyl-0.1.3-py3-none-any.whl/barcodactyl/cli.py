import argparse
import os
import sys
from .detector import BarcodeDetector
from .io_fastq import split_fastq
from .io_sam_bam import split_sam_bam

def detect_input_format(path: str) -> str:
    """Infer input format from file extension or magic bytes."""
    p = path.lower()
    if p.endswith((".fastq", ".fq", ".fastq.gz", ".fq.gz")):
        return "fastq"
    if p.endswith(".sam"):
        return "sam"
    if p.endswith(".bam"):
        return "bam"
    try:
        with open(path, "rb") as fh:
            if fh.read(4) == b"BAM\x01":
                return "bam"
    except Exception:
        pass
    raise SystemExit(f"Cannot infer input format: {path}")

def build_arg_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        prog="barcodactyl",
        description="Split Dorado-barcoded reads into per-barcode files (FASTQ/SAM/BAM)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    ap.add_argument("input", help="Input file: FASTQ(.gz), SAM, or BAM")
    ap.add_argument("-o", "--out-dir", default=".", help="Output directory")
    ap.add_argument("-p", "--prefix", default="", help="Filename prefix")
    ap.add_argument(
        "--out-format",
        choices=["auto", "fastq", "sam", "bam"],
        default="auto",
        help="Output format (default: same as input)",
    )
    ap.add_argument("--pattern", default=None, help="Custom regex for barcode")
    ap.add_argument("--unassigned-label", default="unassigned")
    ap.add_argument("--min-barcode", type=int, default=1)
    ap.add_argument("--max-barcode", type=int, default=96)
    ap.add_argument("-q", "--quiet", action="store_true")
    ap.add_argument(
        "--ignore-truncation",
        action="store_true",
        help="Try to read BAM without BGZF EOF marker (use with caution).",
    )
    return ap

def main(argv=None) -> int:
    ap = build_arg_parser()
    args = ap.parse_args(argv)
    in_fmt = detect_input_format(args.input)
    out_fmt = args.out_format if args.out_format != "auto" else in_fmt

    detector = BarcodeDetector(
        pattern=args.pattern,
        min_bc=args.min_barcode,
        max_bc=args.max_barcode,
        unassigned=args.unassigned_label,
    )

    os.makedirs(args.out_dir, exist_ok=True)

    if in_fmt == "fastq":
        if out_fmt != "fastq":
            raise SystemExit("FASTQ->SAM/BAM not supported")
        return (
            split_fastq(
                args.input,
                args.out_dir,
                args.prefix,
                detector,
                out_ext=".fastq",
                quiet=args.quiet,
            )
            or 0
        )

    elif in_fmt in ("sam", "bam"):
        if out_fmt not in ("sam", "bam"):
            raise SystemExit("SAM/BAM->FASTQ not supported")
        return (
            split_sam_bam(
                args.input,
                args.out_dir,
                args.prefix,
                detector,
                out_format=out_fmt,
                quiet=args.quiet,
                ignore_truncation=args.ignore_truncation,
            )
            or 0
        )

    else:
        raise SystemExit(f"Unknown input format {in_fmt}")


if __name__ == "__main__":
    sys.exit(main())
