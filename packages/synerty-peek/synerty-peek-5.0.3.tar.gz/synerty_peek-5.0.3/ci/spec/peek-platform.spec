Name:           peek-platform
Version:        SED_PACKAGE_BRANCH
Release:        SED_PACKAGE_VERSION%{?dist}
Summary:        Peek platform complete installation package

License:        Proprietary
BuildArch:      x86_64
Requires:       peek-env, peek-python
AutoReq:        no
Provides:       SED_PEEK_SOFTWARE_HOME/peek-platform/venv/bin/python

AutoReqProv: no
%global debug_package %{nil}
%global _enable_debug_packages 0
%global _include_minidebuginfo 0
%global _build_id_links none
%global __os_install_post %{nil}
%global __check_files %{nil}

# Additional performance optimizations
%global _source_filedigest_algorithm 0
%global _binary_filedigest_algorithm 0
%global _missing_build_ids_terminate_build 0
%global __spec_install_post %{nil}
%undefine __brp_mangle_shebangs
%undefine __brp_strip
%undefine __brp_strip_comment_note
%undefine __brp_strip_static_archive
%undefine __brp_python_bytecompile
%undefine __brp_python_hardlink

%description
Complete Peek platform installation package including all community plugins,
enterprise plugins (if available), and web applications. Provides a modular
installation with separate directories for virtual environment, utility scripts,
and Node.js components. Includes systemd service files for peek_logic, peek_worker,
peek_office, peek_field, and peek_agent services. Services are installed but left
disabled and stopped by default for manual configuration and startup.

The package creates a modular directory structure at SED_PEEK_SOFTWARE_HOME/peek-platform:
- venv/     - Python virtual environment with all Peek platform components
- scripts/  - Utility scripts for service management
- nodejs/   - Node.js installation for web applications

This replaces the previous installation method that used /home/peek/synerty-peek-<version>
directory structure and provides better separation of concerns.

This package leverages the following technologies / projects:
* Python virtual environment - https://virtualenv.pypa.io/
* Node.js applications - https://nodejs.org/
* systemd service management - https://systemd.io/

%install
set -o errexit
if [ "$PEEK_PKG_CI_TESTS" == "true" ]
then
    set -x
fi

# Run npm install steps that were moved from build phase
export SITE_PACKAGES="$(echo SED_PEEK_SOFTWARE_HOME/peek-platform/venv/lib/python*/site-packages)"
export PATH="SED_PEEK_SOFTWARE_HOME/peek-platform/nodejs/bin:$PATH"

# Install field app node_modules
echo "Installing field app node_modules..."
cd ${SITE_PACKAGES}/peek_field_app
npm install &

# Install office app node_modules
echo "Installing office app node_modules..."
cd ${SITE_PACKAGES}/peek_office_app
npm install &

# Install admin app node_modules
echo "Installing admin app node_modules..."
cd ${SITE_PACKAGES}/peek_admin_app
npm install &

# Install EDNAR node_modules
echo "Installing EDNAR app node_modules..."
cd ${SITE_PACKAGES}/peek_plugin_zepben_ednar_dms_diagram/_private/ednar-app
npm install &

# Wait for background npm installs to complete
time wait

mkdir -p %{buildroot}SED_PEEK_SOFTWARE_HOME

# Assert that the Peek installation directory exists at the known location
test -d "SED_PEEK_SOFTWARE_HOME/peek-platform"

time rsync -a --hard-links SED_PEEK_SOFTWARE_HOME/peek-platform/ %{buildroot}SED_PEEK_SOFTWARE_HOME/peek-platform/

# Assert that required directories were copied
test -d "%{buildroot}SED_PEEK_SOFTWARE_HOME/peek-platform/venv"
test -d "%{buildroot}SED_PEEK_SOFTWARE_HOME/peek-platform/scripts"
test -d "%{buildroot}SED_PEEK_SOFTWARE_HOME/peek-platform/nodejs"
test -d "%{buildroot}SED_PEEK_SOFTWARE_HOME/peek-platform/venv/bin"
test -d "%{buildroot}SED_PEEK_SOFTWARE_HOME/peek-platform/venv/lib"
test -d "%{buildroot}SED_PEEK_SOFTWARE_HOME/peek-platform/share/pkg-scripts"
test -d "%{buildroot}SED_PEEK_SOFTWARE_HOME/peek-platform/share/admin"
test -d "%{buildroot}SED_PEEK_SOFTWARE_HOME/peek-platform/share/service"
test -d "%{buildroot}SED_PEEK_SOFTWARE_HOME/peek-platform/share/admin"
test -d "%{buildroot}SED_PEEK_SOFTWARE_HOME/peek-platform/share/sudoers.d"

