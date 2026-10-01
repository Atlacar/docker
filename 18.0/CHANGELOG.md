# V3

- Community .deb retained only as bootstrap/environment provider.
- Community Python source removed and Enterprise +e source copied to the same dist-packages path in the same RUN layer.
- Enterprise tarball is consumed with BuildKit RUN bind mount, not COPY.
- Removed `/mnt/enterprise` runtime directory.
- Added Enterprise source verification to build smoke test.
