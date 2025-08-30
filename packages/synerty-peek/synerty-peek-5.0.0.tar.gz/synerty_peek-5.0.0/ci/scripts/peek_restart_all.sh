#!/bin/bash

# Initialize our own variables
verbose=0

# Parse the flags using getopts
while getopts "vh" opt; do
  case ${opt} in
    v)
      verbose=1
      ;;
    h)
      echo "Usage: $0 [-v] [-h]"
      echo "Options:"
      echo " -v, Enable verbose mode"
      echo " -h, Display this help message"
      exit 0
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      exit 1
      ;;
  esac
done

# Define an array to store services that are enabled and can be restarted.
declare -a services_to_restart

for s in peek_office peek_field peek_agent peek_worker peek_logic
do
    # Check if the service exists
    if systemctl list-unit-files | grep -q "${s}.service"
    then
        [ "$verbose" -eq 1 ] && echo "Service $s exists."

        # Check if the service is active
        if systemctl is-active --quiet ${s}
        then
            echo "Stopping $s"
            sudo systemctl stop ${s}.service
        else
            [ "$verbose" -eq 1 ] && echo "Service $s is not active."
        fi

        # Check if the service is enabled
        if systemctl is-enabled --quiet ${s}
        then
            [ "$verbose" -eq 1 ] && echo "Service $s is enabled, will be restarted."
            services_to_restart=($s "${services_to_restart[@]}")
        else
            [ "$verbose" -eq 1 ] && echo "Service $s is not enabled."
        fi
    else
        [ "$verbose" -eq 1 ] && echo "Service $s does not exist."
    fi
done

[ "$verbose" -eq 1 ] && echo "Waiting for services to stop"
sleep 5s

[ "$verbose" -eq 1 ] && echo "Killing anything left running"
pkill -9 -u $USER -f python || true

# Restart the services that are enabled
for s in "${services_to_restart[@]}"
do
    echo "Starting $s"
    sudo systemctl start ${s}.service
    sleep 1s
done