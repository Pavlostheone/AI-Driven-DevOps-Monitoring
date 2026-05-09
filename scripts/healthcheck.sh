#!/bin/bash

source "$(dirname "$0")/config.env"

DATE=$(date '+%Y-%m-%d %H:%M:%S')

 # === Function === #

log_message() {
    echo "$DATE - $1" | tee -a "$LOG_FILE"
}

SERVICES=("docker" "nginx")

# === MAIN === #

for service in "${SERVICES[@]}"; do
    if systemctl is-active --quiet "$service"; then
        echo "$service is running"
        STATUS="Okay"
    else
        echo "$service is DOWN"
        STATUS="Not Okay"
    fi
log_message "SERVICES: $service - STATUS: $STATUS"

done
