#! /bin/bash

# Define text formatting variables
GREEN='\033[0;32m'   # Green text color
RED='\033[0;31m'     # Red text color
NC='\033[0m'         # No color (reset)

# Check if dirname cmd exists
if ! command -v dirname &> /dev/null
then
        echo "dirname command could not be found"
        exit 1
else
        SCRIPT_PATH="$(dirname -- "${BASH_SOURCE[0]}")"
fi

if [[ "$SCRIPT_PATH" == "." ]]; then
        SCRIPT_PATH=$(pwd)
else
        SCRIPT_PATH="$(pwd)/$SCRIPT_PATH"
fi

PROGRAM_NAME="install-ctadirac-server"

# Default values
DIRAC_DIR="/opt/dirac"
PORT="no"
CREATE_USER="no"
CERT="no"
CONFIGURE="no"
CTADIRAC_VERSION=""
FAKE_CERT="no"
MYSQL="no"
RUNIT="no"
NGINX="no"

# Usage information
display_usage() {
    cat <<EOF
Install DIRAC servers and its dependencies.

Prerequisites:
  - MySQL or MariaDB server must be installed.
  - DIRAC services ports must be open:
  https://dirac.readthedocs.io/en/integration/AdministratorGuide/ServerInstallations/InstallingDiracServer.html#requirements

This script must be executed as root.

Usage:
  $0 [OPTIONS]

Options:
  -c, --cert        Install certificates (default: $CERT)
  --cfg             Launch dirac-configure and dirac-setup-site using the given configuration file (default: $CONFIGURE)
  -d, --dir         DIRAC install directory (default: $DIRAC_DIR)
  -f, --fake        Install fake certificates (default: $FAKE_CERT)
  -h, --help        Display this help
  -n, --nginx       Install and configure Nginx (default: $NGINX)
  -m, --mysql       Create MySQL user (default: $MYSQL)
  -r, --runit       Install runit utilities (default: $RUNIT)
  -u, --user        Create dirac user (default: $CREATE_USER)
  -v, --version     Precise CTADIRAC version

Example:
  $0 -cnmru -d /opt/dirac -v 2.2.22
EOF
}

# Function to enable individual options based on combined options
enable_combined_options() {
    local combined_options="$1"
    for opt in $(echo "$combined_options" | sed 's/./& /g'); do
        case "$opt" in
            c)
                CERT="yes"
                ;;
            f)
                FAKE_CERT="yes"
                ;;
            m)
                MYSQL="yes"
                ;;
            n)
                NGINX="yes"
                ;;
            r)
                RUNIT="yes"
                ;;
            u)
                CREATE_USER="yes"
                ;;
            *)
                echo "Unknown option: -$opt"
                display_usage
                exit 1
                ;;
        esac
    done
}

# Parse command-line options
while [[ $# -gt 0 ]]; do
    case "$1" in
        -c|--installcert)
            CERT="yes"
            shift
            ;;
        --cfg)
            shift
            CFG_FILE="$1"
            if [ -f $CFG_FILE ]; then
                CONFIGURE="yes"
            else
                echo -e "${RED}$CFG_FILE does not exists or is not a file${NC}"
                exit 1
            fi
            ;;
        -d|--dir)
            shift
            if [[ -n "$1" ]]; then
                DIRAC_DIR="$1"
            else
                echo "Error: The -d|--dir option requires a non-empty value."
                exit 1
            fi
            ;;
        -f|--fake)
            FAKE_CERT="yes"
            shift
            ;;
        -h|--help)
            display_usage
            exit 0
            ;;
        -n|--nginx)
            NGINX="yes"
            shift
            ;;
        -m|--mysql)
            MYSQL="yes"
            shift
            ;;
        -r|--runit)
            RUNIT="yes"
            shift
            ;;
        -u|--user)
            CREATE_USER="yes"
            shift
            ;;
        -v|--version)
            shift
            if [[ -n "$1" ]]; then
                CTADIRAC_VERSION="$1"
            else
                echo -e "${RED}The -v|--ctaversion option requires a non-empty value.${NC}"
                exit 1
            fi
            api_url="https://pypi.org/pypi/CTADIRAC/$CTADIRAC_VERSION/json"
            version=$(curl -s "$api_url" | jq -r .info.version)
            if [[ "$version" == "null" ]]; then
                echo -e "${RED}ERROR: Failed to find a version from $api_url${NC}"
                latest_version=$(curl -s https://pypi.org/pypi/CTADIRAC/json | jq -r .info.version)
                echo -e "Find latest CTADIRAC version: $latest_version"
                read -r -p "Use this version instead? [y/n] " use_latest
                case "$use_latest" in
                    [Yy]es|y)
                        CTADIRAC_VERSION=$latest_version
                        ;;
                    [Nn]o|n)
                        exit 1
                        ;;
                    *)
                        echo "Invalid input. Please enter 'yes' or 'no'."
                        exit 1
                        ;;
                esac
            fi
            ;;
        --)
            shift
            break
            ;;
        -*)
            # Handle combined options
            enable_combined_options "${1#-}"
            shift
            ;;
        *)
            # Handle arguments without options (if needed)
            shift
            ;;
    esac
