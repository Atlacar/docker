#!/usr/bin/env bash
set -euo pipefail

PROFILE="${1:-stable}"
case "$PROFILE" in
  stable|latest) ;;
  *) echo "Usage: $0 [stable|latest]" >&2; exit 2 ;;
esac

VENV="${TMPDIR:-/tmp}/odoo19-pip-lock-$$"
python3 -m venv "$VENV"
"$VENV/bin/python" -m pip install -U pip pip-tools
"$VENV/bin/pip-compile" \
  --upgrade \
  --generate-hashes \
  --constraint odoo19-py312.constraints \
  "requirements-pypi-${PROFILE}.txt" \
  --output-file "requirements-pypi-${PROFILE}.lock.txt"
rm -rf "$VENV"
echo "Generated requirements-pypi-${PROFILE}.lock.txt"
