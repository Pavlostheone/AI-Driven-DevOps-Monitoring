#!/bin/bash

log_message() {
    echo "$1" | tee -a "$LOG_FILE"
}