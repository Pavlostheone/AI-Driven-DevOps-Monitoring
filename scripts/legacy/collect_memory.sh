#!/bin/bash
# LEGACY: Replaced by Prometheus which collects this metric natively.
source "$(dirname "$0")/common.sh"
source "$(dirname "$0")/config.env"

MEMORY_USAGE=$(powershell -Command "
\$os = Get-CimInstance Win32_OperatingSystem
\$used = ((\$os.TotalVisibleMemorySize - \$os.FreePhysicalMemory) / \$os.TotalVisibleMemorySize) * 100
[math]::Round(\$used)
")

STATUS="OK"

if (( MEMORY_USAGE > THRESHOLD_MEMORY )); then
    STATUS="ALERT"
fi

log_message "MEMORY: $DATE - $STATUS: Memory usage ${MEMORY_USAGE}% within threshold (${THRESHOLD_MEMORY}%)"

echo "$MEMORY_USAGE"