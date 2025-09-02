#!/bin/bash
# Script to verify the Peek platform installation

set -o errexit
if [ "$PEEK_PKG_CI_TESTS" == "true" ]
then
    set -x
fi

# Output header
echo "==== Peek Platform Installation Verification ===="
echo

# Check Peek installation directory structure
echo "Checking Peek installation directory structure..."
if [ -d SED_PEEK_SOFTWARE_HOME/peek-platform ]
then
    echo "✓ Peek installation directory exists"
    ls -la SED_PEEK_SOFTWARE_HOME/peek-platform/
else
    echo "✗ Peek installation directory missing"
fi

# Check virtual environment
echo
echo "Checking Peek virtual environment..."
if [ -d SED_PEEK_SOFTWARE_HOME/peek-platform/venv ]
then
    echo "✓ Peek virtual environment directory exists"
    ls -la SED_PEEK_SOFTWARE_HOME/peek-platform/venv/
else
    echo "✗ Peek virtual environment directory missing"
fi

if [ -f SED_PEEK_SOFTWARE_HOME/peek-platform/venv/bin/python ]
then
    echo "✓ Python executable exists in virtual environment"
    su - peek -c "python --version"
else
    echo "✗ Python executable missing in virtual environment"
fi

if [ -f SED_PEEK_SOFTWARE_HOME/peek-platform/venv/bin/pip ]
then
    echo "✓ Pip executable exists in virtual environment"
    su - peek -c "pip --version"
else
    echo "✗ Pip executable missing in virtual environment"
fi

# Check scripts directory
echo
echo "Checking Peek scripts directory..."
if [ -d SED_PEEK_SOFTWARE_HOME/peek-platform/scripts ]
then
    echo "✓ Peek scripts directory exists"
    ls -la SED_PEEK_SOFTWARE_HOME/peek-platform/scripts/
else
    echo "✗ Peek scripts directory missing"
fi

# Check nodejs directory
echo
echo "Checking Peek nodejs directory..."
if [ -d SED_PEEK_SOFTWARE_HOME/peek-platform/nodejs ]
then
    echo "✓ Peek nodejs directory exists"
    ls -la SED_PEEK_SOFTWARE_HOME/peek-platform/nodejs/
else
    echo "✗ Peek nodejs directory missing"
fi

if [ -f SED_PEEK_SOFTWARE_HOME/peek-platform/nodejs/bin/node ]
then
    echo "✓ Node.js executable exists"
    su - peek -c "node --version"
else
    echo "✗ Node.js executable missing"
fi

if [ -f SED_PEEK_SOFTWARE_HOME/peek-platform/nodejs/bin/npm ]
then
    echo "✓ npm executable exists"
    su - peek -c "npm --version"
else
    echo "✗ npm executable missing"
fi

# Check Peek platform modules
echo
echo "Checking Peek platform modules..."
if su - peek -c "python -c \"import peek_platform; print('Peek platform version:', peek_platform.__version__)\"" 2>/dev/null;
then
    echo "✓ Peek platform module is installed and importable"
else
    echo "✗ Peek platform module is not installed or not importable"
fi

# Check individual Peek services
echo
echo "Checking Peek service modules..."
PEEK_SERVICES="peek_logic_service peek_worker_service peek_office_service peek_field_service peek_agent_service"
for service in $PEEK_SERVICES;
do
    if su - peek -c "python -c \"import $service\"" >/dev/null 2>&1;
    then
        echo "✓ $service module is available"
    else
        echo "✗ $service module is not available"
    fi
done

# Check Peek directories
echo
echo "Checking Peek directories..."
PEEK_DIRS="SED_PEEK_DATA_HOME SED_PEEK_CONFIG_HOME SED_PEEK_LOG_HOME SED_PEEK_RUN_HOME SED_PEEK_TMP_HOME"
for dir in $PEEK_DIRS;
do
    if [ -d "$dir" ];
    then
        echo "✓ Directory $dir exists"
        ls -ld "$dir"
    else
        echo "✗ Directory $dir missing"
    fi
done

# Check systemd service files
echo
echo "Checking systemd service files..."
PEEK_SERVICES="peek_logic peek_worker peek_office peek_field peek_agent"
for service in $PEEK_SERVICES;
do
    if [ -f "/usr/lib/systemd/system/${service}.service" ];
    then
        echo "✓ ${service}.service file exists"
    else
        echo "✗ ${service}.service file missing"
    fi
done

