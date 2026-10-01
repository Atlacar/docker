#!/usr/bin/env bash
set -euo pipefail

# Optional helper for a stricter fully-resolved lock on a machine with Internet access.
# It does NOT modify the Dockerfile automatically; review the generated lock before use.
PROFILE="${1:-stable}"
case "$PROFILE" in
  stable|latest) ;;
  *) echo "Usage: $0 [stable|latest]" >&2; exit 2 ;;
esac

VENV="${TMPDIR:-/tmp}/odoo18-pip-lock-$$"
python3 -m venv "$VENV"
"$VENV/bin/python" -m pip install -U pip pip-tools
"$VENV/bin/pip-compile" \
  --upgrade \
  --generate-hashes \
  --constraint odoo18-py312.constraints \
  "requirements-pypi-${PROFILE}.txt" \
  --output-file "requirements-pypi-${PROFILE}.lock.txt"
rm -rf "$VENV"
echo "Generated requirements-pypi-${PROFILE}.lock.txt"
