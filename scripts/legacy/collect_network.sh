#!/bin/bash
# LEGACY: Replaced by Prometheus which collects this metric natively.
source "$(dirname "$0")/config.env"

PING_RESULT=$(ping -c 2 google.com | tail -1)

echo "$PING_RESULT"
