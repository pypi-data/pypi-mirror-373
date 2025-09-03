# DIRAC installation Utilities

* [install-ctadirac-server.sh](bin/install-ctadirac.sh)

```bash
$ install-ctadirac-server.sh --help

Install DIRAC servers and its dependencies.

Prerequisites:
  - MySQL or MariaDB server must be installed.
  - DIRAC services ports must be open:
  https://dirac.readthedocs.io/en/integration/AdministratorGuide/ServerInstallations/InstallingDiracServer.html#requirements

This script must be executed as root.

Usage:
  ./install-ctadirac.sh [OPTIONS]

Options:
  -c, --cert        Install certificates (default: no)
  --cfg             Launch dirac-configure and dirac-setup-site using the given configuration file (default: no)
  -d, --dir         DIRAC install directory (default: /opt/dirac)
  -f, --fake        Install fake certificates (default: no)
  -h, --help        Display this help
  -n, --nginx       Install and configure Nginx (default: no)
  -m, --mysql       Create MySQL user (default: no)
  -r, --runit       Install runit utilities (default: no)
  -u, --user        Create dirac user (default: no)
  -v, --version     Precise CTADIRAC version

Example:
  ./install-ctadirac.sh -cnmru -d /opt/dirac -v 2.2.22
```
