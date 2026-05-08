#!/bin/bash
CPU=$(./scripts/collect_cpu.sh)
MEMORY=$(./scripts/collect_memory.sh)
DISK=$(./scripts/collect_disk.sh)

echo "CPU: $CPU%"
echo "MEMORY: $MEMORY%"
echo "DISK:  $DISK%"

