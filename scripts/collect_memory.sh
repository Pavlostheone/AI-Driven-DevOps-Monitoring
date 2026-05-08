#!/bin/bash

MEMORY_USAGE=$(free | awk '/Mem:/ {
    printf("%.0f"), $3/$2 * 100}')

echo "$MEMORY_USAGE"
