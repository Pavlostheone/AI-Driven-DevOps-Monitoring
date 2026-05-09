#!/bin/bash

source "$(dirname "$0")/common.sh"
source "$(dirname "$0")/config.env"

DATE=$(date '+%Y-%m-%d %H:%M:%S')

# === Function === #

# Function to check required commands
check_dependencies() {
    for cmd in awk; do
        if ! command -v "$cmd" &>/dev/null; then
            echo "$DATE - ERROR: Required command '$cmd' not found." | tee -a "$LOG_FILE"
            exit 1

        fi
    done
}

# Function to get average CPU usage across all cores
get_cpu_usage(){
    #Extract CPU usage using top command
  local usage
  usage=$(wmic cpu get loadpercentage | awk 'NR==2 {print $1}')


# Handle empty or invalid values
  if [[ -z "$usage" || "$usage" == *"e+"* ]]; then 
    echo "0"
  else
    echo "${usage%.*}" #strip decimals
  fi
}

#Function to send email alert
send_email_alert() {
    local cpu_value="$1"
    local subject="[ALERT] High CPU Usage on $HOSTNAME"
    local message="Date: $DATE
    Host: $HOSTNAME
    CPU Usage: ${cpu_value}%

    CPU usage has exceeded the defined threshold (${THRESHOLD_CPU}%).

    Please investigate running processes using:
    top, ps -eo pid,comm,pcpu --sort=-pcpu

    Regards,
    Monitoring Script"

    echo "$message" | mailx -s "$subject" "$MAIL_TO"
    echo "$DATE - EMAIL: Alert email sent to $MAIL_TO (CPU: ${cpu_value}%)" >> "$LOG_FILE"

}

# Function to send recovery email
 send_recovery_email() {
    local cpu_value="$1"
    local subject="[RECOVERY] CPU Usage Normalised on $HOSTNAME"
    local message="Date: $DATE
    Host: $HOSTNAME
    CPU Usage: ${cpu_value}%

    CPU usage has returned tyo normal levels below ${THRESHOLD_CPU}%.

    System performance stabilised.

    Regards, 
    Monitoring Script"

    echo "$message" | mailx -s "$subject" "$MAIL_TO"
    echo "$DATE - EMAIL: Recovery email sent to $MAIL_TO (CPU: ${cpu_value}%)" >> "$LOG_FILE"
}

log_message() {
    echo "$1" | tee -a "$LOG_FILE"
}

# === MAIN Logic === #
check_dependencies

CPU_USAGE=$(get_cpu_usage)
CPU_INT=${CPU_USAGE%.*}

if [[ ! "$CPU_INT" =~ ^[0-9]+$ ]]; then
    log_message "ERROR: Invalid CPU usage value '$CPU_INT'"
    exit 1
fi

if (( CPU_INT > THRESHOLD_CPU)); then
    #CPU HIGH
    if [[ ! -f "$STATE_FILE" ]]; then
        log_message "ALERT: CPU usage ${CPU_INT}% > ${THRESHOLD_CPU}%. Sending alert..."
        send_email_alert "$CPU_INT"
        echo "ALERT_SENT" > "$STATE_FILE"
    else
     log_message "ALert: CPU usage ${CPU_INT}% > ${THRESHOLD_CPU}%. Alert already sent."
    fi
else
    #CPU Normal
    if [[ -f "$STATE_FILE" ]]; then
        log_message "RECOVERY: CPU usage ${CPU_INT}% < ${THRESHOLD_CPU}%. Sending recovery email..."
        send_recovery_email "$CPU_INT"
        rm -f "$STATE_FILE"
    else
        log_message "OK: CPU usage ${CPU_INT}% within threshold (${THRESHOLD_CPU}%)"
    fi
fi