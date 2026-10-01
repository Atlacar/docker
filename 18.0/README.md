# Odoo 18 Enterprise in-place replacement V3

这个版本基于 V2（Ubuntu Noble + `/opt/odoo-venv` + WeasyPrint 70）修改。

## 目标

Community `.deb` **只作为 bootstrap**：

- 创建 `odoo` 用户和组；
- 建立 `/etc/odoo`、`/var/lib/odoo` 等 Debian/Odoo 环境；
- 安装 `.deb` 声明的系统/Python依赖；
- 保留 `/usr/bin/odoo` launcher。

随后在**同一个 `RUN` 镜像层**中删除 Community Python 源码，并用本地完整 Enterprise `+e` archive 原位替换：

```text
/usr/lib/python3/dist-packages/odoo
```

因此最终运行时只有 Enterprise Odoo 源码，不需要 `/mnt/enterprise` 或第二份 `/opt/odoo-enterprise`。

## 必需文件

把下面这些文件放在同一个 Docker build context：

```text
.
├── Dockerfile
├── odoo_18.0+e.20260811.tar.gz
├── entrypoint.sh
├── odoo.conf
├── wait-for-psql.py
├── odoo18-py312.constraints
├── requirements-pypi-stable.txt
├── requirements-pypi-latest.txt
└── verify-python-stack.py
```

Enterprise archive 应类似：

```text
odoo-18.0+e.20260811/
├── odoo/
├── odoo.egg-info/
├── requirements.txt
├── setup.py
└── ...
```

Dockerfile 使用 `tar --strip-components=1` 解压。

## 推荐先计算 Enterprise SHA256

Linux/macOS：

```bash
sha256sum odoo_18.0+e.20260811.tar.gz
```

PowerShell：

```powershell
Get-FileHash .\odoo_18.0+e.20260811.tar.gz -Algorithm SHA256
```

## 构建

stable：

```bash
docker build --pull \
  --build-arg PYPI_PROFILE=stable \
  --build-arg ODOO_RELEASE=20260811 \
  --build-arg ODOO_ENTERPRISE_SHA256='<你的SHA256>' \
  -t odoo18-enterprise:20260811 .
```

latest：

```bash
docker build --pull \
  --build-arg PYPI_PROFILE=latest \
  --build-arg ODOO_RELEASE=20260811 \
  --build-arg ODOO_ENTERPRISE_SHA256='<你的SHA256>' \
  -t odoo18-enterprise:20260811-latest .
```

## 为什么不会无端保留两份 Odoo 源码

Community `.deb` 安装、Community 源码删除、Enterprise 源码复制都发生在同一个 `RUN` 中。

Enterprise tar.gz 使用：

```dockerfile
RUN --mount=type=bind,...
```

读取，因此压缩包本身也不会通过 `COPY` 成为一个永久镜像层。

## 构建时会自动检查

构建会失败，如果：

- `.deb` 的 Odoo 路径不是预期的 `/usr/lib/python3/dist-packages/odoo`；
- Enterprise archive 缺少 `odoo/__init__.py`；
- 未发现 `web_enterprise` 或 `account_accountant`；
- 最终 `import odoo` 不是从原位替换目录加载；
- WeasyPrint 70 / PyCUPS / PDF smoke test 失败。

## 注意

`dpkg` 仍认为 `odoo` 包已安装，但其 Python 源码已经被本地 Enterprise 源码替换。因此 Dockerfile 会执行：

```bash
apt-mark hold odoo
```

不要在运行中的容器执行 `apt reinstall odoo` 或升级 `odoo` 包；升级 Odoo 应重新构建镜像。