done

PKG_MNGR="yum"
# Check for the presence of common package manager commands
if command -v yum &> /dev/null; then
    PKG_MNGR="yum"
elif command -v dnf &> /dev/null; then
    PKG_MNGR="dnf"
elif command -v apt &> /dev/null; then
    PKG_MNGR="apt"
fi

if [[ "$MYSQL" == "yes" ]]; then
        if [[  -z "$(command -v mysql)" ]]; then
                echo -e "${RED}ERROR: mysql command not found.${NC}"
                exit 1
        else
                echo -e "${GREEN}MySQL Configuration:${NC}"
                read -p "Enter MySQL root password: "$'\n' -s mysql_root_pwd
                echo ""
                read -p "Enter MySQL dirac password: "$'\n' -s mysql_dirac_pwd
                echo ""
        fi
fi

# Create dirac user
if [[ "$CREATE_USER" == "yes" ]]; then
        echo -e "${GREEN}Creating dirac user and group...${NC}"
        groupadd -r dirac
        useradd -d /home/dirac -s /bin/bash --no-log-init -r -g dirac dirac
fi

echo -e "${GREEN}Creating directories...${NC}"
mkdir -p $DIRAC_DIR
mkdir -p $DIRAC_DIR/sbin
mkdir -p $DIRAC_DIR/etc
mkdir -p $DIRAC_DIR/user
mkdir -p $DIRAC_DIR/etc/grid-security
mkdir -p /home/dirac

echo -e "${GREEN}Setting directory ownership...${NC}"
chown -R dirac:dirac /home/dirac
chown -R dirac:dirac $DIRAC_DIR
echo -e "${GREEN}Directory setup completed.${NC}"

if [[ "$CERT" == "yes" ]]; then
        yum_ca=$(yum list  ca-policy-egi-core | awk '{print $1}')
        pkg=$(echo $yum_ca | awk -F' ' '{print $NF}')
        if [[ ! "$pkg" == "ca-policy-egi-core" ]]; then
                echo -e "${GREEN}Installing EGI certificates...${NC}"
                cp $SCRIPT_PATH/../files/EGI-trustanchors.repo /etc/yum.repos.d/
                $PKG_MNGR install -y ca-policy-egi-core
                echo -e "${GREEN}Certificates installed.${NC}"
        else
                echo -e "${GREEN}ca-policy-egi-core already installed.${NC}"
        fi
fi

if [[ -d /etc/grid-security/ ]]; then
        echo -e "${GREEN}Creating grid-security symlink${NC}"
        ln -s /etc/grid-security/certificates $DIRAC_DIR/etc/grid-security/certificates
        chown dirac:dirac $DIRAC_DIR/etc/grid-security/certificates
fi

if [[ -f /etc/grid-security/hostcert.pem ]] && [[ -f /etc/grid-security/hostkey.pem ]]; then
        echo -e "${GREEN}Copying hostcert and hostkey:${NC}"
        cp /etc/grid-security/hostcert.pem $DIRAC_DIR/etc/grid-security/hostcert.pem
        cp /etc/grid-security/hostkey.pem $DIRAC_DIR/etc/grid-security/hostkey.pem
        chown dirac:dirac $DIRAC_DIR/etc/grid-security/hostkey.pem
        chown dirac:dirac $DIRAC_DIR/etc/grid-security/hostcert.pem
fi

if [[ "$FAKE_CERT" == "yes" ]]; then
        echo -e "${GREEN}Creating fake certificate:${NC}"
        export TESTCODE="$SCRIPT_PATH/../caUtilities"
        export SERVERINSTALLDIR="$DIRAC_DIR"
        source $SCRIPT_PATH/../caUtilities/utilities.sh
        generateCA
        generateCertificates 365
        generateUserCredentials 365
        chown dirac:dirac $DIRAC_DIR/etc/grid-security/host*
fi

if [[ "$RUNIT" == "yes" ]]; then
        yum_run=$(yum list  runit | awk '{print $1}')
        pkg=$(echo $yum_run | awk -F' ' '{print $NF}')
         if [[ ! "$pkg" == "runit.x86_64" ]]; then
                echo -e "${GREEN}Installing RUNIT:${NC}"
                curl -O https://diracproject.web.cern.ch/diracproject/rpm/runit-2.1.2-1.el7.cern.x86_64.rpm
                $PKG_MNGR install -y ./runit-2.1.2-1.el7.cern.x86_64.rpm
                $PKG_MNGR clean all
                rm ./runit-2.1.2-1.el7.cern.x86_64.rpm
        else
                echo "runit already installed"
        fi
fi

