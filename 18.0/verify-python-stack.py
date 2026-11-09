from importlib import metadata
from pathlib import Path
import sys


def version(name):
    try:
        return metadata.version(name)
    except metadata.PackageNotFoundError:
        return "not-installed"


print("Python executable:", sys.executable)
print("Python version:", sys.version.replace("\n", " "))

import odoo  # noqa: E402
import cups  # noqa: E402
import authlib  # noqa: E402
import lxml_html_clean  # noqa: E402
import lxml.etree  # noqa: E402

odoo_root = Path("/usr/lib/python3/dist-packages/odoo").resolve()
odoo_file = Path(odoo.__file__).resolve()

print("Odoo module:", odoo_file)
print("PyCUPS module:", cups.__file__)
print("Authlib:", authlib.__version__, authlib.__file__)
print("lxml runtime:", ".".join(map(str, lxml.etree.LXML_VERSION)))
print("lxml_html_clean module:", lxml_html_clean.__file__)

if odoo_file != odoo_root / "__init__.py":
    raise SystemExit(f"Odoo is not loaded from the in-place replacement path: {odoo_file}")

enterprise_markers = (
    odoo_root / "addons" / "web_enterprise" / "__manifest__.py",
    odoo_root / "addons" / "account_accountant" / "__manifest__.py",
)
if not any(p.is_file() for p in enterprise_markers):
    raise SystemExit("Enterprise addon marker not found in the active Odoo source")

print("Enterprise Odoo source: OK")

if "/opt/odoo-venv/" in lxml_html_clean.__file__:
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
