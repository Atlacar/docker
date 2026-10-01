# Odoo 19/20 PyPI + WeasyPrint + venv wrapper migration

This migration ports the enhanced Odoo 18 image pattern to Odoo 19.0 and 20.0 on Ubuntu 24.04 Noble.

## Enterprise archives expected in each build context

- `19.0/odoo_19.0+e.20260505.tar.gz`
- `20.0/odoo-20.0+e.20260930.tar.gz`

The archives are bind-mounted only for the Enterprise source replacement step, so they are not copied into a separate image layer.

## What was migrated

- Community `.deb` bootstrap + in-place Enterprise Python source replacement in the same image layer.
- `/opt/odoo-venv` created with `--system-site-packages`.
- `PATH=/opt/odoo-venv/bin:$PATH` plus an `odoo` wrapper that runs `/usr/bin/odoo` with the venv Python interpreter.
- `stable` and `latest` PyPI overlay profiles.
- WeasyPrint 70.0 from PyPI, with Pango/Harfbuzz/font system libraries from Noble.
- Odoo core dependency guardrails derived from Odoo Community `19.0/requirements.txt` and `20.0/requirements.txt` for Python 3.12/Noble.
- `lxml-html-clean` remains distro/Odoo managed rather than upgraded by the PyPI overlay.
- Build-time smoke test validates Enterprise source, Odoo major series, lxml source, and an actual WeasyPrint PDF render.
- LF normalization in source plus a Dockerfile `sed` safety net for Windows checkouts.

## Build Odoo 19

```bash
cd 19.0
# Put odoo_19.0+e.20260505.tar.gz in this directory first.
docker build --progress=plain \
  --build-arg PYPI_PROFILE=stable \
  -t odoo:19e-20260505 .
```

Latest non-core overlay:

```bash
docker build --progress=plain \
  --build-arg PYPI_PROFILE=latest \
  -t odoo:19e-20260505-latest .
```

## Build Odoo 20

```bash
cd 20.0
# Put odoo-20.0+e.20260930.tar.gz in this directory first.
docker build --progress=plain \
  --build-arg PYPI_PROFILE=stable \
  -t odoo:20e-20260930 .
```

Latest non-core overlay:

```bash
docker build --progress=plain \
  --build-arg PYPI_PROFILE=latest \
  -t odoo:20e-20260930-latest .
```

## Optional integrity pinning

The Dockerfiles accept:

- `ODOO_SHA256` for the Community bootstrap `.deb`.
- `ODOO_ENTERPRISE_SHA256` for the local Enterprise tarball.

Example:

```bash
docker build \
  --build-arg ODOO_ENTERPRISE_SHA256="$(sha256sum odoo-20.0+e.20260930.tar.gz | awk '{print $1}')" \
  -t odoo:20e-20260930 .
```

## PyPI profiles

`stable` installs only WeasyPrint 70.0 on top of the distro/Odoo Python stack.

`latest` additionally overlays the same selected non-core packages as the enhanced 18.0 image:

- pandas 3.0.6
- aiohttp 3.14.3
- phonenumbers 9.0.39
- watchdog 6.0.0

Odoo core dependencies are protected by the version-specific constraints files.

## Important dependency difference

For Python 3.12/Noble, Odoo 20 adds `h11==0.16.0` to its Community requirements. Odoo 20 no longer lists the Odoo 19 `pytz` and `xlwt` requirements. The two generated constraints files reflect those branch-specific declarations.