echo -e "${GREEN}Copying runsvdir files:${NC}"
cp  $SCRIPT_PATH/../files/runsvdir-start $DIRAC_DIR/sbin/
cp -f $SCRIPT_PATH/../files/runsvdir-start.service /usr/lib/systemd/system/runsvdir-start.service

sed -i "s|DIRAC_DIR|${DIRAC_DIR}|g" /usr/lib/systemd/system/runsvdir-start.service
sed -i "s|DIRAC_DIR|${DIRAC_DIR}|g" $DIRAC_DIR/sbin/runsvdir-start

chown -R dirac:dirac $DIRAC_DIR/sbin/
chmod -R 744 $DIRAC_DIR/sbin/

echo -e "${GREEN}Reloading runit service${NC}"
systemctl daemon-reload
systemctl restart runsvdir-start
systemctl enable runsvdir-start
systemctl status runsvdir-start

if [[ "$MYSQL" == "yes" ]]; then
        echo -e "${GREEN}Creating MySQL user${NC}"
        if [[ "$(mysql -u root -p$mysql_root_pwd -e "SELECT User, Host FROM mysql.user WHERE User='Dirac';")" != "" ]]; then
                mysql -uroot -p"$mysql_root_pwd" -e "CREATE USER 'Dirac'@'%' IDENTIFIED BY '$mysql_dirac_pwd'; \
                CREATE USER 'Dirac'@'localhost' IDENTIFIED BY '$mysql_dirac_pwd'; "
        else
                echo "MySQL Dirac user already exists."
        fi
fi

# installing nginx and conf
if [[ "$NGINX" == "yes" ]]; then
        echo -e "${GREEN}Installing NGINX:${NC}"
        yum install nginx -y
        systemctl enable nginx
        systemctl start nginx

        if ! [[ -f  /etc/nginx/ssl/dhparam.pem ]]; then
                read -p "Creating dh parameter ? (this could take a very long time) [Y/n] "$'\n' DH_PARAM
                if [[ "$DH_PARAM" == "Y" ]]; then
                        echo "This could take a long time..."
                        openssl dhparam -out /etc/nginx/ssl/dhparam.pem 4096
                fi
        fi
        echo -e "${GREEN}Creating /etc/nginx/conf.d/site.conf${NC}"
        cp $SCRIPT_PATH/../files/site.conf /etc/nginx/conf.d/site.conf
        sed -i "s|your.server.domain|$(hostname)|g" /etc/nginx/conf.d/site.conf
        if ! [[ "$DIRAC_DIR" == "/opt/dirac/" ]]; then
                sed -i "s|/opt/dirac|$DIRAC_DIR|g" /etc/nginx/conf.d/site.conf
        fi
        echo -e "${GREEN}Reloading nginx service${NC}"
        systemctl restart nginx
        systemctl status nginx
fi

if [[ "$CONFIGURE" == "yes" ]]; then
    cp $CFG_FILE $DIRAC_DIR
    CFG_FILE=$DIRAC_DIR/$(basename $CFG_FILE)
    chown dirac:dirac $CFG_FILE
fi
# Create env file while changing user:
echo -e "${GREEN}Creating environment file...${NC}"
echo "
export DIRAC_DIR=$DIRAC_DIR
export CTADIRAC_VERSION=$CTADIRAC_VERSION
export CONFIGURE=$CONFIGURE
export CFG_FILE=$CFG_FILE" > /tmp/variables.sh
chown dirac:dirac /tmp/variables.sh
chmod 764 /tmp/variables.sh

# Install DIRAC
echo -e "${GREEN}Running as dirac user${NC}"
exec su - dirac << 'EOF'
source /tmp/variables.sh
cd $DIRAC_DIR
curl -O https://raw.githubusercontent.com/DIRACGrid/management/master/install_site.sh
chmod 764 ./install_site.sh

if [[ "$CONFIGURE" != "yes" ]]; then
        sed -i '/^dirac-configure --cfg "${install_cfg}" -ddd$/s/^/#/' ./install_site.sh
        sed -i '/^dirac-setup-site -ddd$/s/^/#/' ./install_site.sh
fi

./install_site.sh -p rich -i $DIRAC_DIR -e CTADIRAC -v $CTADIRAC_VERSION $CFG_FILE

# Add MYSQL env var in bashrc
# Get the second to last line of the bashrc
file=bashrc
second_to_last_line=$(tail -n 2 "$file" | head -n 1)

# Insert your content just before the second to last line
{
    head -n -1 "$file"
    echo "# Set to 0 to not share MYSQL connections between threads"
    echo "export MYSQL_CONNECTION_GRACE_TIME=0"
    echo "$second_to_last_line"
    tail -n 1 "$file"
} > /tmp/temp_bashrc && mv /tmp/temp_bashrc "$file"

source ./bashrc

EOF
echo -e "${GREEN}Installation Finished${NC}"