# Check utility scripts
echo
echo "Checking utility scripts..."
UTIL_SCRIPTS="peek_stop_all.sh peek_restart_all.sh"
for script in $UTIL_SCRIPTS;
do
    if [ -f "SED_PEEK_SOFTWARE_HOME/peek-platform/scripts/$script" ];
    then
        echo "✓ $script exists in scripts directory"
    else
        echo "✗ $script missing from scripts directory"
    fi
done

# Check admin directory
echo
echo "Checking admin directory..."
if [ -d SED_PEEK_SOFTWARE_HOME/peek-platform/share/admin ]
then
    echo "✓ Admin directory exists"
    ls -la SED_PEEK_SOFTWARE_HOME/peek-platform/share/admin/
else
    echo "✗ Admin directory missing"
fi

# Check admin scripts
ADMIN_SCRIPTS="dump_config_only.sh p_gen_self_signed_certificates.py p_gen_self_signed_certificates.sh update_app_server.sql"
for script in $ADMIN_SCRIPTS;
do
    if [ -f "SED_PEEK_SOFTWARE_HOME/peek-platform/share/admin/$script" ];
    then
        echo "✓ $script exists in admin directory"
    else
        echo "✗ $script missing from admin directory"
    fi
done

# Check environment integration
echo
echo "Checking environment integration..."
if [ -f SED_PEEK_PROFILE_D/901-peek-platform.sh ]
then
    echo "✓ Main peek platform environment file exists"
else
    echo "✗ Main peek platform environment file is missing"
fi

# Check file ownership
echo
echo "Checking file ownership..."
if [ "$(stat -c %U SED_PEEK_SOFTWARE_HOME/peek-platform 2>/dev/null)" = "peek" ]
then
    echo "✓ Peek installation directory owned by peek user"
else
    echo "✗ Peek installation directory not owned by peek user"
fi

# Check that Peek tools are available to peek user (if peek user exists)
if id peek > /dev/null 2>&1
then
    echo
    echo "Testing Peek platform in peek user environment..."

    # Test that Python virtual environment is accessible
    if su - peek -c "python --version" > /dev/null 2>&1
    then
        echo "✓ Peek Python is accessible to peek user"
    else
        echo "✗ Peek Python is not accessible to peek user"
    fi

    # Test that Peek platform can be imported
    if su - peek -c "python -c 'import peek_platform'" > /dev/null 2>&1
    then
        echo "✓ Peek platform is importable by peek user"
    else
        echo "✗ Peek platform is not importable by peek user"
    fi

    # Test utility scripts
    if su - peek -c "test -x SED_PEEK_SOFTWARE_HOME/peek-platform/scripts/peek_stop_all.sh" 2>/dev/null
    then
        echo "✓ Utility scripts are executable by peek user"
    else
        echo "✗ Utility scripts are not executable by peek user"
    fi

    # Test Node.js access
    if su - peek -c "node --version" > /dev/null 2>&1
    then
        echo "✓ Node.js is accessible to peek user"
    else
        echo "✗ Node.js is not accessible to peek user"
    fi

    # Test npm access
    if su - peek -c "npm --version" > /dev/null 2>&1
    then
        echo "✓ npm is accessible to peek user"
    else
        echo "✗ npm is not accessible to peek user"
    fi

    # Test that environment aliases work
    if su - peek -c "type p_stop_" >/dev/null 2>&1
    then
        echo "✓ Environment aliases work for peek user"
    else
        echo "✗ Environment aliases not working for peek user"
    fi
else
    echo
    echo "✗ Peek user not found - cannot test user access"
fi

# Test Node.js applications
echo
echo "Checking Node.js applications..."
SITE_PACKAGES=$(echo SED_PEEK_SOFTWARE_HOME/peek-platform/venv/lib/python*/site-packages)
NODE_APPS="peek_field_app peek_office_app peek_admin_app"
for app in $NODE_APPS;
do
    if [ -d "${SITE_PACKAGES}/${app}/node_modules" ];
    then
        echo "✓ ${app} node_modules directory exists"
    else
        echo "✗ ${app} node_modules directory missing"
    fi
done

# Test modular directory structure
echo
echo "Verifying modular directory structure..."
echo "Virtual environment: SED_PEEK_SOFTWARE_HOME/peek-platform/venv"
echo "Utility scripts: SED_PEEK_SOFTWARE_HOME/peek-platform/scripts"
echo "Node.js installation: SED_PEEK_SOFTWARE_HOME/peek-platform/nodejs"

echo
echo "==== Verification Complete ===="