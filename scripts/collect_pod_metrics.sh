#!/bin/bash

source "$(dirname "$0")/common.sh"
source "$(dirname "$0")/config.env"

NOT_RUNNING=$(kubectl get pods -A --no-headers 2>/dev/null | grep -Ev "Running|Completed" | wc -l)

STATUS="OK"

if (( NOT_RUNNING > 0 )); then
    STATUS="ALERT"
fi

log_message "PODS: $DATE - $STATUS: ${NOT_RUNNING} pod(s) not in Running/Completed state"

echo "$NOT_RUNNING"