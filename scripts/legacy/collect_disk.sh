#!/bin/bash
# LEGACY: Replaced by Prometheus which collects this metric natively.
source "$(dirname "$0")/common.sh"
source "$(dirname "$0")/config.env"

DISK_USAGE=$(powershell -Command "
\$disk = Get-CimInstance Win32_LogicalDisk -Filter \"DeviceID='C:'\"
\$used = ((\$disk.Size - \$disk.FreeSpace) / \$disk.Size) * 100
[math]::Round(\$used)
")

STATUS="OK"

if (( DISK_USAGE > THRESHOLD_DISK )); then
    STATUS="ALERT"
fi

log_message "DISK: $DATE - $STATUS: Disk usage ${DISK_USAGE}% within threshold (${THRESHOLD_DISK}%)"

echo "$DISK_USAGE"