# Assert that core Peek executables exist
test -f "%{buildroot}SED_PEEK_SOFTWARE_HOME/peek-platform/venv/bin/python"
test -f "%{buildroot}SED_PEEK_SOFTWARE_HOME/peek-platform/venv/bin/pip"
test -f "%{buildroot}SED_PEEK_SOFTWARE_HOME/peek-platform/nodejs/bin/node"
test -f "%{buildroot}SED_PEEK_SOFTWARE_HOME/peek-platform/nodejs/bin/npm"

# Assert that utility scripts exist
test -f "%{buildroot}SED_PEEK_SOFTWARE_HOME/peek-platform/scripts/peek_stop_all.sh"
test -f "%{buildroot}SED_PEEK_SOFTWARE_HOME/peek-platform/scripts/peek_restart_all.sh"

# Add systemd service files from share directory
mkdir -p %{buildroot}/usr/lib/systemd/system
cp %{_sourcedir}/service/*.service %{buildroot}/usr/lib/systemd/system/

# Add sudoers file from share directory
mkdir -p %{buildroot}/etc
cp -av %{_sourcedir}/sudoers.d %{buildroot}/etc/

%files
SED_PEEK_SOFTWARE_HOME/peek-platform
/usr/lib/systemd/system/peek_logic.service
/usr/lib/systemd/system/peek_worker.service
/usr/lib/systemd/system/peek_office.service
/usr/lib/systemd/system/peek_field.service
/usr/lib/systemd/system/peek_agent.service
%attr(440,root,root) /etc/sudoers.d/peek-platform

%pre
set -o errexit
if [ "$PEEK_PKG_CI_TESTS" == "true" ]
then
    set -x
fi

# Ensure peek user exists (should be created by peek-env package)
if ! id peek >/dev/null 2>&1; then
    echo "ERROR: peek user does not exist. Install peek-env package first."
    exit 1
fi

%post
set -o errexit
if [ "$PEEK_PKG_CI_TESTS" == "true" ]
then
    set -x
fi

# Ensure peek-env and peek-python are installed
if [ ! -d "SED_PEEK_SOFTWARE_HOME/env" ]
then
    echo "Error: peek-env package is not installed!"
    echo "Please install peek-env first."
    exit 1
fi

if [ ! -d "SED_PEEK_SOFTWARE_HOME/python" ]
then
    echo "Error: peek-python package is not installed!"
    echo "Please install peek-python first."
    exit 1
fi

# Set executable permissions on scripts before execution
chmod +x SED_PEEK_SOFTWARE_HOME/peek-platform/share/pkg-scripts/*.sh

# Set sudoers permissions
chmod 440 /etc/sudoers.d/peek-platform
chown root:root /etc/sudoers.d/peek-platform

# Create the profile.d scripts for peek-env integration
test -d SED_PEEK_PROFILE_D

# Copy profile files from share directory to final location
cp -a SED_PEEK_SOFTWARE_HOME/peek-platform/share/profile.d/* SED_PEEK_PROFILE_D/

# Set permissions on profile files
chmod 644 SED_PEEK_PROFILE_D/901-peek-platform*.sh

# Delete this
rm -rf SED_PEEK_SOFTWARE_HOME/peek-platform/share/profile.d

# Create required Peek directories
mkdir -p SED_PEEK_DATA_HOME
mkdir -p SED_PEEK_CONFIG_HOME
mkdir -p SED_PEEK_LOG_HOME
mkdir -p SED_PEEK_RUN_HOME
mkdir -p SED_PEEK_TMP_HOME
mkdir -p SED_PEEK_SERVICE_CONFIG_HOME
mkdir -p SED_PEEK_SERVICE_LOG_DIR

# Check for PGHOST in profile.d files and add to service files if found
PGHOST_VALUE=$( \
    grep -h "export PGHOST" SED_PEEK_HOME/etc/profile.d/* 2>/dev/null |
    head -1 |
    cut -d'=' -f2 |
    tr -d '"' \
    || true \
)
if [ -n "$PGHOST_VALUE" ]
then
    echo "Found PGHOST=$PGHOST_VALUE, adding to peek_logic and peek_worker service files"
    sed -i \
        '/Environment="LD_LIBRARY_PATH=/a Environment="PGHOST='$PGHOST_VALUE'"'\
        /usr/lib/systemd/system/peek_logic.service \
        /usr/lib/systemd/system/peek_worker.service
fi

# Set ownership for Peek directories
chown -R peek:peek SED_PEEK_DATA_HOME
chown -R peek:peek SED_PEEK_CONFIG_HOME  
chown -R peek:peek SED_PEEK_LOG_HOME
chown -R peek:peek SED_PEEK_RUN_HOME
chown -R peek:peek SED_PEEK_TMP_HOME
chown -R peek:peek SED_PEEK_SOFTWARE_HOME/peek-platform


# Set proper permissions
chmod 755 SED_PEEK_DATA_HOME
chmod 755 SED_PEEK_CONFIG_HOME
chmod 755 SED_PEEK_LOG_HOME
chmod 755 SED_PEEK_RUN_HOME
chmod 755 SED_PEEK_TMP_HOME

# Create symlink for peek src
export SITE_PACKAGES="$(echo SED_PEEK_SOFTWARE_HOME/peek-platform/venv/lib/python*/site-packages)"
mkdir -p $(dirname "SED_PEEK_SRC_SYMLINK")
ln -sf ${SITE_PACKAGES} "SED_PEEK_SRC_SYMLINK"


