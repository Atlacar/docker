from importlib import metadata
from pathlib import Path
import os
import sys


def version(name):
    try:
        return metadata.version(name)
    except metadata.PackageNotFoundError:
        return "not-installed"


expected_odoo = os.environ.get("ODOO_VERSION", "")
print("Python executable:", sys.executable)
print("Python version:", sys.version.replace("\n", " "))
print("Expected Odoo series:", expected_odoo)

import odoo  # noqa: E402
import odoo.release  # noqa: E402
import weasyprint  # noqa: E402
import lxml_html_clean  # noqa: E402
import lxml.etree  # noqa: E402
from weasyprint import HTML  # noqa: E402

odoo_root = Path("/usr/lib/python3/dist-packages/odoo").resolve()
odoo_file = Path(odoo.__file__).resolve()
release = str(getattr(odoo.release, "version", "unknown"))

print("Odoo module:", odoo_file)
print("Odoo release:", release)
print("WeasyPrint:", weasyprint.__version__, weasyprint.__file__)
print("lxml runtime:", ".".join(map(str, lxml.etree.LXML_VERSION)))
print("lxml_html_clean module:", lxml_html_clean.__file__)

if odoo_file != odoo_root / "__init__.py":
    raise SystemExit(f"Odoo is not loaded from the in-place replacement path: {odoo_file}")

if expected_odoo and not release.startswith(expected_odoo):
    raise SystemExit(f"Expected Odoo {expected_odoo}, loaded release {release}")

enterprise_markers = (
    odoo_root / "addons" / "web_enterprise" / "__manifest__.py",
    odoo_root / "addons" / "account_accountant" / "__manifest__.py",
)
if not any(p.is_file() for p in enterprise_markers):
    raise SystemExit("Enterprise addon marker not found in the active Odoo source")

print("Enterprise Odoo source: OK")

if "/opt/odoo-venv/" in str(lxml_html_clean.__file__):
    raise SystemExit("lxml_html_clean must remain distro/Odoo-managed, not a PyPI venv override")

for package in (
    "Pillow",
    "lxml",
    "Werkzeug",
    "requests",
    "urllib3",
    "openpyxl",
    "pandas",
    "aiohttp",
    "phonenumbers",
    "watchdog",
    "lxml-html-clean",
):
    print(f"{package}: {version(package)}")

if weasyprint.__version__ != "70.0":
    raise SystemExit(f"Expected WeasyPrint 70.0, got {weasyprint.__version__}")

pdf_path = Path("/tmp/weasyprint-smoke-test.pdf")
HTML(
    string=f"""<!doctype html>
<html lang="zh-CN">
<meta charset="utf-8">
<style>
  body {{ font-family: sans-serif; }}
  h1 {{ margin-bottom: 0.4em; }}
</style>
<body>
  <h1>WeasyPrint 70 smoke test</h1>
  <p>中文测试 / Español / Odoo {expected_odoo} Enterprise / Ubuntu Noble</p>
</body>
</html>"""
).write_pdf(pdf_path)

if not pdf_path.exists() or pdf_path.stat().st_size < 1000:
    raise SystemExit("WeasyPrint smoke-test PDF was not generated correctly")

print("WeasyPrint PDF smoke test: OK", pdf_path.stat().st_size, "bytes")
