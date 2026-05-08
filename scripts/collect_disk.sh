#!/bin/bash

DISK_USAGE=$(df / | awk 'NR==2 {
    gsub("%","")
    print $5
}')

echo "$DISK_USAGE"
