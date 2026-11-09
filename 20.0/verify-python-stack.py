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
import authlib  # noqa: E402
import lxml_html_clean  # noqa: E402
import lxml.etree  # noqa: E402

odoo_root = Path("/usr/lib/python3/dist-packages/odoo").resolve()
odoo_path = Path(odoo.release.__file__).resolve().parent
release = str(getattr(odoo.release, "version", "unknown"))

print("Odoo namespace paths:", list(odoo.__path__))
print("Odoo release module:", odoo.release.__file__)
print("Odoo release:", release)
print("Authlib:", authlib.__version__, authlib.__file__)
print("lxml runtime:", ".".join(map(str, lxml.etree.LXML_VERSION)))
print("lxml_html_clean module:", lxml_html_clean.__file__)

if odoo_path != odoo_root:
    raise SystemExit(f"Odoo is not loaded from the in-place replacement path: {odoo_path}")

if not (odoo_root / "init.py").is_file():
    raise SystemExit("Odoo 19+/20 namespace initialization module init.py is missing")

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
