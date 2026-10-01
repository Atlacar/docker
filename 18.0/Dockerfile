# syntax=docker/dockerfile:1.7

FROM ubuntu:noble

LABEL org.opencontainers.image.title="Odoo 18 Enterprise on Ubuntu Noble with PyPI overlay" \
      org.opencontainers.image.description="Odoo 18 Community DEB bootstrap, source replaced in-place by local Enterprise archive" \
      org.opencontainers.image.vendor="custom"

SHELL ["/bin/bash", "-xo", "pipefail", "-c"]

ENV LANG=en_US.UTF-8 \
    VIRTUAL_ENV=/opt/odoo-venv \
    PATH=/opt/odoo-venv/bin:${PATH} \
    PYTHONNOUSERSITE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_PREFER_BINARY=1

ARG TARGETARCH
ARG PYPI_PROFILE=stable

# System packages remain the Odoo/Noble baseline.
# WeasyPrint itself is intentionally NOT installed from apt; it is provided by PyPI in the venv.
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        dirmngr \
        gnupg \
        libssl-dev \
        node-less \
        libwebp-dev \
        python3-venv \
        python3-magic \
        python3-num2words \
        python3-odf \
        python3-pdfminer \
        python3-pip \
        python3-phonenumbers \
        python3-pyldap \
        python3-qrcode \
        python3-renderpm \
        python3-setuptools \
        python3-slugify \
        python3-vobject \
        python3-watchdog \
        python3-xlwt \
        python3-inotify \
        python3-xlsxwriter \
        python3-xlrd \
        python3-aiohttp \
        python3-pil \
        python3-cups \
        cups-client \
        xz-utils \
        python3-pandas \
        python3-openpyxl \
        python3-lxml-html-clean \
        fontconfig \
        libpango-1.0-0 \
        libpangoft2-1.0-0 \
        libharfbuzz0b && \
    if [ -z "${TARGETARCH}" ]; then \
        TARGETARCH="$(dpkg --print-architecture)"; \
    fi; \
    WKHTMLTOPDF_ARCH=${TARGETARCH} && \
    case ${TARGETARCH} in \
    "amd64") WKHTMLTOPDF_ARCH=amd64 && WKHTMLTOPDF_SHA=967390a759707337b46d1c02452e2bb6b2dc6d59  ;; \
    "arm64")  WKHTMLTOPDF_SHA=90f6e69896d51ef77339d3f3a20f8582bdf496cc  ;; \
    "ppc64le" | "ppc64el") WKHTMLTOPDF_ARCH=ppc64el && WKHTMLTOPDF_SHA=5312d7d34a25b321282929df82e3574319aed25c  ;; \
    esac \
    && curl -o wkhtmltox.deb -sSL https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-3/wkhtmltox_0.12.6.1-3.jammy_${WKHTMLTOPDF_ARCH}.deb \
    && echo ${WKHTMLTOPDF_SHA} wkhtmltox.deb | sha1sum -c - \
    && apt-get install -y --no-install-recommends ./wkhtmltox.deb \
    && rm -rf /var/lib/apt/lists/* wkhtmltox.deb

# Install LxgwNeoXiHei font
RUN mkdir -p /usr/share/fonts/truetype/LXGWNeoXiHei && \
    curl -fL --retry 5 --retry-delay 2 \
      https://github.com/lxgw/LxgwNeoXiHei/releases/download/v1.211/LXGWNeoXiHei.ttf \
      -o /usr/share/fonts/truetype/LXGWNeoXiHei/LXGWNeoXiHei.ttf && \
    fc-cache -f

# Install latest PostgreSQL client
RUN echo 'deb http://apt.postgresql.org/pub/repos/apt/ noble-pgdg main' > /etc/apt/sources.list.d/pgdg.list && \
    GNUPGHOME="$(mktemp -d)" && \
    export GNUPGHOME && \
    repokey='B97B0AFCAA1A47F044F244A07FCC7D46ACCC4CF8' && \
    gpg --batch --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys "${repokey}" && \
    gpg --batch --armor --export "${repokey}" > /etc/apt/trusted.gpg.d/pgdg.gpg.asc && \
    gpgconf --kill all && \
    rm -rf "$GNUPGHOME" && \
    apt-get update && \
    apt-get install --no-install-recommends -y postgresql-client && \
    rm -f /etc/apt/sources.list.d/pgdg.list && \
    rm -rf /var/lib/apt/lists/*

# Install rtlcss (on Debian buster)
RUN apt-get update && \
    apt-get install -y --no-install-recommends nodejs npm \
    && npm install -g rtlcss \
    && apt-get purge --autoremove -y npm \
    && rm -rf /var/lib/apt/lists/*

# ---------------------------------------------------------------------------
# Bootstrap Odoo with the official Community .deb, then REPLACE its Python
# source in the SAME RUN layer with the local full Enterprise (+e) archive.
#
# Why one RUN?
# Removing Community source in a later Docker layer would hide it at runtime,
# but the bytes would remain in the previous layer and still enlarge the image.
#
# Why RUN --mount instead of COPY?
# The Enterprise .tar.gz is only mounted for this build step and is not stored
# as a separate image layer.
# ---------------------------------------------------------------------------
ENV ODOO_VERSION=18.0
ARG ODOO_RELEASE=20260811
ARG ODOO_SHA256=""
ARG ODOO_ENTERPRISE_SHA256=""

RUN --mount=type=bind,source=odoo_18.0+e.20260811.tar.gz,target=/tmp/odoo-enterprise.tar.gz,readonly \
    set -eux; \
    \
    curl -fL --retry 5 --retry-delay 2 \
      -o /tmp/odoo.deb \
      "https://nightly.odoo.com/${ODOO_VERSION}/nightly/deb/odoo_${ODOO_VERSION}.${ODOO_RELEASE}_all.deb"; \
    \
    if [ -n "${ODOO_SHA256}" ]; then \
      echo "${ODOO_SHA256}  /tmp/odoo.deb" | sha256sum -c -; \
    else \
      echo "WARNING: ODOO_SHA256 is empty; Community bootstrap .deb integrity is not pinned." >&2; \
    fi; \
    \
    if [ -n "${ODOO_ENTERPRISE_SHA256}" ]; then \
      echo "${ODOO_ENTERPRISE_SHA256}  /tmp/odoo-enterprise.tar.gz" | sha256sum -c -; \
    else \
      echo "WARNING: ODOO_ENTERPRISE_SHA256 is empty; Enterprise archive integrity is not pinned." >&2; \
    fi; \
    \
    apt-get update; \
    apt-get -y install --no-install-recommends /tmp/odoo.deb; \
    \
    # Confirm what the .deb installed before replacing it.
    COMMUNITY_ODOO_DIR="$(python3 -c 'import os, odoo; print(os.path.dirname(os.path.realpath(odoo.__file__)))')"; \
    echo "Community bootstrap Odoo path: ${COMMUNITY_ODOO_DIR}"; \
    test "${COMMUNITY_ODOO_DIR}" = "/usr/lib/python3/dist-packages/odoo"; \
    getent passwd odoo >/dev/null; \
    getent group odoo >/dev/null; \
    test -x /usr/bin/odoo; \
    \
    # Validate the Enterprise archive in a temporary directory first.
    mkdir -p /tmp/odoo-enterprise-src; \
    tar \
      --extract \
      --gzip \
      --file=/tmp/odoo-enterprise.tar.gz \
      --strip-components=1 \
      --directory=/tmp/odoo-enterprise-src; \
    test -f /tmp/odoo-enterprise-src/odoo/__init__.py; \
    test -f /tmp/odoo-enterprise-src/odoo/release.py; \
    test -f /tmp/odoo-enterprise-src/requirements.txt; \
    test -d /tmp/odoo-enterprise-src/odoo/addons; \
    if [ ! -f /tmp/odoo-enterprise-src/odoo/addons/web_enterprise/__manifest__.py ] && \
       [ ! -f /tmp/odoo-enterprise-src/odoo/addons/account_accountant/__manifest__.py ]; then \
      echo "ERROR: Enterprise addon marker not found. Is this really a full Odoo +e archive?" >&2; \
      exit 1; \
    fi; \
    \
    # Delete only Community Python source/metadata; keep the .deb-created
    # user, group, /usr/bin/odoo, /etc/odoo, /var/lib/odoo and dependencies.
    rm -rf \
      /usr/lib/python3/dist-packages/odoo \
      /usr/lib/python3/dist-packages/odoo-*.egg-info \
      /usr/lib/python3/dist-packages/odoo-*.dist-info; \
    \
    # Put Enterprise source at the exact path expected by the .deb launcher.
    mkdir -p /usr/lib/python3/dist-packages/odoo; \
    cp -a /tmp/odoo-enterprise-src/odoo/. /usr/lib/python3/dist-packages/odoo/; \
    if [ -d /tmp/odoo-enterprise-src/odoo.egg-info ]; then \
      cp -a /tmp/odoo-enterprise-src/odoo.egg-info /usr/lib/python3/dist-packages/; \
    fi; \
    chown -R root:root \
      /usr/lib/python3/dist-packages/odoo \
      /usr/lib/python3/dist-packages/odoo.egg-info 2>/dev/null || true; \
    \
    # Verify that Python now loads the replaced Enterprise tree.
    python3 -c 'from pathlib import Path; import odoo, odoo.release; root=Path("/usr/lib/python3/dist-packages/odoo").resolve(); loaded=Path(odoo.__file__).resolve(); print("Odoo loaded from:", loaded); print("Odoo release:", getattr(odoo.release, "version", "unknown")); assert loaded == root / "__init__.py", f"Unexpected Odoo import path: {loaded}"; markers=(root/"addons"/"web_enterprise"/"__manifest__.py", root/"addons"/"account_accountant"/"__manifest__.py"); assert any(p.is_file() for p in markers), "Enterprise addon marker missing after replacement"; print("Enterprise Odoo in-place replacement: OK")'; \
    \
    # Prevent an accidental apt upgrade/reinstall from restoring Community code.
    apt-mark hold odoo; \
    \
    rm -rf \
      /tmp/odoo.deb \
      /tmp/odoo-enterprise-src \
      /var/lib/apt/lists/*

# PyPI overlay: keep Odoo's Noble/Python 3.12 package versions constrained,
# but allow selected non-core packages and WeasyPrint to come from PyPI.
# Do NOT pip-upgrade lxml-html-clean: 0.4.5 requires lxml>=6.1.1, while
# Odoo 18/Noble pins lxml==5.2.1. The apt package remains authoritative.
COPY ./odoo18-py312.constraints /opt/odoo18-py312.constraints
COPY ./requirements-pypi-stable.txt /opt/requirements-pypi-stable.txt
COPY ./requirements-pypi-latest.txt /opt/requirements-pypi-latest.txt
COPY ./verify-python-stack.py /opt/verify-python-stack.py

RUN python3 -m venv --system-site-packages "${VIRTUAL_ENV}" && \
    "${VIRTUAL_ENV}/bin/python" -m pip install --no-cache-dir --upgrade pip setuptools wheel && \
    "${VIRTUAL_ENV}/bin/python" -c 'import lxml_html_clean; print("Using apt lxml_html_clean:", lxml_html_clean.__file__)' && \
    case "${PYPI_PROFILE}" in \
      stable) PYPI_REQUIREMENTS=/opt/requirements-pypi-stable.txt ;; \
      latest) PYPI_REQUIREMENTS=/opt/requirements-pypi-latest.txt ;; \
      *) echo "PYPI_PROFILE must be 'stable' or 'latest' (got: ${PYPI_PROFILE})" >&2; exit 2 ;; \
    esac && \
    "${VIRTUAL_ENV}/bin/python" -m pip install \
      --no-cache-dir \
      --upgrade \
      --upgrade-strategy only-if-needed \
      --constraint /opt/odoo18-py312.constraints \
      -r "${PYPI_REQUIREMENTS}"

# /usr/bin/odoo has a system-Python shebang. This wrapper makes the existing
# entrypoint's `exec odoo ...` use the venv interpreter while still launching
# the .deb-provided /usr/bin/odoo script. That script imports the Enterprise
# source now installed in /usr/lib/python3/dist-packages/odoo.
RUN cat > "${VIRTUAL_ENV}/bin/odoo" <<'EOF_WRAPPER' && chmod +x "${VIRTUAL_ENV}/bin/odoo"
#!/bin/bash
exec /opt/odoo-venv/bin/python3 /usr/bin/odoo "$@"
EOF_WRAPPER

# Build-time smoke test: verify Enterprise Odoo source, PyCUPS and a real
# WeasyPrint PDF render.
RUN "${VIRTUAL_ENV}/bin/python" /opt/verify-python-stack.py

# Copy entrypoint script and Odoo configuration file
COPY ./entrypoint.sh /
COPY ./odoo.conf /etc/odoo/
COPY ./wait-for-psql.py /usr/local/bin/wait-for-psql.py

# Set permissions and Mount /var/lib/odoo to allow restoring filestore and /mnt/extra-addons for users addons
RUN chmod +x /entrypoint.sh /usr/local/bin/wait-for-psql.py && \
    chown odoo:odoo /etc/odoo/odoo.conf && \
    mkdir -p \
        /var/lib/odoo/sessions \
        /var/lib/odoo/addons/18.0 \
        /mnt/extra-addons && \
    chown -R odoo:odoo \
        /var/lib/odoo \
        /mnt/extra-addons && \
    chmod 700 /var/lib/odoo/sessions
VOLUME ["/var/lib/odoo", "/mnt/extra-addons"]

# Expose Odoo services
EXPOSE 8069 8071 8072

# Set the default config file
ENV ODOO_RC=/etc/odoo/odoo.conf

# Set default user when running the container
USER odoo

ENTRYPOINT ["/entrypoint.sh"]
CMD ["odoo"]
