#!/bin/bash

verbose=false

for s in peek_agent peek_worker peek_office peek_field peek_logic
do
    # Check if the service exists
    if systemctl list-unit-files | grep -q "${s}.service"
    then
        ! $verbose || echo "Service $s exists."

        # Check if the service is active
        if systemctl is-active --quiet ${s}
        then
            echo "Stopping $s"
            sudo systemctl stop ${s}.service
        else
            echo "Service $s is not active."
        fi
    else
        echo "Service $s does not exist."
    fi
done

echo "Waiting for services to stop"
sleep 5s

echo "Killing anything left running"
pkill -9 -u $USER -f python || true