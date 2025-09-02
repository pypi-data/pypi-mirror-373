# barcodactyl

Split Barcode reads into per-barcode files. Supports FASTQ(.gz), SAM, and BAM.

## Install
```bash
pip install barcodactyl
```

## Run
```bash
barcodactyl reads.fastq -o out/ --prefix run1_
```

## Tests
```bash
pip install -e .[test]
pytest -q
```