# Set executable permissions on scripts
chmod +x SED_PEEK_SOFTWARE_HOME/peek-platform/scripts/*.sh

# Run verification script
if [ "$PEEK_PKG_CI_TESTS" == "true" ]
then
    SED_PEEK_SOFTWARE_HOME/peek-platform/share/pkg-scripts/verify-installation.sh || exit -1
else
    if ! SED_PEEK_SOFTWARE_HOME/peek-platform/share/pkg-scripts/verify-installation.sh > /dev/null 2>&1
    then
        SED_PEEK_SOFTWARE_HOME/peek-platform/share/pkg-scripts/verify-installation.sh
        exit -1
    fi
fi

# Reload systemd but do not enable or start services
if [ "$PEEK_PKG_CI_TESTS" != "true" ]
then
    systemctl daemon-reload
    echo "Services installed but not enabled. Use 'systemctl enable <service>' to enable."
    echo "Available services: peek_logic, peek_worker, peek_office, peek_field, peek_agent"
fi

%preun
set -o errexit

# Stop all Peek services if they are running
for service in peek_logic peek_worker peek_office peek_field peek_agent; do
    systemctl stop $service || true
    systemctl disable $service || true
done

# Remove profile.d integration
rm -f SED_PEEK_PROFILE_D/901-peek-platform*.sh

%postun
set -o errexit

# Remove systemd service files
rm -f /usr/lib/systemd/system/peek_logic.service
rm -f /usr/lib/systemd/system/peek_worker.service
rm -f /usr/lib/systemd/system/peek_office.service
rm -f /usr/lib/systemd/system/peek_field.service
rm -f /usr/lib/systemd/system/peek_agent.service

# Remove sudoers file
rm -f /etc/sudoers.d/peek-platform

systemctl daemon-reload

# Remove the entire SED_PEEK_SOFTWARE_HOME/peek-platform directory
rm -rf SED_PEEK_SOFTWARE_HOME/peek-platform

%changelog
* SED_PACKAGE_DATE Synerty Gitlab CI <support@synerty.com> - SED_PACKAGE_BRANCH-SED_PACKAGE_VERSION
- Automated build of Peek platform complete installation package with modular directory structure
- Virtual environment: SED_PEEK_SOFTWARE_HOME/peek-platform/venv
- Utility scripts: SED_PEEK_SOFTWARE_HOME/peek-platform/scripts  
- Node.js installation: SED_PEEK_SOFTWARE_HOME/peek-platform/nodejs
- Separate profile.d integration for each component