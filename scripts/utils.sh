#!/bin/bash

log_message()  {
    local logfile="$1"
    local message="$2"

   echo "$(date '+%Y-%m-%d %H:%M:%S') - $message" \
   | tee -a "$logfile"

}
