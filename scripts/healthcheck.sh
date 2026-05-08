#!/bin/bash

SERVICES=("docker" "nginx")

for service in "${SERVICES[@]}"; do
    if systemctl is-active --quiet "$service"; then
        echo "$service is running"
    else
        echo "$service is DOWN"
    fi
done
