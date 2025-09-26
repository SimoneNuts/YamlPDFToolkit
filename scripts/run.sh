#!/usr/bin/env bash
set -euo pipefail
SRC=${1:-"./examples"}
OUT=${2:-"./pdf"}
python3 "$(dirname "$0")/../openapi_to_pdf.py" --src "$SRC" --out "$OUT" --keep-html