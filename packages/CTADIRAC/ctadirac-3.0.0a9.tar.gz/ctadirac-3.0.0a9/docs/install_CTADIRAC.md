# CTA-DIRAC Installation

This document aims to provide a sequential and simple way of installing DIRAC and its components. It mainly follows the [official DIRAC documentation](https://dirac.readthedocs.io/en/integration/AdministratorGuide/ServerInstallations/InstallingDiracServer.html).

## Manual to install Dirac on a server from scratch <a name="manual_inst"></a>

- [CTA-DIRAC Installation](#cta-dirac-installation)
  - [Manual to install Dirac on a server from scratch ](#manual-to-install-dirac-on-a-server-from-scratch-)
    - [Server preparation ](#server-preparation-)
    - [DIRAC installation ](#dirac-installation-)
    - [Doing all using scripts ](#doing-all-using-scripts-)
    - [Replace DIPS protocol by HTTPS with Tornado ](#replace-dips-protocol-by-https-with-tornado-)
    - [DIRAC Configuration ](#dirac-configuration-)
    - [Dockerize DIRAC ](#dockerize-dirac-)
    - [Running DIRAC services using a Kubernetes cluster ](#running-dirac-services-using-a-kubernetes-cluster-)

### Server preparation <a name="server_prep"></a>
--------------------------------------

The following must be done in root and is for RH based OS. But it can be adapt for other distributions.

1. Create DIRAC user:

```bash
groupadd -r dirac
useradd -d /home/dirac -s /bin/bash --no-log-init -r -g dirac dirac
```

2. Create necessary directories:

```bash
export DIRAC_DIR=/path/to/dirac
mkdir -p $DIRAC_DIR
mkdir -p $DIRAC_DIR/sbin
mkdir -p $DIRAC_DIR/etc
mkdir -p $DIRAC_DIR/user
mkdir -p $DIRAC_DIR/etc/grid-security
mkdir -p /home/dirac

chown -R dirac:dirac /home/dirac
chown -R dirac:dirac $DIRAC_DIR
```

3. Install necessary packages:

```bash
# Grid certificates repo:
echo "[EGI-trustanchors]
name=EGI-trustanchors
baseurl=http://repository.egi.eu/sw/production/cas/1/current/
gpgkey=http://repository.egi.eu/sw/production/cas/1/GPG-KEY-EUGridPMA-RPM-3
gpgcheck=1
enabled=1" > /etc/yum.repos.d/EGI-trustanchors.repo

# MariaDB server: Needs EPEL repo.
yum install -y mariadb-server
# install pkgs:
yum install -y iptables-service git ca-policy-egi-core
# Install runit
curl -O https://diracproject.web.cern.ch/diracproject/rpm/runit-2.1.2-1.el7.cern.x86_64.rpm
yum install -y ./runit-2.1.2-1.el7.cern.x86_64.rpm
rm  ./runit-2.1.2-1.el7.cern.x86_64.rpm
yum clean all
```

4. Open ports:

```bash
service iptables restart
iptables -I INPUT -p tcp --dport 9130:9200 -j ACCEPT
iptables-save
systemctl restart iptables.service
```

Add the following lines for the WebApp (this is not necessary if using Nginx):

```bash
iptables -t nat -I PREROUTING -p tcp --dport 80 -j REDIRECT --to-ports 8080
iptables -t nat -I PREROUTING -p tcp --dport 443 -j REDIRECT --to-ports 8443
```

5. Create MySQL users:

```bash
# Start services:
systemctl start mariadb
systemctl status mariadb

# If first identification:
mysql -u root -e "ALTER USER 'root'@'localhost' IDENTIFIED BY '$MYSQL_ROOT_PWD'"

mysql -u root -p"$MYSQL_ROOT_PWD" -e \
"CREATE USER 'Dirac'@'%' IDENTIFIED BY '$MYSQL_DIRAC_PWD'; \
CREATE USER 'Dirac'@'localhost' IDENTIFIED BY '$MYSQL_DIRAC_PWD'; "

# if you use an external DB:
mysql -u root -p"$MYSQL_ROOT_PWD" -e \
"CREATE USER 'Dirac'@'[DB-SERVER-HOSTNAME]' IDENTIFIED BY '[PASSWORD]';"
```

If issue with socket while running mysql cmd the socket path can be  found in: `ps -aux | grep mysql` (or in `/etc/my.cnf.d/mariadb-server.cnf`) and add the following in `~/.my.cnf`: `[mysql] socket=/path/to/socket`

Then restart mysql services:
```bash
systemctl restart mariadb.service
```

6. Configure runit:

Adapt the scripts `runsvdir-start` and `runsvdir-start.service`.

```bash
cp /path/to/runsvdir-start $DIRAC_DIR/sbin/
cp /path/to/runsvdir-start.service /usr/lib/systemd/system/
chown -R dirac:dirac $DIRAC_DIR/sbin/

systemctl daemon-reload
systemctl restart runsvdir-start
systemctl enable runsvdir-start
systemctl status runsvdir-start
```

7. Manage certificates: skip this part if the host has its own host certificates.

If you need to create "fake certificate" do the following as `dirac` user:
```bash
export DIRAC_DEV=/path/to
cd $DIRAC_DEV
wget https://github.com/DIRACGrid/DIRACOS2/releases/download/latest/DIRACOS-Linux-x86_64.sh
bash DIRACOS-Linux-x86_64.sh
rm DIRACOS-Linux-x86_64.sh
git checkout release/integration
export SERVERINSTALLDIR=$DIRAC_DIR
export TESTCODE=$DIRAC_DEV
source tests/Jenkins/utilities.sh
generateCA
generateCertificates 365
generateUserCredentials 365
mkdir -p ~/.globus/
cp $DIRAC_DIR/user/*.{pem,key} ~/.globus/
mv ~/.globus/client.key ~/.globus/userkey.pem
mv ~/.globus/client.pem ~/.globus/usercert.pem
```

In kubernetes: the hostname dns used by the `utilities.sh` script is too long so we need to fix the script by taking only the short hostname.
Use EGI grid pkg, as `dirac` user:

```bash
cp hostcert.pem hostkey.pem $DIRAC_DIR/etc/grid-security
ln -s /etc/grid-security/certificates $DIRAC_DIR/etc/grid-security/certificates
```

### DIRAC installation <a name="dirac_inst"></a>
------------------------------------

1. Download the installer:

```bash
curl -O https://raw.githubusercontent.com/DIRACGrid/management/master/install_site.sh
```

Adapt the script if necessary.

2. Create your configuration file:

Can use [dirac_example.cfg](../utils/files/dirac_example.cfg) as template.
Pay attention to the X509 variables...

3. Run installation:

```bash
./install_site.sh -i /opt/dirac [-v <x.y.z>] [-e <extension>] [-p <extra-pip-install>] install.cfg
```

For CTA:

```bash
./install_site.sh -i $DIRAC_DIR -e CTADIRAC  /path/to/install_server.cfg
```

You should end with the running services list.

**Note**: It's good to set: `export MYSQL_CONNECTION_GRACE_TIME=0` in the `bashrc`.

4. Install components and dbs:

```bash
dirac-install-db <DB>
dirac-install-component <System> <Component>
```

5. Installing Web App

Follow the same procedure as for the other DIRAC services installation, except here we will specify a different configuration file where we add WebApp specific arguments. See example [web_app_example.cfg](../utils/deploy/files/web_app_example.cfg).

https://dirac.readthedocs.io/en/integration/AdministratorGuide/ServerInstallations/InstallingWebAppDIRAC.html#installing-webappdirac

* Using `Nginx`:

See: https://dirac.readthedocs.io/en/integration/AdministratorGuide/ServerInstallations/InstallingWebAppDIRAC.html#install-nginx

Pilot script issue: the pilot needs to contact the Webapp in order to download dedicated files (mainly `webRoot/resources/www/pilot/`). If `Nginx` is used you need to add the following lines in `/etc/nginx/conf.d/site.conf` to make it works:

```bash
location /pilot/ {
   autoindex on;
   root /opt/dirac/webRoot/www;
   expires 1h;
   break;
  }

  location /files/ {
   autoindex on;
   root /opt/dirac/webRoot/www;
   expires 1h;
   break;
  }

  location /defaults/ {
   autoindex on;
   root /opt/dirac/webRoot/www;
   expires 1h;
   break;
  }
  ```

If you got `502 Bad Gateway` error, run both following commands:
```bash
grep nginx /var/log/audit/audit.log | audit2allow -M nginx
semodule -i nginx.pp
```

### Doing all using scripts <a name="using_script"></a>
-------------------------------------------

You can use the script [install-ctadirac-server.sh](../utils/deploy/bin/install-ctadirac-server.sh) to do all the server preparation and the DIRAC installation in once.

### Replace DIPS protocol by HTTPS with Tornado <a name="dips_https"></a>
-----------------------------------------------

See: https://github.com/chaen/DIRAC/blob/rel-v7r3_doc_installHTTPs/docs/source/AdministratorGuide/ServerInstallations/HTTPSServices.rst#mastercs-special-case

1. Preparation

    * Install Tornado packages:
        - `tornado-m2crypto`
        -  `WebAppDIRAC` which requires `tornado`

    * Install and run DIRAC CS and services as usual

2. Install HTTPS-based services

    * Connect through a client, initialize the proxy, connect to the `dirac-configuration-cli` or using the Web App and modify the following:
        - Set Tornado:

        ```bash
        set DIRAC/Setups/<setup_name>/Tornado Production
        set Systems/Tornado/Production/Port 8444
        writeToServer
        ```
        - Modify the service:

        ```bash
        set Systems/<sys_name>/<setup_name>/Services/<service_name>/Protocol https
        set Systems/<sys_name>/<setup_name>/Services/<service_name>/HandlerPath DIRAC/<system_name>/Service/Tornado<system_name>Handler.py
        removeOption Systems/<sys_name>/<setup_name>/Services/<service_name>/Port
        set Systems/<sys_name>/<setup_name>/Services/URLs/<service_name> https://<host_name>:<tornado_port>/<system>/<service>
        ```
    * Run the following command or restart the tornado service to run the service under Tornado:

        ```bash
        dirac-install-tornado-service <System/Service>
        # Or
        runsvctlr t startup/Tornado_Tornado
        ```
        - one can check if the service if running under Tornado by reading the Tornado logs.

        - once the service is running under Tornado, one can remove it from the `runit` and `startup` directories.

3. Run the Master CS with Tornado:

    * Edit `etc/dirac.cfg` and change the `Systems/Configuration/<Setup>/Services/Server` as:

    ```bash
    Systems
    {
        Configuration
        {
            CTADIRAC-cert
            {
                Services
                {
                    Server
                    {
                        HandlerPath = DIRAC/ConfigurationSystem/Service/TornadoConfigurationHandler.py
                        Port = 9135
                    }
                }
                URLs
                {
                    Server = https://disp-vm1.zeuthen.desy.de:9135/Configuration/Server
                    Server += https://disp-vm2.zeuthen.desy.de:9135/Configuration/Server
                }
            }
        }
    }
    ```

    * Do the same change in the CS configuration.
    * Replace all `dips://server:9135/Configuration/Server` to `https://server:9135/Configuration/Server`
    * Replace `runit/Configuration/Server/run` with:

    ```bash
    #!/bin/bash
    rcfile=/opt/dirac/bashrc
    [ -e $rcfile ] && source $rcfile
    #
    export DIRAC_USE_TORNADO_IOLOOP=Yes
    exec 2>&1
    #
    [ "service" = "agent" ] && renice 20 -p $$
    #
    #
    exec tornado-start-CS -ddd
    ```
    * Restart the CS as usual.

### DIRAC Configuration <a name="dirac_conf"></a>
-----------------------------------------------

Here are the mandatory or highly recommended and non exhasutive  configuration options for a running DIRAC instance.

1. Configuration:
    - Name
    - MasterServer = name of the master CS
    - Servers = the other CS servers

2.  Setups:

Put here all the system names you will install associated with setups names you will use.

3. Systems:

Here are the definitions of all services, agents and dbs. They are automatically generated when installing the component. Except for specific cases as for HTTPS services you won't need to change it.

- SiteDirector: Install a SiteDirector agent for each site configured in the Resources section as in the example below (this is not mandatory, but it's more efficient):
  - SiteDirectorPIC
  - SiteDirectorCSCS
  - SiteDirectorFRASCATI
  - SiteDirectorDESY

To do so you need to run:
```
dirac-install-component WorkloadManagement SiteDirectorPIC -m SiteDirector
```
or via `dirac-admin-sysadmin-cli`
```
install agent WorkloadManagement SiteDirectorPIC -m SiteDirector
```

- Here is the list of NON-mandatory services:
  - Accounting_NetworkAgent: need queuing system
  - Configuration_GOCDB2CSAgent: only if using GOCDB
  - Configuration_Bdii2CSAgent
  - Configuration_VOMS2CSAgent
  - DataManagement_FTS3Agent: only if using S3
  - DataManagement_S3Gateway: only if using S3
  - Framework_TokenManager: only if using token auth
  - WorkloadManagement_PilotsLogging
  - WorkloadManagement_VirtualMachineMonitorAgent
  - WorkloadManagement_JobAgent: created by pilot jobs

- PilotSyncAgent:
    - specify: `SaveDirectory`

4. Registry:
    - Users: username, DN, email and CA
    - Groups: properties, userlist
    - Hosts: hostnames hosting services and their properties
    - VOMS: VOMS servers definition
    - VO: used VO definition

5. Operations:
Define here DataManagement, SE, Jobs, Pilots etc... technical specifications.

    - Pilot:
        - Server= prefer the WebApp server


6. WebApp:

    - StaticDirs: specify the path to pilot scripts located on the WebApp server

7. Resources:

    - Sites:
        - sites definitions
        - allow sites using `dirac-admin-allow-site SITE "COMMENT"`
        - CE and SE types and def
    - StorageElements:
    - FileCatalogs:
    - SEGroups:
    - Computing:
        - HTCondorCE/WorkingDirectory =  /opt/dirac/work/WorkloadManagement/SiteDirectorHTCondorCE (need to create by hand this directory)

8. Monitoring:

    - OpenSearch:
      - Minimal permissions on the certificates/index prefix:
        ```
        indices:data/write/update
        indices:admin/get
        indices:admin/aliases/get
        indices:admin/mappings/get
        cluster:monitor/main
        ```
      - DIRAC configuration:
        - In `dirac.cfg`
        ```
        Services
        {
            Monitoring
            {
                CTADIRAC-alma
                {
                    Databases
                    {
                        MonitoringDB
                        {
                            Host = opensearch-api
                            Port = 9200
                            SSL = False
                            IndexPrefix = index-prefix
                            CRT = True
                            ca_certs = /path/to/ca
                            client_cert = /path/to/cert
                            client_key =/path/to/cert-key
                        }
                    }
                }
            }
            WorkloadManagement
            {
                CTADIRAC-alma
                {
                    Databases
                    {
                        ElasticJobParametersDB
                        {
                            Host = opensearch-api
                            Port = 9200
                            SSL = False
                            IndexPrefix = index-prefix
                            CRT = True
                            ca_certs = /path/to/ca
                            client_cert = /path/to/cert
                            client_key =/path/to/cert-key
                        }
                    }
                }
            }
        }
        ```
        - In the general cfg:
        ```
        Services/JobMonitoring
        {
            useESForJobParametersFlag = True
        }
        Operation/<Setup>/MonitoringBackends
        {
            WMSHistory = Monitoring
            DataOperation = Monitoring
            PilotsHistory = Monitoring
            PilotSubmissionMonitoring = Monitoring
            AgentMonitoring = Monitoring
            ServiceMonitoring = Monitoring
            RMSMonitoring = Monitoring
        }
        ```

    Finally restart the services.

### Dockerize DIRAC <a name="dirac_docker"></a>
-----------------------------------------------

To be written.

### Running DIRAC services using a Kubernetes cluster <a name="dirac_kube"></a>
-----------------------------------------------

To be written.
