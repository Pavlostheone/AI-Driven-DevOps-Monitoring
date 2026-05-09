#!/bin/bash
# LEGACY: Replaced by Prometheus which collects this metric natively.

source "$(dirname "$0")/config.env"

ps -eo pid,comm,%cpu,%mem --sort=-%cpu | head
